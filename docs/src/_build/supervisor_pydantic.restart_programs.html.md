# supervisor_pydantic.restart_programs

### supervisor_pydantic.restart_programs(cfg: ~pathlib.Annotated[~pathlib.Path, <typer.models.OptionInfo object at 0x7f71d1342550>] = PosixPath('pydantic.json'), force: bool = False, \_exit: ~typing.Annotated[bool, <typer.models.ArgumentInfo object at 0x7f71d1342610>] = True)

Restart all programs in the supervisor instance

* **Parameters:**
  * **cfg** (*Annotated* *[**Path* *,* *Option* *,* *optional*) – Path to JSON file of SupervisorConvenienceConfiguration
  * **force** (*bool* *,* *optional*) – if true, force restart. Defaults to False.
