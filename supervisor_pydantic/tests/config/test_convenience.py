from supervisor_pydantic import ConvenienceConfiguration, ProgramConfiguration, SupervisorConvenienceConfiguration


def test_inst():
    ConvenienceConfiguration()


def test_inst_extra():
    SupervisorConvenienceConfiguration(convenience=ConvenienceConfiguration(), program={"test": ProgramConfiguration(command="echo test")})


def test_cfg():
    c = ConvenienceConfiguration(username="test", password="testpw")
    assert (
        c.to_cfg().strip()
        == """[convenience]
username=test
password=testpw"""
    )


def test_cfg_extra():
    c = SupervisorConvenienceConfiguration(
        convenience=ConvenienceConfiguration(port=7000),
        program={"test": ProgramConfiguration(command="echo test")},
        working_dir="/tmp/supervisor-runner-test",
    )
    assert (
        c.to_cfg().strip()
        == """[inet_http_server]
port=*:7000

[supervisord]
logfile=/tmp/supervisor-runner-test/supervisord.log
pidfile=/tmp/supervisor-runner-test/supervisord.pid
nodaemon=false
directory=/tmp/supervisor-runner-test
identifier=supervisor

[supervisorctl]
serverurl=http://localhost:7000/

[program:test]
command=echo test
autostart=false
startsecs=1
autorestart=false
exitcodes=0
stopsignal=TERM
stopwaitsecs=30
stopasgroup=true
killasgroup=true
stdout_logfile=/tmp/supervisor-runner-test/test/output.log
stderr_logfile=/tmp/supervisor-runner-test/test/error.log
directory=/tmp/supervisor-runner-test/test

[rpcinterface:supervisor]
supervisor.rpcinterface_factory=supervisor.rpcinterface:make_main_rpcinterface"""
    )
