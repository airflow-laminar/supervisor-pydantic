# supervisor_pydantic.UnixHttpServerConfiguration

### *pydantic model* supervisor_pydantic.UnixHttpServerConfiguration[[source]](../../../_modules/supervisor_pydantic/config/unix_http_server.html.md#UnixHttpServerConfiguration)

Bases: `_BaseCfgModel`

#### *field* file *: Path | None* *= None*

A path to a UNIX domain socket on which supervisor will listen for HTTP/XML-RPC requests. supervisorctl uses XML-RPC to communicate with supervisord over this port. This option can include the value %(here)s, which expands to the directory in which the supervisord configuration file was found.

#### *field* chmod *: \_check_is_octal)] | None* *= None*

Change the UNIX permission mode bits of the UNIX domain socket to this value at startup.

#### *field* chown *: Annotated[str, AfterValidator(func=\_is_username_or_usernamegroup)] | None* *= None*

Change the user and group of the socket file to this value. May be a UNIX username (e.g. chrism) or a UNIX username and group separated by a colon (e.g. chrism:wheel).

#### *field* username *: Annotated[str, AfterValidator(func=\_is_username)] | None* *= None*

The username required for authentication to this HTTP server.

#### *field* password *: SecretStr | None* *= None*

The password required for authentication to this HTTP server. This can be a cleartext password, or can be specified as a SHA-1 hash if prefixed by the string {SHA}. For example, {SHA}82ab876d1387bfafe46cc1c8a2ef074eae50cb1d is the SHA-stored version of the password “thepassword”. Note that hashed password must be in hex format.
