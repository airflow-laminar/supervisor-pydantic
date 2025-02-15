from getpass import getuser
from pathlib import Path
from unittest.mock import patch

from supervisor_pydantic import load_config


def test_hydra_config():
    with (
        patch("supervisor_pydantic.config.supervisor.gettempdir") as p1,
    ):
        pth = Path(__file__).resolve().parent.parent.parent.parent / ".pytest_cache"
        p1.return_value = str(pth)
        cfg = load_config("config", overrides=["+program=[sleep,echo]", "+rpcinterface=standard", "+inet_http_server=local"])
        assert (
            cfg.to_cfg().strip()
            == """[inet_http_server]
port=localhost:8000

[supervisord]
logfile={dir}/supervisord.log
pidfile={dir}/supervisord.pid
directory={dir}

[supervisorctl]

[program:sleep]
command=sleep 1000
directory={dir}/sleep

[program:echo]
command=echo
directory={dir}/echo

[rpcinterface:supervisor]
supervisor.rpcinterface_factory=supervisor.rpcinterface:make_main_rpcinterface""".format(dir=str(pth / f"supervisor-{getuser()}-sleep-echo"))
        )
