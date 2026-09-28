# supervisor_pydantic.start_programs

### supervisor_pydantic.start_programs(cfg: ~pathlib.Annotated[~pathlib.Path, <typer.models.OptionInfo object at 0x7f0308afb690>] = PosixPath('pydantic.json'), restart: bool = False, \_exit: ~typing.Annotated[bool, <typer.models.ArgumentInfo object at 0x7f0308b56950>] = True)[[source]](../../../_modules/supervisor_pydantic/convenience/commands.html.md#start_programs)

Start all programs in the supervisor instance

* **Parameters:**
  * **cfg** (*Annotated* *[**Path* *,* *Option* *,* *optional*) – Path to JSON file of SupervisorConvenienceConfiguration
  * **restart** (*bool* *,* *optional*) – if true, restart all programs. Defaults to False.
