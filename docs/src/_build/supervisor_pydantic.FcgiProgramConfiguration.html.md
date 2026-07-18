# supervisor_pydantic.FcgiProgramConfiguration

### *pydantic model* supervisor_pydantic.FcgiProgramConfiguration

Bases: [`ProgramConfiguration`](supervisor_pydantic.ProgramConfiguration.md#supervisor_pydantic.ProgramConfiguration)

#### to_cfg(key: str) → str

#### *field* socket *: str* *[Required]*

The FastCGI socket for this program, either TCP or UNIX domain socket. For TCP sockets, use this format: [tcp://localhost:9002](tcp://localhost:9002). For UNIX domain sockets, use unix:///absolute/path/to/file.sock. String expressions are evaluated against a dictionary containing the keys “program_name” and “here” (the directory of the supervisord config file).

#### *field* socket_backlog *: str | None* *= None*

Sets socket listen(2) backlog.

#### *field* socket_owner *: Annotated[str, AfterValidator(func=\_is_username_or_usernamegroup)] | None* *= None*

For UNIX domain sockets, this parameter can be used to specify the user and group for the FastCGI socket. May be a UNIX username (e.g. chrism) or a UNIX username and group separated by a colon (e.g. chrism:wheel).

#### *field* socket_mode *: \_check_is_octal)] | None* *= None*

For UNIX domain sockets, this parameter can be used to specify the permission mode.
