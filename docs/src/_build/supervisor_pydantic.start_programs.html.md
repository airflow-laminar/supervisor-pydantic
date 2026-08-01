# supervisor_pydantic.start_programs

### supervisor_pydantic.start_programs(cfg: ~pathlib.Annotated[~pathlib.Path, <typer.models.OptionInfo object at 0x7fe3ca297210>] = PosixPath('pydantic.json'), restart: bool = False, \_exit: ~typing.Annotated[bool, <typer.models.ArgumentInfo object at 0x7fe3ca171f90>] = True)

Start all programs in the supervisor instance

* **Parameters:**
  * **cfg** (*Annotated* *[**Path* *,* *Option* *,* *optional*) – Path to JSON file of SupervisorConvenienceConfiguration
  * **restart** (*bool* *,* *optional*) – if true, restart all programs. Defaults to False.
