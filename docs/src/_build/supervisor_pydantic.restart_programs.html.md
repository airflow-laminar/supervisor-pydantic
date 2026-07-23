# supervisor_pydantic.restart_programs

### supervisor_pydantic.restart_programs(cfg: ~pathlib.Annotated[~pathlib.Path, <typer.models.OptionInfo object at 0x7f777405ca10>] = PosixPath('pydantic.json'), force: bool = False, \_exit: ~typing.Annotated[bool, <typer.models.ArgumentInfo object at 0x7f777405cad0>] = True)

Restart all programs in the supervisor instance

* **Parameters:**
  * **cfg** (*Annotated* *[**Path* *,* *Option* *,* *optional*) – Path to JSON file of SupervisorConvenienceConfiguration
  * **force** (*bool* *,* *optional*) – if true, force restart. Defaults to False.
