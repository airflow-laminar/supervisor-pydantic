from subprocess import check_call

from supervisor_pydantic.config import SupervisorConvenienceConfiguration
from supervisor_pydantic.convenience.commands import start_supervisor, stop_supervisor, write_supervisor_config


def test_command():
    assert check_call(["_supervisor_convenience", "--help"]) == 0


def test_write(supervisor_convenience_configuration: SupervisorConvenienceConfiguration):
    json = supervisor_convenience_configuration.model_dump_json(exclude_unset=True)
    assert write_supervisor_config(json, _exit=False)
    assert supervisor_convenience_configuration._pydantic_path.read_text().strip() == json
    supervisor_convenience_configuration.rmdir()


def test_start_stop(supervisor_convenience_configuration: SupervisorConvenienceConfiguration):
    json = supervisor_convenience_configuration.model_dump_json(exclude_unset=True)
    assert write_supervisor_config(json, _exit=False)
    assert supervisor_convenience_configuration._pydantic_path.read_text().strip() == json
    assert start_supervisor(supervisor_convenience_configuration._pydantic_path, _exit=False)
    assert stop_supervisor(supervisor_convenience_configuration._pydantic_path, _exit=False)
    supervisor_convenience_configuration.rmdir()
