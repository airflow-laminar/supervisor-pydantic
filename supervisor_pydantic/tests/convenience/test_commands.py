import shutil
import socket
import subprocess
from pathlib import Path
from subprocess import check_call
from tempfile import TemporaryDirectory
from time import monotonic, sleep
from typing import Any
from unittest.mock import Mock, patch
from xmlrpc.client import Fault

import pytest
from typer import Exit

from supervisor_pydantic import ProgramConfiguration, SupervisorConvenienceConfiguration, SupervisorRemoteXMLRPCClient
from supervisor_pydantic.convenience.commands import (
    _check_exists,
    _check_running,
    _check_same,
    _load_or_pass,
    _raise_or_exit,
    _wait_or_while,
    kill_supervisor,
    remove_supervisor_config,
    restart_programs,
    start_supervisor,
    stop_supervisor,
    write_supervisor_config,
)


def _supervisord_available() -> bool:
    """Check if supervisord binary is available and functional."""
    if not shutil.which("supervisord"):
        return False
    try:
        result = subprocess.run(
            ["supervisord", "--version"],
            capture_output=True,
            check=False,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
        return False


def test_command():
    assert check_call(["_supervisor_convenience", "--help"]) == 0


def test_write(supervisor_convenience_configuration: SupervisorConvenienceConfiguration):
    json = supervisor_convenience_configuration.model_dump_json(exclude_unset=True)
    assert write_supervisor_config(json, _exit=False)
    assert supervisor_convenience_configuration._pydantic_path.read_text().strip() == json
    supervisor_convenience_configuration.rmdir()


@pytest.mark.skipif(not _supervisord_available(), reason="supervisord is not installed or not functional")
def test_start_stop(supervisor_convenience_configuration: SupervisorConvenienceConfiguration):
    json = supervisor_convenience_configuration.model_dump_json(exclude_unset=True)
    assert write_supervisor_config(json, _exit=False)
    assert supervisor_convenience_configuration._pydantic_path.read_text().strip() == json
    assert start_supervisor(supervisor_convenience_configuration._pydantic_path, _exit=False)
    assert stop_supervisor(supervisor_convenience_configuration._pydantic_path, _exit=False)
    supervisor_convenience_configuration.rmdir()


def test_start_supervisor_with_changed_config_and_stopped_daemon(supervisor_convenience_configuration: SupervisorConvenienceConfiguration):
    supervisor_convenience_configuration._write_self()
    supervisor_convenience_configuration.config_path.write_text("different content")

    with (
        patch("supervisor_pydantic.convenience.commands.SupervisorRemoteXMLRPCClient") as client,
        patch("supervisor_pydantic.convenience.commands.SupervisorConvenienceConfiguration.start") as start,
        patch("supervisor_pydantic.convenience.commands.SupervisorConvenienceConfiguration.running", side_effect=[False, False, True]),
    ):
        assert start_supervisor(supervisor_convenience_configuration, _exit=False)

    client.assert_not_called()
    start.assert_called_once_with(daemon=True)
    assert _check_same(supervisor_convenience_configuration)


def test_start_supervisor_with_changed_config_and_running_daemon(supervisor_convenience_configuration: SupervisorConvenienceConfiguration):
    cfg = supervisor_convenience_configuration.model_copy(deep=True)
    cfg._write_self()
    previous_config = cfg.config_path.read_text()
    cfg.program["test"].command = "echo replacement"

    with (
        patch("supervisor_pydantic.convenience.commands.SupervisorRemoteXMLRPCClient") as client,
        patch("supervisor_pydantic.convenience.commands.SupervisorConvenienceConfiguration.start") as start,
        patch("supervisor_pydantic.convenience.commands.SupervisorConvenienceConfiguration.running", side_effect=[True, False, True]),
        patch("supervisor_pydantic.convenience.commands.stop_supervisor", return_value=True) as stop,
    ):
        stop.side_effect = lambda *args, **kwargs: cfg.config_path.read_text() == previous_config
        assert start_supervisor(cfg, _exit=False)

    stop.assert_called_once()
    client.assert_not_called()
    start.assert_called_once_with(daemon=True)
    assert _check_same(cfg)


@pytest.mark.parametrize("command", [write_supervisor_config, start_supervisor])
@pytest.mark.parametrize("exit_mode", [False, True])
def test_changed_config_is_not_written_if_shutdown_fails(supervisor_convenience_configuration, command, exit_mode):
    cfg = supervisor_convenience_configuration.model_copy(deep=True)
    cfg._write_self()
    old_config = cfg.config_path.read_text()
    old_json = cfg._pydantic_path.read_text()
    cfg.port = "127.0.0.1:9002"
    cfg.inet_http_server.port = cfg.port
    with (
        patch("supervisor_pydantic.convenience.commands.SupervisorConvenienceConfiguration.running", return_value=True),
        patch("supervisor_pydantic.convenience.commands.stop_supervisor", return_value=False) as stop,
        patch("supervisor_pydantic.convenience.commands.SupervisorConvenienceConfiguration.start") as start,
    ):
        if exit_mode:
            with pytest.raises(Exit) as failure:
                command(cfg, _exit=True)
            assert failure.value.exit_code == 1
        else:
            assert command(cfg, _exit=False) is False
    stop.assert_called_once()
    start.assert_not_called()
    assert cfg.config_path.read_text() == old_config
    assert cfg._pydantic_path.read_text() == old_json


@pytest.mark.parametrize("use_here", [False, True])
def test_configure_stops_old_daemon_before_replacing_config(supervisor_convenience_configuration, use_here):
    cfg = supervisor_convenience_configuration.model_copy(deep=True)
    if use_here:
        cfg.supervisord.pidfile = Path("%(here)s/supervisord.pid")
    cfg._write_self()
    old_config = cfg.config_path.read_text()
    old_pidfile = cfg.config_path.parent / "supervisord.pid" if use_here else cfg.supervisord.pidfile
    cfg.supervisord.pidfile = cfg.working_dir / "replacement.pid"

    def stop(previous, _exit):
        assert not _exit
        assert previous.supervisord.pidfile == old_pidfile
        assert cfg.config_path.read_text() == old_config
        return True

    with (
        patch("supervisor_pydantic.convenience.commands.SupervisorConvenienceConfiguration.running", return_value=True),
        patch("supervisor_pydantic.convenience.commands.stop_supervisor", side_effect=stop) as stopped,
    ):
        assert write_supervisor_config(cfg.model_dump_json(), _exit=False)
    stopped.assert_called_once()
    assert _check_same(cfg)


@pytest.mark.parametrize("command", [write_supervisor_config, start_supervisor])
def test_unchanged_running_config_does_not_stop_daemon(supervisor_convenience_configuration, command):
    cfg = supervisor_convenience_configuration.model_copy(deep=True)
    cfg._write_self()
    with (
        patch("supervisor_pydantic.convenience.commands.SupervisorConvenienceConfiguration.running", return_value=True),
        patch("supervisor_pydantic.convenience.commands.stop_supervisor") as stop,
        patch("supervisor_pydantic.convenience.commands.SupervisorConvenienceConfiguration.start") as start,
    ):
        assert command(cfg, _exit=False)
    stop.assert_not_called()
    start.assert_not_called()


@pytest.mark.skipif(not _supervisord_available(), reason="supervisord is not installed or not functional")
@pytest.mark.parametrize("configure_first", [False, True])
@pytest.mark.parametrize("change", ["port", "credentials", "program", "pidfile"])
def test_live_reconfiguration_applies_changed_settings(tmp_path, open_port, change, configure_first):
    values: dict[str, Any] = {
        "working_dir": tmp_path,
        "port": f"127.0.0.1:{open_port}",
        "username": "test",
        "password": "before",
        "program": {"test": {"command": "sleep 60"}},
        "command_timeout": 5,
        "startsecs": 0,
        "stopwaitsecs": 1,
    }
    old = SupervisorConvenienceConfiguration(**values)
    old._write_self()
    client = SupervisorRemoteXMLRPCClient(old)
    process = subprocess.Popen(
        [shutil.which("supervisord"), "-n", "-c", str(old.config_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    new = old
    try:
        deadline = monotonic() + 5
        while True:
            try:
                client.getState()
                break
            except ConnectionRefusedError:
                assert monotonic() < deadline, "Supervisor did not open its XML-RPC endpoint"
                sleep(0.05)
        old_pid = process.pid
        client.startAllProcesses()
        assert write_supervisor_config(old.model_dump_json(), _exit=False)
        assert start_supervisor(old, _exit=False)
        assert process.poll() is None
        if change == "port":
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                values["port"] = f"127.0.0.1:{sock.getsockname()[1]}"
        elif change == "credentials":
            values["username"] = "updated"
            values["password"] = "after"
        elif change == "program":
            values["program"] = {"replacement": {"command": "sleep 60"}}
        else:
            values["supervisord"] = {"pidfile": tmp_path / "replacement.pid"}
        new = SupervisorConvenienceConfiguration(**values)
        if configure_first:
            assert write_supervisor_config(new.model_dump_json(), _exit=False)
            assert not old.running()
            assert start_supervisor(new._pydantic_path, _exit=False)
        else:
            assert start_supervisor(new, _exit=False)
        process.wait(timeout=5)
        assert new.running()
        assert int(new.supervisord.pidfile.read_text()) != old_pid
        client = SupervisorRemoteXMLRPCClient(new)
        assert {info.name for info in client.getProgramProcessInfo()} == set(new.program)
        assert _check_same(new)
    finally:
        if new.running():
            stop_supervisor(new, _exit=False)
        if old.running():
            stop_supervisor(old, _exit=False)
        if process.poll() is None:
            process.terminate()
        process.wait(timeout=5)


# Unit tests for helper functions


def test_raise_or_exit_returns_value():
    """Test _raise_or_exit returns the value when exit=False."""
    assert _raise_or_exit(True, exit=False) is True
    assert _raise_or_exit(False, exit=False) is False


def test_raise_or_exit_raises_exit():
    """Test _raise_or_exit raises Exit when exit=True."""
    with pytest.raises(Exit):
        _raise_or_exit(True, exit=True)
    with pytest.raises(Exit):
        _raise_or_exit(False, exit=True)


def test_wait_or_while_until_immediate():
    """Test _wait_or_while returns True immediately when until() is True."""
    result = _wait_or_while(until=lambda: True, timeout=1)
    assert result is True


def test_wait_or_while_unless_immediate():
    """Test _wait_or_while returns False when unless() is True."""
    result = _wait_or_while(until=lambda: False, unless=lambda: True, timeout=1)
    assert result is False


def test_wait_or_while_timeout():
    """Test _wait_or_while returns False on timeout."""
    call_count = 0

    def always_false():
        nonlocal call_count
        call_count += 1
        return False

    result = _wait_or_while(until=always_false, timeout=2)
    assert result is False
    assert call_count == 2  # Called once per second


def test_load_or_pass_with_string():
    """Test _load_or_pass with a JSON string."""
    with TemporaryDirectory() as td:
        cfg = SupervisorConvenienceConfiguration(
            port="*:9001",
            working_dir=td,
            program={"test": ProgramConfiguration(command="echo hello")},
        )
        json_str = cfg.model_dump_json()
        result = _load_or_pass(json_str)
        assert isinstance(result, SupervisorConvenienceConfiguration)
        assert result.port == "*:9001"


def test_load_or_pass_with_config_object():
    """Test _load_or_pass passes through a config object."""
    with TemporaryDirectory() as td:
        cfg = SupervisorConvenienceConfiguration(
            port="*:9001",
            working_dir=td,
            program={"test": ProgramConfiguration(command="echo hello")},
        )
        result = _load_or_pass(cfg)
        assert result is cfg


def test_load_or_pass_with_invalid_type():
    """Test _load_or_pass raises NotImplementedError for invalid types."""
    with pytest.raises(NotImplementedError):
        _load_or_pass(12345)  # type: ignore


def test_check_exists_true():
    """Test _check_exists returns True when both paths exist."""
    with TemporaryDirectory() as td:
        cfg = SupervisorConvenienceConfiguration(
            port="*:9001",
            working_dir=td,
            program={"test": ProgramConfiguration(command="echo hello")},
        )
        cfg._write_self()
        assert _check_exists(cfg) is True


def test_check_exists_false():
    """Test _check_exists returns False when paths don't exist."""
    with TemporaryDirectory() as td:
        cfg = SupervisorConvenienceConfiguration(
            port="*:9001",
            working_dir=td,
            program={"test": ProgramConfiguration(command="echo hello")},
        )
        # Don't write the config
        assert _check_exists(cfg) is False


def test_check_same_no_file():
    """Test _check_same returns True when no file exists."""
    with TemporaryDirectory() as td:
        cfg = SupervisorConvenienceConfiguration(
            port="*:9001",
            working_dir=td,
            program={"test": ProgramConfiguration(command="echo hello")},
        )
        # Don't write - should return True (can write it)
        assert _check_same(cfg) is True


def test_check_same_matching_file():
    """Test _check_same returns True when file matches."""
    with TemporaryDirectory() as td:
        cfg = SupervisorConvenienceConfiguration(
            port="*:9001",
            working_dir=td,
            program={"test": ProgramConfiguration(command="echo hello")},
        )
        cfg._write_self()
        assert _check_same(cfg) is True


def test_check_same_different_file():
    """Test _check_same returns False when file differs."""
    with TemporaryDirectory() as td:
        cfg = SupervisorConvenienceConfiguration(
            port="*:9001",
            working_dir=td,
            program={"test": ProgramConfiguration(command="echo hello")},
        )
        cfg._write_self()
        # Modify the config file directly to simulate a different config
        cfg.config_path.write_text("different content")
        assert _check_same(cfg) is False


def test_check_running_not_running():
    """Test _check_running returns False when supervisor is not running."""
    with TemporaryDirectory() as td:
        cfg = SupervisorConvenienceConfiguration(
            port="*:9001",
            working_dir=td,
            program={"test": ProgramConfiguration(command="echo hello")},
        )
        cfg._write_self()
        # Not started, so not running
        assert _check_running(cfg) is False


def test_check_running_with_mock():
    """Test _check_running returns True when supervisor is running."""
    with TemporaryDirectory() as td:
        cfg = SupervisorConvenienceConfiguration(
            port="*:9001",
            working_dir=td,
            program={"test": ProgramConfiguration(command="echo hello")},
        )
        cfg._write_self()

        with patch(
            "supervisor_pydantic.convenience.commands.SupervisorConvenienceConfiguration.running",
            return_value=True,
        ):
            assert _check_running(cfg) is True


def test_load_or_pass_with_path():
    """Test _load_or_pass with a Path object."""

    with TemporaryDirectory() as td:
        cfg = SupervisorConvenienceConfiguration(
            port="*:9001",
            working_dir=td,
            program={"test": ProgramConfiguration(command="echo hello")},
        )
        # Write the pydantic JSON config file
        cfg._write_self()
        json_path = cfg._pydantic_path

        result = _load_or_pass(json_path)
        assert isinstance(result, SupervisorConvenienceConfiguration)


def test_write_supervisor_config_different_file():
    """Test write_supervisor_config when file already exists with different content."""
    with TemporaryDirectory() as td:
        cfg = SupervisorConvenienceConfiguration(
            port="*:9001",
            working_dir=td,
            program={"test": ProgramConfiguration(command="echo hello")},
        )
        # Write a different config first
        cfg._write_self()
        cfg.config_path.write_text("different content")

        # Now write the correct config
        json = cfg.model_dump_json()
        result = write_supervisor_config(json, _exit=False)
        assert result is True
        # The config should now match
        assert _check_same(cfg) is True


def test_main_creates_app():
    """Test that main function creates a Typer app with correct commands."""
    from typer import Typer

    from supervisor_pydantic.convenience.commands import _add_to_typer

    # Test _add_to_typer works
    app = Typer()
    _add_to_typer(app, "configure-supervisor", write_supervisor_config)

    # Verify the command was added
    assert any(cmd.name == "configure-supervisor" for cmd in app.registered_commands)


@pytest.mark.parametrize("stopped", [False, True])
def test_kill_reports_whether_supervisor_stopped(stopped):
    cfg = Mock(command_timeout=1)
    cfg.running.return_value = not stopped
    with (
        patch("supervisor_pydantic.convenience.commands._load_or_pass", return_value=cfg),
        patch("supervisor_pydantic.convenience.commands.stop_programs", return_value=True),
        patch("supervisor_pydantic.convenience.commands.sleep"),
    ):
        assert kill_supervisor(cfg, _exit=False) is stopped
    cfg.kill.assert_called_once_with()


@pytest.mark.parametrize("stop_succeeds, kill_succeeds", [(True, False), (False, True), (False, False)])
def test_remove_requires_successful_shutdown(stop_succeeds, kill_succeeds):
    cfg = Mock(command_timeout=1)
    with (
        patch("supervisor_pydantic.convenience.commands._load_or_pass", return_value=cfg),
        patch("supervisor_pydantic.convenience.commands.stop_supervisor", return_value=stop_succeeds),
        patch("supervisor_pydantic.convenience.commands.kill_supervisor", return_value=kill_succeeds) as kill,
        patch("supervisor_pydantic.convenience.commands.sleep"),
    ):
        assert remove_supervisor_config(cfg, _exit=False) is (stop_succeeds or kill_succeeds)
    if stop_succeeds:
        kill.assert_not_called()
    else:
        kill.assert_called_once_with(cfg, _exit=False)
    if stop_succeeds or kill_succeeds:
        cfg.rmdir.assert_called_once_with()
    else:
        cfg.rmdir.assert_not_called()


@pytest.mark.parametrize("stop_succeeds, start_succeeds", [(True, True), (False, True), (True, False)])
def test_restart_returns_api_boolean(stop_succeeds, start_succeeds):
    cfg = Mock()
    with (
        patch("supervisor_pydantic.convenience.commands.stop_programs", return_value=stop_succeeds) as stop,
        patch("supervisor_pydantic.convenience.commands.start_programs", return_value=start_succeeds) as start,
    ):
        assert restart_programs(cfg, force=True, _exit=False) is (stop_succeeds and start_succeeds)
    stop.assert_called_once_with(cfg, _exit=False)
    if stop_succeeds:
        start.assert_called_once_with(cfg, _exit=False)
    else:
        start.assert_not_called()


@pytest.mark.parametrize("fault_code", [6, 10])
def test_force_kill_accepts_only_shutdown_rpc_fault(fault_code):
    cfg = Mock(command_timeout=1)
    cfg.running.return_value = False
    with (
        patch("supervisor_pydantic.convenience.commands._load_or_pass", return_value=cfg),
        patch("supervisor_pydantic.convenience.commands.stop_programs", side_effect=Fault(fault_code, "Supervisor error")),
    ):
        if fault_code == 6:
            assert kill_supervisor(cfg, _exit=False)
            cfg.kill.assert_called_once_with()
        else:
            with pytest.raises(Fault):
                kill_supervisor(cfg, _exit=False)
            cfg.kill.assert_not_called()


def test_restart_without_force_does_not_stop_programs():
    cfg = Mock()
    with (
        patch("supervisor_pydantic.convenience.commands.stop_programs") as stop,
        patch("supervisor_pydantic.convenience.commands.start_programs", return_value=True) as start,
    ):
        assert restart_programs(cfg, _exit=False)
    stop.assert_not_called()
    start.assert_called_once_with(cfg, _exit=False)
