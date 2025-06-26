from pydantic import ValidationError
from pytest import raises

from supervisor_pydantic import EventListenerConfiguration


def test_inst():
    with raises(ValidationError):
        EventListenerConfiguration()
    with raises(ValidationError):
        EventListenerConfiguration(stdout_capture_maxbytes=10)
    EventListenerConfiguration(command="echo 'test'")


def test_cfg():
    c = EventListenerConfiguration(command="echo 'test'")
    assert c.to_cfg("name").strip() == "[eventlistener:name]\ncommand=echo 'test'"


def test_cfg_roundtrip():
    c = EventListenerConfiguration(command="echo 'test'")
    print(c.model_dump_json(exclude_unset=True))
    assert c.model_validate_json(c.model_dump_json(exclude_unset=True)) == c

    c = EventListenerConfiguration(command="echo 'test'", events=["PROCESS_STATE"])
    assert c.model_validate_json(c.model_dump_json()) == c
