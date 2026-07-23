# supervisor_pydantic.RpcInterfaceConfiguration

### *pydantic model* supervisor_pydantic.RpcInterfaceConfiguration

Bases: `_BaseCfgModel`

#### to_cfg(key: str) → str

#### *field* rpcinterface_factory *: str* *= 'supervisor.rpcinterface:make_main_rpcinterface'*

pkg_resources “entry point” dotted name to your RPC interface’s factory function.

#### *field* kwargs *: dict[str, Any] | None* *= None*
