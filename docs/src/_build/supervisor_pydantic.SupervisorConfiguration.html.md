# supervisor_pydantic.SupervisorConfiguration

### *pydantic model* supervisor_pydantic.SupervisorConfiguration[[source]](../../../_modules/supervisor_pydantic/config/supervisor.html.md#SupervisorConfiguration)

Bases: `BaseModel`

#### to_cfg() → str[[source]](../../../_modules/supervisor_pydantic/config/supervisor.html.md#SupervisorConfiguration.to_cfg)

#### *field* unix_http_server *: [UnixHttpServerConfiguration](supervisor_pydantic.UnixHttpServerConfiguration.html.md#supervisor_pydantic.UnixHttpServerConfiguration) | None* *= None*

#### *field* inet_http_server *: [InetHttpServerConfiguration](supervisor_pydantic.InetHttpServerConfiguration.html.md#supervisor_pydantic.InetHttpServerConfiguration) | None* *= None*

#### *field* supervisord *: [SupervisordConfiguration](supervisor_pydantic.SupervisordConfiguration.html.md#supervisor_pydantic.SupervisordConfiguration)* *= SupervisordConfiguration(logfile=None, logfile_maxbytes=None, logfile_backups=None, loglevel=None, pidfile=None, umask=None, nodaemon=None, silent=None, minfds=None, minprocs=None, nocleanup=None, childlogdir=None, user=None, directory=None, strip_ansi=None, environment=None, identifier=None)*

#### *field* supervisorctl *: [SupervisorctlConfiguration](supervisor_pydantic.SupervisorctlConfiguration.html.md#supervisor_pydantic.SupervisorctlConfiguration)* *= SupervisorctlConfiguration(serverurl=None, username=None, password=None, prompt=None, history_file=None)*

#### *field* include *: [IncludeConfiguration](supervisor_pydantic.IncludeConfiguration.html.md#supervisor_pydantic.IncludeConfiguration) | None* *= None*

#### *field* program *: dict[str, [ProgramConfiguration](supervisor_pydantic.ProgramConfiguration.html.md#supervisor_pydantic.ProgramConfiguration)]* *[Required]*

#### *field* group *: dict[str, [GroupConfiguration](supervisor_pydantic.GroupConfiguration.html.md#supervisor_pydantic.GroupConfiguration)] | None* *= None*

#### *field* fcgiprogram *: dict[str, [FcgiProgramConfiguration](supervisor_pydantic.FcgiProgramConfiguration.html.md#supervisor_pydantic.FcgiProgramConfiguration)] | None* *= None*

#### *field* eventlistener *: dict[str, [EventListenerConfiguration](supervisor_pydantic.EventListenerConfiguration.html.md#supervisor_pydantic.EventListenerConfiguration)] | None* *= None*

#### *field* rpcinterface *: dict[str, [RpcInterfaceConfiguration](supervisor_pydantic.RpcInterfaceConfiguration.html.md#supervisor_pydantic.RpcInterfaceConfiguration)] | None* *= None*

#### *field* config_path *: Path | None* *= 'supervisord.conf'*

Path to supervisor configuration file, relative to working_dir

#### *field* working_dir *: Path | None* *= ''*

Path to supervisor working directory

#### *classmethod* load(config_dir: str = 'config', config_name: str = '', overrides: list[str] | None = None, , basepath: str = '', \_offset: int = 3) → [SupervisorConfiguration](#supervisor_pydantic.SupervisorConfiguration)[[source]](../../../_modules/supervisor_pydantic/config/supervisor.html.md#SupervisorConfiguration.load)

#### write()[[source]](../../../_modules/supervisor_pydantic/config/supervisor.html.md#SupervisorConfiguration.write)

#### rmdir()[[source]](../../../_modules/supervisor_pydantic/config/supervisor.html.md#SupervisorConfiguration.rmdir)

#### start(daemon: bool = False)[[source]](../../../_modules/supervisor_pydantic/config/supervisor.html.md#SupervisorConfiguration.start)

#### running()[[source]](../../../_modules/supervisor_pydantic/config/supervisor.html.md#SupervisorConfiguration.running)

#### stop()[[source]](../../../_modules/supervisor_pydantic/config/supervisor.html.md#SupervisorConfiguration.stop)

#### kill()[[source]](../../../_modules/supervisor_pydantic/config/supervisor.html.md#SupervisorConfiguration.kill)
