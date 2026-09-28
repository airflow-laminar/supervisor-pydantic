from datetime import UTC, datetime
from unittest.mock import MagicMock, call

from supervisor_pydantic.client import ProcessInfo, ProcessState, SupervisorRemoteXMLRPCClient


def _gen() -> ProcessInfo:
    return ProcessInfo(
        name="test",
        group="test",
        state=ProcessState.UNKNOWN,
        description="",
        start=datetime.now(UTC),
        stop=datetime.now(UTC),
        now=datetime.now(UTC),
        spawnerr="",
        exitstatus=0,
        logfile="",
        stdout_logfile="",
        stderr_logfile="",
        pid=0,
    )


def test_ok():
    x = _gen()
    x.state = ProcessState.RUNNING
    assert x.ok()
    x.state = ProcessState.EXITED
    x.exitstatus = 0
    assert x.ok()


def test_never_started_is_not_done_or_ok():
    x = _gen()
    x.state = ProcessState.STOPPED
    x.description = "Not started"
    x.start = datetime.fromtimestamp(0, UTC)

    assert not x.done()
    assert not x.ok()


def test_spawn_error_is_preserved():
    data = _gen().model_dump(exclude={"spawnerr"})
    data["spawnerr"] = "NOT_EXECUTABLE: No closing quotation"

    process = ProcessInfo.model_validate(data)

    assert process.spawnerr == "NOT_EXECUTABLE: No closing quotation"
    assert process.model_dump()["spawnerr"] == "NOT_EXECUTABLE: No closing quotation"


def _client() -> SupervisorRemoteXMLRPCClient:
    client = SupervisorRemoteXMLRPCClient.__new__(SupervisorRemoteXMLRPCClient)
    client._cfg = MagicMock(program={"test": MagicMock()})
    client._client = MagicMock()
    return client


def test_process_log_arguments_are_forwarded():
    client = _client()

    client.readProcessStderrLog("test", offset=4, length=8)
    client.readProcessStdoutLog("test", offset=2, length=6)

    client._client.supervisor.readProcessStderrLog.assert_called_once_with("test", 4, 8)
    client._client.supervisor.readProcessStdoutLog.assert_called_once_with("test", 2, 6)


def test_signal_process_arguments_are_forwarded():
    client = _client()

    client.signalProcess("test", "TERM")

    client._client.supervisor.signalProcess.assert_called_once_with("test", "TERM")


def test_changed_process_group_is_replaced_before_restart():
    client = _client()
    client._client.supervisor.reloadConfig.return_value = [[[], ["test"], []]]
    client._stopProcessInternal = MagicMock()
    client.startProcess = MagicMock()

    client.reloadConfig()

    client._client.supervisor.removeProcessGroup.assert_called_once_with("test")
    client._client.supervisor.addProcessGroup.assert_called_once_with("test")
    assert client._client.supervisor.method_calls.index(call.removeProcessGroup("test")) < client._client.supervisor.method_calls.index(
        call.addProcessGroup("test")
    )
