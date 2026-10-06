from collections import Counter
from datetime import datetime
from enum import Enum
from typing import Literal
from xmlrpc.client import Fault, ProtocolError, ServerProxy

from pydantic import BaseModel

from ..config import SupervisorConvenienceConfiguration

__all__ = ("ProcessInfo", "ProcessLogChunk", "ProcessState", "SupervisorMethodResult", "SupervisorRemoteXMLRPCClient", "SupervisorState")


class ProcessState(Enum):
    STOPPED = 0
    STARTING = 10
    RUNNING = 20
    BACKOFF = 30
    STOPPING = 40
    EXITED = 100
    FATAL = 200
    UNKNOWN = 1000

    @classmethod
    def _missing_(cls, code):
        if isinstance(code, str):
            return getattr(cls, code)
        if code not in (0, 10, 20, 30, 40, 100, 200):
            return super().__init__(1000)
        raise ValueError(code)


class SupervisorState(Enum):
    FATAL = 2
    RUNNING = 1
    RESTARTING = 0
    SHUTDOWN = -1

    @classmethod
    def _missing_(cls, code):
        if isinstance(code, str):
            return getattr(cls, code)
        raise ValueError(code)


class SupervisorMethodResult(Enum):
    # duplicated from https://github.com/Supervisor/supervisor/blob/29eeb9dd55c55da2e83c5497d01f3a859998ecf9/supervisor/xmlrpc.py
    UNKNOWN_METHOD = 1
    INCORRECT_PARAMETERS = 2
    BAD_ARGUMENTS = 3
    SIGNATURE_UNSUPPORTED = 4
    SHUTDOWN_STATE = 6
    BAD_NAME = 10
    BAD_SIGNAL = 11
    NO_FILE = 20
    NOT_EXECUTABLE = 21
    FAILED = 30
    ABNORMAL_TERMINATION = 40
    SPAWN_ERROR = 50
    ALREADY_STARTED = 60
    NOT_RUNNING = 70
    SUCCESS = 80
    ALREADY_ADDED = 90
    STILL_RUNNING = 91
    CANT_REREAD = 92


class ProcessInfo(BaseModel):
    name: str
    group: str
    state: ProcessState
    description: str
    start: datetime
    stop: datetime
    now: datetime
    spawnerr: str = ""
    exitstatus: int
    logfile: str
    stdout_logfile: str
    stderr_logfile: str
    pid: int

    def running(self):
        return self.state in (ProcessState.RUNNING, ProcessState.STOPPING)

    def stopped(self):
        return self.state in (ProcessState.STOPPED, ProcessState.EXITED, ProcessState.FATAL)

    def done(self, ok_exitstatuses=None):
        ok_exitstatuses = ok_exitstatuses or (0,)
        return (self.state == ProcessState.STOPPED and self.start.timestamp() > 0) or (
            self.state == ProcessState.EXITED and self.exitstatus in ok_exitstatuses
        )

    def ok(self, ok_exitstatuses=None):
        ok_exitstatuses = ok_exitstatuses or (0,)
        return (
            self.state
            in (
                # ProcessState.STARTING,
                ProcessState.RUNNING,
                ProcessState.STOPPING,
            )
            or (self.state == ProcessState.STOPPED and self.start.timestamp() > 0)
            or (self.state == ProcessState.EXITED and self.exitstatus in ok_exitstatuses)
        )

    def bad(self, ok_exitstatuses=None):
        ok_exitstatuses = ok_exitstatuses or (0,)
        return self.state in (ProcessState.FATAL, ProcessState.UNKNOWN) or (
            self.state == ProcessState.EXITED and self.exitstatus not in ok_exitstatuses
        )


class ProcessLogChunk(BaseModel):
    text: str
    offset: int
    truncated: bool = False


