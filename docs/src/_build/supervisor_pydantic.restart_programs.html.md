# supervisor_pydantic.restart_programs

### supervisor_pydantic.restart_programs(cfg: ~pathlib.Annotated[~pathlib.Path, <typer.models.OptionInfo object at 0x7fd9d7e45390>] = PosixPath('pydantic.json'), force: bool = False, \_exit: ~typing.Annotated[bool, <typer.models.ArgumentInfo object at 0x7fd9d7e45450>] = True)[[source]](../../../_modules/supervisor_pydantic/convenience/commands.html.md#restart_programs)

Restart all programs in the supervisor instance

* **Parameters:**
  * **cfg** (*Annotated* *[**Path* *,* *Option* *,* *optional*) – Path to JSON file of SupervisorConvenienceConfiguration
  * **force** (*bool* *,* *optional*) – if true, force restart. Defaults to False.
