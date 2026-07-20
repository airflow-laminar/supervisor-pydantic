# supervisor_pydantic.check_programs

### supervisor_pydantic.check_programs(cfg: ~pathlib.Annotated[~pathlib.Path, <typer.models.OptionInfo object at 0x7fdd8cf54a50>] = PosixPath('pydantic.json'), check_running: bool = False, check_done: bool = False, \_exit: ~typing.Annotated[bool, <typer.models.ArgumentInfo object at 0x7fdd8cf54b10>] = True)

Check if programs are in a good state.

* **Parameters:**
  * **cfg** (*Annotated* *[**Path* *,* *Option* *,* *optional*) – Path to JSON file of SupervisorConvenienceConfiguration
  * **check_running** (*bool* *,* *optional*) – if true, only return true if they’re running
  * **check_done** (*bool* *,* *optional*) – if true, only return true if they’re done (cleanly)
