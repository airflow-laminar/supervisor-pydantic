from pydantic import ValidationError
from pytest import raises

from supervisor_pydantic import ProgramConfiguration, SupervisorConfiguration


def test_config_instantiation():
    with raises(ValidationError):
        c = SupervisorConfiguration.model_validate({})
    c = SupervisorConfiguration(program={"test": ProgramConfiguration(command="echo 'hello'")})
    assert c
