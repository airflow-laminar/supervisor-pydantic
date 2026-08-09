# supervisor_pydantic.SupervisorctlConfiguration

### *pydantic model* supervisor_pydantic.SupervisorctlConfiguration[[source]](../../../_modules/supervisor_pydantic/config/supervisorctl.html.md#SupervisorctlConfiguration)

Bases: `_BaseCfgModel`

#### *field* serverurl *: AnyUrl | None* *= None*

The URL that should be used to access the supervisord server, e.g. [http://localhost:9001](http://localhost:9001). For UNIX domain sockets, use unix:///absolute/path/to/file.sock.

#### *field* username *: Annotated[str, AfterValidator(func=\_is_username)] | None* *= None*

The username to pass to the supervisord server for use in authentication. This should be same as username from the supervisord server configuration for the port or UNIX domain socket you’re attempting to access.

#### *field* password *: SecretStr | None* *= None*

The password to pass to the supervisord server for use in authentication. This should be the cleartext version of password from the supervisord server configuration for the port or UNIX domain socket you’re attempting to access. This value cannot be passed as a SHA hash. Unlike other passwords specified in this file, it must be provided in cleartext.

#### *field* prompt *: str | None* *= None*

String used as supervisorctl prompt.

#### *field* history_file *: Path | None* *= None*

A path to use as the readline persistent history file. If you enable this feature by choosing a path, your supervisorctl commands will be kept in the file, and you can use readline (e.g. arrow-up) to invoke commands you performed in your last supervisorctl session.
