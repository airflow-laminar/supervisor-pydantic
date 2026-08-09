# supervisor_pydantic.GroupConfiguration

### *pydantic model* supervisor_pydantic.GroupConfiguration[[source]](../../../_modules/supervisor_pydantic/config/group.html.md#GroupConfiguration)

Bases: `_BaseCfgModel`

#### to_cfg(key: str) → str[[source]](../../../_modules/supervisor_pydantic/config/group.html.md#GroupConfiguration.to_cfg)

#### *field* programs *: list[str]* *[Required]*

A comma-separated list of program names. The programs which are listed become members of the group.

#### *field* priority *: int | None* *= None*

A priority number analogous to a [program:x] priority value assigned to the group.
