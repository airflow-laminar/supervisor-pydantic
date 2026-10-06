from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock, call
from xmlrpc.client import Fault, ProtocolError

import pytest

from supervisor_pydantic import GroupConfiguration, ProcessInfo, ProgramConfiguration, SupervisorRemoteXMLRPCClient


def client():
    value = SupervisorRemoteXMLRPCClient.__new__(SupervisorRemoteXMLRPCClient)
    value._cfg = SimpleNamespace(program={"batch": ProgramConfiguration(command="true")}, group=None, fcgiprogram=None)
    value._client = Mock()
    return value


def info(name, group=None, state="RUNNING"):
    return ProcessInfo(
        name=name,
        group=group or name,
        state=state,
        description="",
        start=datetime.now(UTC),
        stop=datetime.fromtimestamp(0, UTC),
        now=datetime.now(UTC),
        exitstatus=0,
        logfile="",
        stdout_logfile="",
        stderr_logfile="",
        pid=1,
    )


@pytest.mark.parametrize("channel", ["stdout", "stderr"])
def test_incremental_read_uses_byte_offset_without_replaying_tail(channel):
    value = client()
    tail = getattr(value._client.supervisor, f"tailProcess{channel.title()}Log")
    read = getattr(value._client.supervisor, f"readProcess{channel.title()}Log")
    tail.return_value = ["", 5, False]
    read.return_value = "café"

    chunk = value.readProcessLogChunk("batch", channel, length=5)
    assert chunk.text == "café"
    assert chunk.offset == 5
    assert not chunk.truncated
    assert value.readProcessLogChunk("batch", channel, offset=chunk.offset).text == ""
    read.assert_called_once_with("batch", 0, 5)
    assert tail.call_args_list == [call("batch", 0, 0), call("batch", 0, 0)]


def test_log_truncation_resets_cursor():
    value = client()
    value._client.supervisor.tailProcessStdoutLog.return_value = ["", 3, False]
    value._client.supervisor.readProcessStdoutLog.return_value = "new"

    chunk = value.readProcessLogChunk("batch", "stdout", offset=30)

    assert chunk.text == "new"
    assert chunk.offset == 3
    assert chunk.truncated
    value._client.supervisor.readProcessStdoutLog.assert_called_once_with("batch", 0, 3)


def test_chunk_boundary_completes_utf8_character():
    value = client()
    value._client.supervisor.tailProcessStdoutLog.return_value = ["", 3, False]
    value._client.supervisor.readProcessStdoutLog.side_effect = [
        Fault(1, "UnicodeDecodeError: partial character"),
        Fault(1, "UnicodeDecodeError: partial character"),
        "€",
    ]

    chunk = value.readProcessLogChunk("batch", "stdout", length=1)

    assert chunk.text == "€"
    assert chunk.offset == 3
    assert value._client.supervisor.readProcessStdoutLog.call_args_list == [call("batch", 0, 1), call("batch", 0, 2), call("batch", 0, 3)]


def test_unrelated_rpc_fault_is_not_retried():
    value = client()
    value._client.supervisor.tailProcessStdoutLog.return_value = ["", 3, False]
    value._client.supervisor.readProcessStdoutLog.side_effect = Fault(70, "NO_FILE")

    with pytest.raises(Fault, match="NO_FILE"):
        value.readProcessLogChunk("batch", "stdout")
    assert value._client.supervisor.readProcessStdoutLog.call_count == 1


def test_utf8_boundary_http_error_completes_character():
    value = client()
    value._client.supervisor.tailProcessStdoutLog.return_value = ["", 2, False]
    value._client.supervisor.readProcessStdoutLog.side_effect = [ProtocolError("localhost", 500, "Internal Server Error", {}), "é"]

    chunk = value.readProcessLogChunk("batch", "stdout", length=1)

    assert chunk.text == "é"
    assert chunk.offset == 2


@pytest.mark.parametrize("status, expected_calls", [(403, 1), (500, 4)])
def test_unrecoverable_http_error_propagates(status, expected_calls):
    value = client()
    value._client.supervisor.tailProcessStdoutLog.return_value = ["", 8, False]
    value._client.supervisor.readProcessStdoutLog.side_effect = ProtocolError("localhost", status, "Server error", {})

    with pytest.raises(ProtocolError):
        value.readProcessLogChunk("batch", "stdout", length=1)
    assert value._client.supervisor.readProcessStdoutLog.call_count == expected_calls