class SupervisorRemoteXMLRPCClient:
    """A light wrapper over the supervisor xmlrpc api: http://supervisord.org/api.html"""

    def __init__(self, cfg: SupervisorConvenienceConfiguration):
        self._cfg = cfg
        self._host = cfg.host
        self._port = int(cfg.port.split(":")[-1])
        self._protocol = cfg.protocol
        self._rpcpath = "/" + cfg.rpcpath if not cfg.rpcpath.startswith("/") else cfg.rpcpath
        self._rpcurl = self._build_rpcurl(username=cfg.username, password=cfg.password)
        self._client = ServerProxy(self._rpcurl)

    def _build_rpcurl(self, username: str | None, password: str | None) -> str:
        # Forces http or https based on port, otherwise resolves to given protocol
        protocol = {80: "http", 443: "https"}.get(self._port, self._protocol)
        port = "" if self._port in {80, 443} else f":{self._port}"
        authentication = f"{username}:{password.get_secret_value()}@" if username and password else ""
        return f"{protocol}://{authentication}{self._host}{port}{self._rpcpath}"

    #######################
    # supervisord methods #
    #######################
    def getAllProcessInfo(self) -> list[ProcessInfo]:
        return [ProcessInfo(**_) for _ in self._client.supervisor.getAllProcessInfo()]

    def _program_groups(self) -> dict[str, tuple[int, int]]:
        groups = {
            name: (program.numprocs or 1, program.priority if program.priority is not None else 999)
            for name, program in {**self._cfg.program, **(self._cfg.fcgiprogram or {})}.items()
        }
        for name, group in (self._cfg.group or {}).items():
            groups[name] = (sum(groups.pop(program)[0] for program in group.programs), group.priority if group.priority is not None else 999)
        return groups

    def getProgramProcessInfo(self) -> list[ProcessInfo]:
        """Return configured workloads, excluding event listeners."""
        groups = self._program_groups()
        processes = [info for info in self.getAllProcessInfo() if info.group in groups]
        counts = Counter(info.group for info in processes)
        missing = {name for name, (expected, _) in groups.items() if counts[name] < expected}
        if missing:
            raise RuntimeError(f"Supervisor is missing configured processes in program groups: {', '.join(sorted(missing))}")
        return processes

    def _validate_program(self, name: str):
        if name not in self._cfg.program and name.split(":", 1)[0] not in self._program_groups():
            raise RuntimeError(f"Unknown process: {name}")

    def getState(self) -> SupervisorState:
        return SupervisorState(self._client.supervisor.getState()["statecode"])

    # def readLog(self):
    #     return self._client.supervisor.readLog(0, 0)

    def restart(self) -> SupervisorState:
        self._client.supervisor.restart()
        return self.getState()

    def shutdown(self) -> SupervisorState:
        self._client.supervisor.shutdown()
        return self.getState()

    ###################
    # process methods #
    ###################
    def getProcessInfo(self, name: str) -> ProcessInfo:
        self._validate_program(name)
        return self._getProcessInfoInternal(name)

    def _getProcessInfoInternal(self, name: str) -> ProcessInfo:
        return ProcessInfo(**self._client.supervisor.getProcessInfo(name))

    def readProcessLog(self, name: str):
        self._validate_program(name)
        return self._client.supervisor.readProcessLog(name, 0, 0)

    def readProcessStderrLog(self, name: str, offset: int = 0, length: int = 0):
        self._validate_program(name)

        return self._client.supervisor.readProcessStderrLog(name, offset, length)

    def readProcessStdoutLog(self, name: str, offset: int = 0, length: int = 0):
        self._validate_program(name)
        return self._client.supervisor.readProcessStdoutLog(name, offset, length)

    def readProcessLogChunk(self, name: str, channel: Literal["stdout", "stderr"], offset: int = 0, length: int = 65536) -> ProcessLogChunk:
        """Read new UTF-8 text, advancing a byte cursor without replaying a tail window."""
        self._validate_program(name)
        if channel not in ("stdout", "stderr") or offset < 0 or length <= 0:
            raise ValueError("channel must be stdout/stderr, offset nonnegative, and length positive")
        size = self.getProcessLogSize(name, channel)
        truncated = size < offset
        offset = 0 if truncated else offset
        available = min(length, size - offset)
        if available <= 0:
            return ProcessLogChunk(text="", offset=offset, truncated=truncated)
        read = getattr(self._client.supervisor, f"readProcess{channel.title()}Log")
        for extra in range(4):
            read_length = min(available + extra, size - offset)
            try:
                text = read(name, offset, read_length)
                break
            except Fault as error:
                if "UnicodeDecodeError" not in error.faultString or extra == 3:
                    raise
            except ProtocolError as error:
                # Supervisor can report split UTF-8 as HTTP 500 instead of an XML-RPC fault.
                if error.errcode != 500 or extra == 3:
                    raise
        return ProcessLogChunk(text=text, offset=offset + read_length, truncated=truncated)

    def getProcessLogSize(self, name: str, channel: Literal["stdout", "stderr"]) -> int:
        self._validate_program(name)
        if channel not in ("stdout", "stderr"):
            raise ValueError("channel must be stdout or stderr")
        _, size, _ = getattr(self._client.supervisor, f"tailProcess{channel.title()}Log")(name, 0, 0)
        return size

    def startAllProcesses(self) -> dict[str, ProcessInfo]:
        self.getProgramProcessInfo()
        groups = self._program_groups()
        for name in sorted(groups, key=lambda name: groups[name][1]):
            self._client.supervisor.startProcessGroup(name)
        return {info.name if info.group == info.name else f"{info.group}:{info.name}": info for info in self.getProgramProcessInfo()}

    def startProcess(self, name: str) -> ProcessInfo:
        self._validate_program(name)
        try:
            if self._client.supervisor.startProcess(name):
                return self.getProcessInfo(name)
        except Fault as f:
            if f.faultCode == SupervisorMethodResult.ALREADY_STARTED.value:
                return self.getProcessInfo(name)
            if f.faultCode in (SupervisorMethodResult.SPAWN_ERROR.value, SupervisorMethodResult.ABNORMAL_TERMINATION.value):
                return self.getProcessInfo(name)
            raise
        return self.getProcessInfo(name)

    def stopAllProcesses(self) -> dict[str, ProcessInfo]:
        self.getProgramProcessInfo()
        groups = self._program_groups()
        for name in sorted(groups, key=lambda name: groups[name][1], reverse=True):
            self._client.supervisor.stopProcessGroup(name)
        return {info.name if info.group == info.name else f"{info.group}:{info.name}": info for info in self.getProgramProcessInfo()}

    def stopProcess(self, name: str) -> ProcessInfo:
        self._validate_program(name)
        return self._stopProcessInternal(name)

    def _stopProcessInternal(self, name: str) -> ProcessInfo:
        try:
            if self._client.supervisor.stopProcess(name):
                return self._getProcessInfoInternal(name)
        except Fault as f:
            if f.faultCode == SupervisorMethodResult.NOT_RUNNING.value:
                return self._getProcessInfoInternal(name)
            raise
        return self._getProcessInfoInternal(name)

    def reloadConfig(self, start_new: bool = False) -> SupervisorState:
        added, changed, removed = self._client.supervisor.reloadConfig()[0]
        proc_infos = []
        for name in removed:
            proc_infos.append(self._stopProcessInternal(name))
        for name in changed:
            self._stopProcessInternal(name)
            self._client.supervisor.removeProcessGroup(name)
            self._client.supervisor.addProcessGroup(name)
            proc_infos.append(self.startProcess(name))
        # Don't need to start as we'll do this separately
        for name in added:
            self._client.supervisor.addProcessGroup(name)
            if start_new:
                proc_infos.append(self.startProcess(name))
        return proc_infos

    # def signalAllProcesses(self, signal):
    #     return self._client.supervisor.signalAllProcesses()

    def signalProcess(self, name: str, signal):
        if name not in self._cfg.program:
            raise RuntimeError(f"Unknown process: {name}")
        return self._client.supervisor.signalProcess(name, signal)
