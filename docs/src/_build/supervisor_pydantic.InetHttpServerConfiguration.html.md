# supervisor_pydantic.InetHttpServerConfiguration

### *pydantic model* supervisor_pydantic.InetHttpServerConfiguration[[source]](../../../_modules/supervisor_pydantic/config/inet_http_server.html.md#InetHttpServerConfiguration)

Bases: `_BaseCfgModel`

#### to_cfg() → str[[source]](../../../_modules/supervisor_pydantic/config/inet_http_server.html.md#InetHttpServerConfiguration.to_cfg)

#### *field* port *: Annotated[str, BeforeValidator(func=\_convert_to_host_port, json_schema_input_type=PydanticUndefined), AfterValidator(func=\_is_host_port)] | None* *= None*

A TCP host:port value or (e.g. 127.0.0.1:9001) on which supervisor will listen for HTTP/XML-RPC requests. supervisorctl will use XML-RPC to communicate with supervisord over this port. To listen on all interfaces in the machine, use :9001 or 

```
*
```

:9001. Please read the security warning above.

#### *field* username *: Annotated[str, AfterValidator(func=\_is_username)] | None* *= None*

The username required for authentication to this HTTP server.

#### *field* password *: SecretStr | None* *= None*

he password required for authentication to this HTTP server. This can be a cleartext password, or can be specified as a SHA-1 hash if prefixed by the string {SHA}. For example, {SHA}82ab876d1387bfafe46cc1c8a2ef074eae50cb1d is the SHA-stored version of the password “thepassword”. Note that hashed password must be in hex format.
