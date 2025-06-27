import os
from getpass import getuser
from logging import getLogger
from pathlib import Path
from shutil import rmtree
from signal import SIGKILL, SIGTERM
from subprocess import Popen
from tempfile import gettempdir
from typing import Dict, Optional

from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from pydantic import BaseModel, Field, PrivateAttr, model_validator

from ..exceptions import ConfigNotFoundError
from ..utils import _get_calling_file
from .convenience import ConvenienceConfiguration
from .eventlistener import EventListenerConfiguration
from .fcgiprogram import FcgiProgramConfiguration
from .group import GroupConfiguration
from .include import IncludeConfiguration
from .inet_http_server import InetHttpServerConfiguration
from .program import ProgramConfiguration
from .rpcinterface import RpcInterfaceConfiguration
from .supervisorctl import SupervisorctlConfiguration
from .supervisord import SupervisordConfiguration
from .unix_http_server import UnixHttpServerConfiguration

__all__ = (
    "SupervisorConfiguration",
    "SupervisorConvenienceConfiguration",
    "load_config",
    "load_convenience_config",
)

_log = getLogger(__name__)


class SupervisorConfiguration(BaseModel):
    def to_cfg(self) -> str:
        ret = ""
        if self.unix_http_server:
            ret += self.unix_http_server.to_cfg() + "\n"
        if self.inet_http_server:
            ret += self.inet_http_server.to_cfg() + "\n"
        if self.supervisord:
            ret += self.supervisord.to_cfg() + "\n"
        if self.supervisorctl:
            ret += self.supervisorctl.to_cfg() + "\n"
        if self.include:
            ret += self.include.to_cfg() + "\n"
        for k, v in self.program.items():
            ret += v.to_cfg(key=k) + "\n"
        for k, v in (self.group or {}).items():
            ret += v.to_cfg(key=k) + "\n"
        for k, v in (self.fcgiprogram or {}).items():
            ret += v.to_cfg(key=k) + "\n"
        for k, v in (self.eventlistener or {}).items():
            ret += v.to_cfg(key=k) + "\n"
        for k, v in (self.rpcinterface or {}).items():
            ret += v.to_cfg(key=k) + "\n"
        return ret

    # supervisor setup
    unix_http_server: Optional[UnixHttpServerConfiguration] = Field(default=None)
    inet_http_server: Optional[InetHttpServerConfiguration] = Field(default=None)
    supervisord: SupervisordConfiguration = Field(default=SupervisordConfiguration())
    supervisorctl: SupervisorctlConfiguration = Field(default=SupervisorctlConfiguration())
    include: Optional[IncludeConfiguration] = Field(default=None)

    program: Dict[str, ProgramConfiguration]
    group: Optional[Dict[str, GroupConfiguration]] = Field(default=None)

    fcgiprogram: Optional[Dict[str, FcgiProgramConfiguration]] = Field(default=None)
    eventlistener: Optional[Dict[str, EventListenerConfiguration]] = Field(default=None)
    rpcinterface: Optional[Dict[str, RpcInterfaceConfiguration]] = Field(default=None)

    # other configuration
    config_path: Optional[Path] = Field(default="supervisord.conf", description="Path to supervisor configuration file, relative to `working_dir`")
    working_dir: Optional[Path] = Field(default="", description="Path to supervisor working directory")

    @model_validator(mode="after")
    def _setup_config_and_working_dir(self):
        if self.working_dir is None or self.working_dir == "" and self.supervisord.directory:
            # use this as the dir
            self.working_dir = self.supervisord.directory
        elif self.working_dir is None or self.working_dir == "":
            # align supervisord to working dir
            self.working_dir = Path(gettempdir()).resolve() / f"supervisor-{getuser()}-{'-'.join(list(self.program.keys()))}"

        if not self.supervisord.directory:
            # align supervisord to working dir
            self.supervisord.directory = self.working_dir

        if not Path(self.config_path).exists() or str(self.working_dir) not in str(self.config_path):
            self.config_path = (self.working_dir / self.config_path).resolve()

        # force pidfile to be in working dir if not otherwise set
        if not self.supervisord.pidfile:
            self.supervisord.pidfile = self.working_dir / "supervisord.pid"

        # force logfile to be in working dir if not otherwise set
        if not self.supervisord.logfile:
            self.supervisord.logfile = self.working_dir / "supervisord.log"

        for name, program_config in self.program.items():
            if program_config.directory is None:
                program_config.directory = self.working_dir / name
        return self

    @classmethod
    def _find_parent_config_folder(cls, config_dir: str = "config", config_name: str = "", *, basepath: str = "", _offset: int = 2):
        if basepath:
            if basepath.endswith((".py", ".cfg", ".yml", ".yaml")):
                calling_dag = Path(basepath)
            else:
                calling_dag = Path(basepath) / "dummy.py"
        else:
            calling_dag = Path(_get_calling_file(offset=_offset))
        folder = calling_dag.parent.resolve()
        exists = (
            (folder / config_dir).exists()
            if not config_name
            else ((folder / config_dir / f"{config_name}.yml").exists() or (folder / config_dir / f"{config_name}.yaml").exists())
        )
        while not exists:
            folder = folder.parent
            if str(folder) == os.path.abspath(os.sep):
                raise ConfigNotFoundError(config_dir=config_dir, dagfile=calling_dag)
            exists = (
                (folder / config_dir).exists()
                if not config_name
                else ((folder / config_dir / f"{config_name}.yml").exists() or (folder / config_dir / f"{config_name}.yaml").exists())
            )

        config_dir = (folder / config_dir).resolve()
        if not config_name:
            return folder.resolve(), config_dir, ""
        elif (folder / config_dir / f"{config_name}.yml").exists():
            return folder.resolve(), config_dir, (folder / config_dir / f"{config_name}.yml").resolve()
        return folder.resolve(), config_dir, (folder / config_dir / f"{config_name}.yaml").resolve()

    @classmethod
    def load(
        cls: "SupervisorConfiguration",
        config_dir: str = "config",
        config_name: str = "",
        overrides: Optional[list[str]] = None,
        *,
        basepath: str = "",
        _offset: int = 3,
    ) -> "SupervisorConfiguration":
        overrides = overrides or []

        with initialize_config_dir(config_dir=str(Path(__file__).resolve().parent / "hydra"), version_base=None):
            if config_dir:
                hydra_folder, config_dir, _ = cls._find_parent_config_folder(
                    config_dir=config_dir, config_name=config_name, basepath=basepath, _offset=_offset
                )

                cfg = compose(config_name="base", overrides=[], return_hydra_config=True)
                searchpaths = cfg["hydra"]["searchpath"]
                searchpaths.extend([hydra_folder, config_dir])
                if config_name:
                    overrides = [
                        f"+config={config_name}",
                        *overrides.copy(),
                        f"hydra.searchpath=[{','.join(searchpaths)}]",
                    ]
                else:
                    overrides = [*overrides.copy(), f"hydra.searchpath=[{','.join(searchpaths)}]"]

            cfg = compose(config_name="base", overrides=overrides)
            config = instantiate(cfg)

            if not isinstance(config, cls):
                if issubclass(cls, type(config)):
                    config = config.model_dump(exclude_unset=True)
                config = cls(**config)
            return config

    def write(self):
        _log.info(f"Making working dir: {self.working_dir}")
        self.working_dir.mkdir(parents=True, exist_ok=True)
        for program_name, program_config in self.program.items():
            if program_config.directory:
                _log.info(f"Making program dir ({program_name}): {program_config.directory}")
                program_config.directory.mkdir(exist_ok=True)
        _log.info(f"Writing config file: {self.config_path}")
        self.config_path.write_text(self.to_cfg())

    def rmdir(self):
        if not self.running():
            _log.info(f"Removing working dir: {self.working_dir}")
            rmtree(self.working_dir)

    def start(self, daemon: bool = False):
        _log.info(f"Starting supervisord: {self.config_path}")
        if not self.running():
            if daemon is False:
                Popen(f"supervisord -n -c {str(self.config_path)}", shell=True)
                return
            Popen(f"supervisord -c {str(self.config_path)}", close_fds=True, shell=True)

    def running(self):
        # grab the pidfile, find the process with the pid, and kill
        _log.info(f"Checking supervisord: {self.supervisord.pidfile}")
        if not self.supervisord.pidfile.exists():
            return False
        try:
            os.kill(int(self.supervisord.pidfile.read_text()), 0)
        except OSError:
            return False
        return True

    def stop(self):
        if self.running():
            # grab the pidfile, find the process with the pid, and kill with SIGTERM
            _log.info(f"Stopping supervisord: {self.supervisord.pidfile}")
            os.kill(int(self.supervisord.pidfile.read_text()), SIGTERM)

    def kill(self):
        if self.running():
            # grab the pidfile, find the process with the pid, and kill with SIGKILL
            _log.info(f"Killing supervisord: {self.supervisord.pidfile}")
            os.kill(int(self.supervisord.pidfile.read_text()), SIGKILL)


