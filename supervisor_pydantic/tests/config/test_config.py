from getpass import getuser
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError
from pytest import raises

from supervisor_pydantic import (
    EventListenerConfiguration,
    FcgiProgramConfiguration,
    GroupConfiguration,
    IncludeConfiguration,
    InetHttpServerConfiguration,
    ProgramConfiguration,
    RpcInterfaceConfiguration,
    SupervisorConfiguration,
    SupervisorctlConfiguration,
    SupervisordConfiguration,
    UnixHttpServerConfiguration,
)


def test_inst():
    with raises(ValidationError):
        SupervisorConfiguration()
    with (
        patch("supervisor_pydantic.config.supervisor.gettempdir") as p1,
    ):
        pth = Path(__file__).resolve().parent.parent.parent.parent / ".pytest_cache"
        p1.return_value = str(pth)
        c = SupervisorConfiguration(program={"test": ProgramConfiguration(command="test")})
        assert str(c.working_dir) == str(pth / f"supervisor-{getuser()}-test")
        assert str(c.config_path) == str(pth / f"supervisor-{getuser()}-test" / "supervisord.conf")


def test_cfg_roundtrip_json():
    with (
        patch("supervisor_pydantic.config.supervisor.gettempdir") as p1,
    ):
        pth = Path(__file__).resolve().parent.parent.parent.parent / ".pytest_cache"
        p1.return_value = str(pth)
        c = SupervisorConfiguration(program={"test": ProgramConfiguration(command="test")})
        rehydrated = c.model_validate_json(c.model_dump_json(exclude_unset=True))
        assert rehydrated == c
        assert rehydrated.model_dump_json(exclude_unset=True) == c.model_dump_json(exclude_unset=True)


def test_cfg():
    with (
        patch("supervisor_pydantic.config.supervisor.gettempdir") as p1,
    ):
        pth = Path(__file__).resolve().parent.parent.parent.parent / ".pytest_cache"
        p1.return_value = str(pth)
        c = SupervisorConfiguration(program={"test": ProgramConfiguration(command="test")})
        assert (
            c.to_cfg().strip()
            == """[supervisord]
logfile={dir}/supervisord.log
pidfile={dir}/supervisord.pid
directory={dir}

[supervisorctl]

[program:test]
command=test
directory={dir}/test""".format(dir=str(pth / f"supervisor-{getuser()}-test"))
        )


def test_cfg_all():
    with (
        patch("supervisor_pydantic.config.supervisor.gettempdir") as p1,
    ):
        pth = Path(__file__).resolve().parent.parent.parent.parent / ".pytest_cache"
        p1.return_value = str(pth)
        c = SupervisorConfiguration(
            unix_http_server=UnixHttpServerConfiguration(
                file="/a/test/file",
                chmod="0777",
                chown="test",
                username="test",
                password="testpw",
            ),
            inet_http_server=InetHttpServerConfiguration(port="127.0.0.1:8000", username="test", password="testpw"),
            supervisord=SupervisordConfiguration(),
            supervisorctl=SupervisorctlConfiguration(username="test", password="testpw"),
            include=IncludeConfiguration(files=["a/test/file", "another/test/file"]),
            program={"test": ProgramConfiguration(command="test")},
            group={"testgroup": GroupConfiguration(programs=["test"])},
            fcgiprogram={"testfcgi": FcgiProgramConfiguration(command="echo 'test'", socket="test")},
            eventlistener={"testeventlistener": EventListenerConfiguration(command="echo 'test'")},
            rpcinterface={"testrpcinterface": RpcInterfaceConfiguration(rpcinterface_factory="a.test.module")},
        )
        print(c.to_cfg().strip())
        assert (
            c.to_cfg().strip()
            == """[unix_http_server]
file=/a/test/file
chmod=0777
chown=test
username=test
password=testpw

[inet_http_server]
port=127.0.0.1:8000
username=test
password=testpw

[supervisord]
logfile={dir}/supervisord.log
pidfile={dir}/supervisord.pid
directory={dir}

[supervisorctl]
username=test
password=testpw

[include]
files=a/test/file another/test/file

[program:test]
command=test
directory={dir}/test

[group:testgroup]
programs=test

[fcgi-program:testfcgi]
command=echo 'test'
socket=test

[eventlistener:testeventlistener]
command=echo 'test'

[rpcinterface:testrpcinterface]
supervisor.rpcinterface_factory=a.test.module""".format(dir=str(pth / f"supervisor-{getuser()}-test"))
        )
