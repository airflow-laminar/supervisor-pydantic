from supervisor_pydantic import ConvenienceConfiguration, ProgramConfiguration, SupervisorConvenienceConfiguration


def test_inst():
    ConvenienceConfiguration()


def test_inst_extra():
    SupervisorConvenienceConfiguration(convenience=ConvenienceConfiguration(), program={"test": ProgramConfiguration(command="echo test")})


def test_cfg():
    c = ConvenienceConfiguration(username="test", password="testpw")
    assert (
        c.to_cfg().strip()
        == "[convenience]\nstartsecs=1\nexitcodes=0\nstopsignal=TERM\nstopwaitsecs=30\nport=*:9001\nusername=test\npassword=testpw\nrpcinterface_factory=supervisor.rpcinterface:make_main_rpcinterface\nlocal_or_remote=local\nhost=localhost\nprotocol=http\nrpcpath=/RPC2\ncommand_timeout=30"
    )


def test_cfg_extra():
    c = SupervisorConvenienceConfiguration(
        convenience=ConvenienceConfiguration(), program={"test": ProgramConfiguration(command="echo test")}, working_dir="/tmp/supervisor-runner-test"
    )
    assert (
        c.to_cfg().strip()
        == "[inet_http_server]\nport=*:9001\n\n[supervisord]\nlogfile=/tmp/supervisor-runner-test/supervisord.log\npidfile=/tmp/supervisor-runner-test/supervisord.pid\nnodaemon=false\nidentifier=supervisor\n\n[supervisorctl]\nserverurl=http://localhost:9001/\n\n[program:test]\ncommand=echo test\nautostart=false\nstartsecs=1\nautorestart=false\nexitcodes=0\nstopsignal=TERM\nstopwaitsecs=30\ndirectory=/tmp/supervisor-runner-test/test\n\n[rpcinterface:supervisor]\nsupervisor.rpcinterface_factory=supervisor.rpcinterface:make_main_rpcinterface"
    )
