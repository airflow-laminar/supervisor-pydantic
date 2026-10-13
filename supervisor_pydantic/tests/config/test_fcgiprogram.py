from pydantic import ValidationError
from pytest import raises

from supervisor_pydantic import FcgiProgramConfiguration


def test_inst():
    with raises(ValidationError):
        FcgiProgramConfiguration.model_validate({})
    with raises(ValidationError):
        FcgiProgramConfiguration.model_validate({"socket": "test"})
    with raises(ValidationError):
        FcgiProgramConfiguration.model_validate({"command": "test"})
    FcgiProgramConfiguration(command="echo 'test'", socket="test")


def test_cfg():
    c = FcgiProgramConfiguration(command="echo 'test'", socket="test")
    assert c.to_cfg("name").strip() == "[fcgi-program:name]\ncommand=echo 'test'\nsocket=test"