@pytest.mark.parametrize("options", [{"channel": "other"}, {"channel": "stdout", "offset": -1}, {"channel": "stdout", "length": 0}])
def test_invalid_log_read(options):
    with pytest.raises(ValueError):
        client().readProcessLogChunk("batch", **options)


def test_listener_is_excluded_from_workload_status():
    value = client()
    value.getAllProcessInfo = Mock(return_value=[info("batch"), info("events")])

    assert [process.name for process in value.getProgramProcessInfo()] == ["batch"]


def test_grouped_and_multiple_processes_are_selected():
    value = client()
    value._cfg.program = {"batch": ProgramConfiguration(command="true"), "worker": ProgramConfiguration(command="true", numprocs=2)}
    value._cfg.group = {"jobs": GroupConfiguration(programs=["batch"])}
    value.getAllProcessInfo = Mock(return_value=[info("batch", "jobs"), info("worker_0", "worker"), info("worker_1", "worker"), info("events")])

    assert [process.name for process in value.getProgramProcessInfo()] == ["batch", "worker_0", "worker_1"]


def test_missing_workload_group_is_not_healthy():
    value = client()
    value.getAllProcessInfo = Mock(return_value=[info("events")])

    with pytest.raises(RuntimeError, match="missing configured processes in program groups: batch"):
        value.getProgramProcessInfo()


@pytest.mark.parametrize("grouped", [False, True])
def test_missing_process_in_present_group_is_not_healthy(grouped):
    value = client()
    value._cfg.program["batch"].numprocs = 2
    group = "batch"
    if grouped:
        value._cfg.group = {"jobs": GroupConfiguration(programs=["batch"])}
        group = "jobs"
    value.getAllProcessInfo = Mock(return_value=[info("batch_0", group)])

    with pytest.raises(RuntimeError, match=f"missing configured processes in program groups: {group}"):
        value.getProgramProcessInfo()


def test_missing_member_of_heterogeneous_group_is_not_healthy():
    value = client()
    value._cfg.program["worker"] = ProgramConfiguration(command="true")
    value._cfg.group = {"jobs": GroupConfiguration(programs=["batch", "worker"])}
    value.getAllProcessInfo = Mock(return_value=[info("batch", "jobs")])

    with pytest.raises(RuntimeError, match="missing configured processes in program groups: jobs"):
        value.getProgramProcessInfo()


def test_program_stop_preserves_event_listener():
    value = client()
    value.getAllProcessInfo = Mock(return_value=[info("batch"), info("events")])
    value._client.supervisor.getProcessInfo.return_value = info("batch").model_dump()

    value.stopAllProcesses()

    value._client.supervisor.stopProcessGroup.assert_called_once_with("batch")
    value._client.supervisor.stopAllProcesses.assert_not_called()


def test_program_start_preserves_event_listener():
    value = client()
    value.getAllProcessInfo = Mock(return_value=[info("batch"), info("events")])
    value._client.supervisor.getProcessInfo.return_value = info("batch").model_dump()

    value.startAllProcesses()

    value._client.supervisor.startProcessGroup.assert_called_once_with("batch")
    value._client.supervisor.startAllProcesses.assert_not_called()


def test_group_commands_preserve_priorities_and_process_names():
    value = client()
    value._cfg.program = {
        "high": ProgramConfiguration(command="true", priority=1),
        "low": ProgramConfiguration(command="true", priority=900),
        "batch": ProgramConfiguration(command="true", numprocs=2),
        "peer": ProgramConfiguration(command="true"),
        "default": ProgramConfiguration(command="true"),
    }
    value._cfg.group = {"jobs": GroupConfiguration(programs=["batch", "peer"], priority=10)}
    processes = [
        info("high"),
        info("low"),
        info("custom_0", "jobs"),
        info("custom_1", "jobs"),
        info("peer", "jobs"),
        info("default"),
        info("events"),
    ]
    value.getAllProcessInfo = Mock(return_value=processes)

    result = value.startAllProcesses()
    assert set(result) == {"high", "low", "jobs:custom_0", "jobs:custom_1", "jobs:peer", "default"}
    assert value._client.supervisor.startProcessGroup.call_args_list == [call("high"), call("jobs"), call("low"), call("default")]
    value.stopAllProcesses()
    assert value._client.supervisor.stopProcessGroup.call_args_list == [call("default"), call("low"), call("jobs"), call("high")]
