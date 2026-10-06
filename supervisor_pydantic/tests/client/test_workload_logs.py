import sys
from pathlib import Path
from shlex import quote
from time import monotonic, sleep

import pytest

from supervisor_pydantic import (
    EventListenerConfiguration,
    GroupConfiguration,
    ProcessState,
    SupervisorConvenienceConfiguration,
    SupervisorRemoteXMLRPCClient,
)
from supervisor_pydantic.convenience import check_programs, kill_supervisor, remove_supervisor_config, restart_programs, start_programs, stop_programs
from supervisor_pydantic.tests.conftest import _supervisord_available, _wait_for_server_ready


@pytest.fixture
def workload_instance(tmp_path, open_port):
    if not _supervisord_available():
        pytest.skip("supervisord is not installed")
    program = tmp_path / "workload.py"
    program.write_text("import sys, time\nprint('café € 😀', flush=True)\nprint('erreur €', file=sys.stderr, flush=True)\ntime.sleep(0.2)\n")
    listener = tmp_path / "listener.py"
    listener.write_text("from supervisor import childutils\nwhile True:\n    childutils.listener.wait()\n    childutils.listener.ok()\n")
    cfg = SupervisorConvenienceConfiguration(
        working_dir=tmp_path,
        port=f"127.0.0.1:{open_port}",
        startsecs=0,
        command_timeout=5,
        program={
            "batch": {
                "command": f"{quote(sys.executable)} {quote(str(program))}",
                "numprocs": 2,
                "process_name": "%(program_name)s_%(process_num)02d",
            },
            "other": {"command": f"{quote(sys.executable)} {quote(str(program))}"},
        },
        group={"jobs": GroupConfiguration(programs=["batch", "other"])},
        eventlistener={
            "events": EventListenerConfiguration(
                command=f"{quote(sys.executable)} {quote(str(listener))}",
                events=["PROCESS_STATE"],
                autostart=True,
                startsecs=0,
                stdout_logfile=tmp_path / "listener-output.log",
                stderr_logfile=tmp_path / "listener-error.log",
            )
        },
    )
    cfg.program["batch"].stdout_logfile = tmp_path / "batch" / "output_%(process_num)02d.log"
    cfg.program["batch"].stderr_logfile = tmp_path / "batch" / "error_%(process_num)02d.log"
    cfg.write()
    cfg.start(daemon=True)
    try:
        assert _wait_for_server_ready(open_port), "Supervisor XML-RPC server did not start"
        yield cfg
    finally:
        cfg.stop()
        deadline = monotonic() + 5
        while cfg.running() and monotonic() < deadline:
            sleep(0.1)
        if cfg.running():
            cfg.kill()


def test_finite_workloads_finish_with_running_listener(workload_instance):
    cfg = workload_instance
    client = SupervisorRemoteXMLRPCClient(cfg)
    assert start_programs(cfg, _exit=False)
    deadline = monotonic() + 5
    while monotonic() < deadline and not check_programs(cfg, check_done=True, _exit=False):
        sleep(0.1)
    assert check_programs(cfg, check_done=True, _exit=False)
    assert client._getProcessInfoInternal("events").state == ProcessState.RUNNING
    assert {process.name for process in client.getProgramProcessInfo()} == {"batch_00", "batch_01", "other"}
    assert stop_programs(cfg, _exit=False)
    assert client._getProcessInfoInternal("events").state == ProcessState.RUNNING


def test_stop_running_workloads_preserves_listener(workload_instance):
    cfg = workload_instance
    (cfg.working_dir / "workload.py").write_text("import time\ntime.sleep(60)\n")
    client = SupervisorRemoteXMLRPCClient(cfg)
    client.startAllProcesses()
    assert all(process.running() for process in client.getProgramProcessInfo())

    client.stopAllProcesses()

    assert all(process.stopped() for process in client.getProgramProcessInfo())
    assert client._getProcessInfoInternal("events").state == ProcessState.RUNNING


def test_restart_api_returns_success_and_preserves_listener(workload_instance):
    cfg = workload_instance
    (cfg.working_dir / "workload.py").write_text("import time\ntime.sleep(60)\n")
    assert start_programs(cfg, _exit=False)

    assert restart_programs(cfg, force=True, _exit=False)

    client = SupervisorRemoteXMLRPCClient(cfg)
    assert all(process.running() for process in client.getProgramProcessInfo())
    assert client._getProcessInfoInternal("events").state == ProcessState.RUNNING


@pytest.mark.parametrize("channel, expected", [("stdout", "café € 😀\n"), ("stderr", "erreur €\n")])
def test_live_unicode_log_cursors_and_truncation(workload_instance, channel, expected):
    client = SupervisorRemoteXMLRPCClient(workload_instance)
    client.startAllProcesses()
    deadline = monotonic() + 5
    while monotonic() < deadline and not all(process.done() for process in client.getProgramProcessInfo()):
        sleep(0.1)
    offset = 0
    text = ""
    for _ in range(len(expected)):
        chunk = client.readProcessLogChunk("jobs:batch_00", channel, offset=offset, length=1)
        offset = chunk.offset
        text += chunk.text
    assert text == expected
    assert offset == len(expected.encode("utf-8"))
    assert client.readProcessLogChunk("jobs:batch_00", channel, offset=offset).text == ""
    process = client.getProcessInfo("jobs:batch_00")
    logfile = getattr(process, f"{channel}_logfile")
    Path(logfile).write_text("new\n")
    chunk = client.readProcessLogChunk("jobs:batch_00", channel, offset=offset)
    assert chunk.truncated
    assert chunk.text == "new\n"
    assert chunk.offset == 4


def test_live_newline_normalization_keeps_byte_cursor(workload_instance):
    client = SupervisorRemoteXMLRPCClient(workload_instance)
    client.startAllProcesses()
    deadline = monotonic() + 5
    while monotonic() < deadline and not all(process.done() for process in client.getProgramProcessInfo()):
        sleep(0.1)
    assert all(process.done() for process in client.getProgramProcessInfo())
    logfile = Path(client.getProcessInfo("jobs:batch_00").stdout_logfile)
    logfile.write_bytes(b"CR\r\n")

    chunk = client.readProcessLogChunk("jobs:batch_00", "stdout", length=4)

    assert chunk.text == "CR\n"
    assert chunk.offset == 4
    assert client.readProcessLogChunk("jobs:batch_00", "stdout", offset=chunk.offset).text == ""


@pytest.mark.parametrize("force_kill", [False, True])
def test_live_cleanup_returns_success(workload_instance, force_kill):
    cfg = workload_instance
    if force_kill:
        assert kill_supervisor(cfg, _exit=False)
        assert not cfg.running()
    cfg.command_timeout = 4
    assert remove_supervisor_config(cfg, _exit=False)
    assert not cfg.working_dir.exists()
