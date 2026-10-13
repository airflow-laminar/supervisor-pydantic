import json
import subprocess
import sys

from pydantic import ValidationError
from pytest import mark, raises

from supervisor_pydantic import ProgramConfiguration


def test_inst():
    with raises(ValidationError):
        ProgramConfiguration.model_validate({})
    ProgramConfiguration(command="echo 'test'")


def test_dump_exitcodes():
    # ensure that converting exit codes to string does not regress
    # pydantic_core._pydantic_core.PydanticSerializationError: Error serializing to JSON:
    # PydanticSerializationError: Error calling function `_dump_exitcodes`:
    # TypeError: sequence item 0: expected str instance, int found
    ProgramConfiguration(command="echo 'test'", exitcodes=[0]).model_dump_json(exclude_unset=True)


def test_autorestart_options():
    ProgramConfiguration(command="echo 'test'", autorestart=True).model_dump_json(exclude_unset=True)
    ProgramConfiguration(command="echo 'test'", autorestart=False).model_dump_json(exclude_unset=True)
    ProgramConfiguration(command="echo 'test'", autorestart="unexpected").model_dump_json(exclude_unset=True)
    with raises(ValidationError):
        ProgramConfiguration.model_validate({"command": "echo 'test'", "autorestart": "other"}).model_dump_json(exclude_unset=True)


def test_cfg():
    c = ProgramConfiguration(command="echo 'test'", environment={"USER": "test", "HOME": "a blerg's path"})
    assert c.to_cfg("name").strip() == "[program:name]\ncommand=echo 'test'\nenvironment=USER=test,HOME='a blerg'\"'\"'s path'"


@mark.parametrize(
    "environment",
    [
        {"CHANNELS": "[]", "DOMAINS": '["point72.com","cubistsystematic.com","point72.jsmalerts.atlassian.net"]'},
        {"VALUE": "comma,value=with equals", "EMPTY": "", "HASH": "a#b"},
        {"HOME": "a blerg's path", "JSON": '{"label":"it\'s valid"}'},
    ],
)
def test_environment_survives_repeated_json_roundtrips(environment):
    program = ProgramConfiguration(command="echo test", environment=environment)
    serialized = program.model_dump_json()
    for _round in range(5):
        program = ProgramConfiguration.model_validate_json(program.model_dump_json())
        assert program.environment == environment
        assert program.model_dump_json() == serialized


def test_json_environment_roundtrip_remains_valid_supervisor_configuration():
    environment = {"CHANNELS": "[]", "DOMAINS": '["point72.com","cubistsystematic.com","point72.jsmalerts.atlassian.net"]'}
    program = ProgramConfiguration(command="echo test", environment=environment)
    for _round in range(5):
        program = ProgramConfiguration.model_validate_json(program.model_dump_json())
        line = next(line for line in program.to_cfg("gateway").splitlines() if line.startswith("environment="))
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import json,sys; from supervisor.datatypes import dict_of_key_value_pairs; print(json.dumps(dict_of_key_value_pairs(sys.argv[1])))",
                line.removeprefix("environment="),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        assert json.loads(result.stdout) == environment


def test_malformed_environment_is_rejected_instead_of_dropping_values():
    with raises(ValidationError):
        ProgramConfiguration(command="echo test", environment="DOMAINS=first,second")