class SupervisorConvenienceConfiguration(SupervisorConfiguration):
    convenience: ConvenienceConfiguration = Field(
        default_factory=ConvenienceConfiguration, description="Required configurations for convenience integration"
    )

    _pydantic_path: Path = PrivateAttr(default="pydantic.json")

    def _write_self(self):
        # TODO make config driven
        self.write()
        _log.info(f"Writing model json: {self._pydantic_path}")
        Path(self._pydantic_path).write_text(self.model_dump_json(exclude_unset=True))

    @model_validator(mode="after")
    def _setup_convenience_defaults(self):
        """Method to overload configuration with values needed for the setup
        of convenience tasks that we construct"""
        # inet_http_server
        if not self.inet_http_server:
            self.inet_http_server = InetHttpServerConfiguration()

        self.inet_http_server.port = self.convenience.port
        self.inet_http_server.username = self.convenience.username
        self.inet_http_server.password = self.convenience.password

        self.supervisorctl.serverurl = f"{self.convenience.protocol}://{self.convenience.host}:{self.convenience.port.split(':')[-1]}/"

        # rpcinterface
        if not self.rpcinterface:
            self.rpcinterface = {"supervisor": RpcInterfaceConfiguration()}
        self.rpcinterface["supervisor"].rpcinterface_factory = self.convenience.rpcinterface_factory

        # supervisord
        self.supervisord.nodaemon = False
        self.supervisord.identifier = "supervisor"

        # programs
        for name, config in self.program.items():
            config.autostart = False
            config.autorestart = False
            config.startsecs = self.convenience.startsecs
            config.startretries = self.convenience.startretries
            config.exitcodes = self.convenience.exitcodes
            config.stopsignal = self.convenience.stopsignal
            config.stopwaitsecs = self.convenience.stopwaitsecs
            config.stopasgroup = self.convenience.stopasgroup
            config.killasgroup = self.convenience.killasgroup
            config.stdout_logfile = self.working_dir / name / "output.log"
            config.stderr_logfile = self.working_dir / name / "error.log"

        # other
        if str(self.working_dir) not in str(self._pydantic_path):
            self._pydantic_path = self.working_dir / "pydantic.json"
        return self


load_config = SupervisorConfiguration.load
load_convenience_config = SupervisorConvenienceConfiguration.load
