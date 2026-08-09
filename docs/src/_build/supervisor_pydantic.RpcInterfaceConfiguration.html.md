# supervisor_pydantic.RpcInterfaceConfiguration

### *pydantic model* supervisor_pydantic.RpcInterfaceConfiguration[[source]](../../../_modules/supervisor_pydantic/config/rpcinterface.html.md#RpcInterfaceConfiguration)

Bases: `_BaseCfgModel`

#### to_cfg(key: str) → str[[source]](../../../_modules/supervisor_pydantic/config/rpcinterface.html.md#RpcInterfaceConfiguration.to_cfg)

#### *field* rpcinterface_factory *: str* *= 'supervisor.rpcinterface:make_main_rpcinterface'*

pkg_resources “entry point” dotted name to your RPC interface’s factory function.

#### *field* kwargs *: dict[str, Any] | None* *= None*
