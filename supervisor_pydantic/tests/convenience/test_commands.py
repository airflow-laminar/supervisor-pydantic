import shutil
import subprocess
from subprocess import check_call
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest
from typer import Exit

from supervisor_pydantic import ProgramConfiguration, SupervisorConvenienceConfiguration
from supervisor_pydantic.convenience.commands import (
    _check_exists,
    _check_running,
    _check_same,
    _load_or_pass,
    _raise_or_exit,
    _wait_or_while,
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
