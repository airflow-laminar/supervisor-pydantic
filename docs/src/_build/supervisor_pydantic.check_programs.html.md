# supervisor_pydantic.check_programs

### supervisor_pydantic.check_programs(cfg: ~pathlib.Annotated[~pathlib.Path, <typer.models.OptionInfo object at 0x7f4d2c232e10>] = PosixPath('pydantic.json'), check_running: bool = False, check_done: bool = False, \_exit: ~typing.Annotated[bool, <typer.models.ArgumentInfo object at 0x7f4d2c232e90>] = True)[[source]](../../../_modules/supervisor_pydantic/convenience/commands.html.md#check_programs)

Check if programs are in a good state.

* **Parameters:**
  * **cfg** (*Annotated* *[**Path* *,* *Option* *,* *optional*) – Path to JSON file of SupervisorConvenienceConfiguration
  * **check_running** (*bool* *,* *optional*) – if true, only return true if they’re running
  * **check_done** (*bool* *,* *optional*) – if true, only return true if they’re done (cleanly)
