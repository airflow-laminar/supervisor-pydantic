# supervisor_pydantic.SupervisorConfiguration

### *pydantic model* supervisor_pydantic.SupervisorConfiguration

Bases: `BaseModel`

#### to_cfg() → str

#### *field* unix_http_server *: [UnixHttpServerConfiguration](supervisor_pydantic.UnixHttpServerConfiguration.md#supervisor_pydantic.UnixHttpServerConfiguration) | None* *= None*

#### *field* inet_http_server *: [InetHttpServerConfiguration](supervisor_pydantic.InetHttpServerConfiguration.md#supervisor_pydantic.InetHttpServerConfiguration) | None* *= None*

#### *field* supervisord *: [SupervisordConfiguration](supervisor_pydantic.SupervisordConfiguration.md#supervisor_pydantic.SupervisordConfiguration)* *= SupervisordConfiguration(logfile=None, logfile_maxbytes=None, logfile_backups=None, loglevel=None, pidfile=None, umask=None, nodaemon=None, silent=None, minfds=None, minprocs=None, nocleanup=None, childlogdir=None, user=None, directory=None, strip_ansi=None, environment=None, identifier=None)*

#### *field* supervisorctl *: [SupervisorctlConfiguration](supervisor_pydantic.SupervisorctlConfiguration.md#supervisor_pydantic.SupervisorctlConfiguration)* *= SupervisorctlConfiguration(serverurl=None, username=None, password=None, prompt=None, history_file=None)*

#### *field* include *: [IncludeConfiguration](supervisor_pydantic.IncludeConfiguration.md#supervisor_pydantic.IncludeConfiguration) | None* *= None*

#### *field* program *: dict[str, [ProgramConfiguration](supervisor_pydantic.ProgramConfiguration.md#supervisor_pydantic.ProgramConfiguration)]* *[Required]*

#### *field* group *: dict[str, [GroupConfiguration](supervisor_pydantic.GroupConfiguration.md#supervisor_pydantic.GroupConfiguration)] | None* *= None*

#### *field* fcgiprogram *: dict[str, [FcgiProgramConfiguration](supervisor_pydantic.FcgiProgramConfiguration.md#supervisor_pydantic.FcgiProgramConfiguration)] | None* *= None*

#### *field* eventlistener *: dict[str, [EventListenerConfiguration](supervisor_pydantic.EventListenerConfiguration.md#supervisor_pydantic.EventListenerConfiguration)] | None* *= None*

#### *field* rpcinterface *: dict[str, [RpcInterfaceConfiguration](supervisor_pydantic.RpcInterfaceConfiguration.md#supervisor_pydantic.RpcInterfaceConfiguration)] | None* *= None*

#### *field* config_path *: Path | None* *= 'supervisord.conf'*

Path to supervisor configuration file, relative to working_dir

#### *field* working_dir *: Path | None* *= ''*

Path to supervisor working directory

#### *classmethod* load(config_dir: str = 'config', config_name: str = '', overrides: list[str] | None = None, , basepath: str = '', \_offset: int = 3) → [SupervisorConfiguration](#supervisor_pydantic.SupervisorConfiguration)

#### write()

#### rmdir()

#### start(daemon: bool = False)

#### running()

#### stop()

#### kill()
