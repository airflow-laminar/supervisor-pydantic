import shutil
import socket
import subprocess
from tempfile import NamedTemporaryFile, TemporaryDirectory
from time import sleep
from typing import Iterator

import pytest
from pytest import fixture

from supervisor_pydantic import ProgramConfiguration, SupervisorConvenienceConfiguration


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


def _wait_for_server_ready(port: int, timeout: int = 10) -> bool:
    """Wait until the server is accepting connections on the given port."""
    for _ in range(timeout * 10):  # Check every 100ms
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            s.connect(("127.0.0.1", port))
            s.close()
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            sleep(0.1)
    return False


def _get_port_from_config(cfg: SupervisorConvenienceConfiguration) -> int:
    """Extract the port number from the config's port string (e.g., '*:9001' -> 9001)."""
    port_str = cfg.port
    if ":" in port_str:
        return int(port_str.split(":")[-1])
    return int(port_str)


@fixture(scope="module")
def open_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


@fixture(scope="module")
def permissioned_open_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


@fixture(scope="module")
def supervisor_convenience_configuration(open_port: int) -> Iterator[SupervisorConvenienceConfiguration]:
    with TemporaryDirectory() as td:
        cfg = SupervisorConvenienceConfiguration(
            port=f"*:{open_port}",
            working_dir=td,
            program={
                "test": ProgramConfiguration(
                    command="bash -c 'sleep 1; exit 1'",
                )
            },
        )
        yield cfg


@fixture(scope="module")
def permissioned_supervisor_convenience_configuration(
    permissioned_open_port: int,
) -> Iterator[SupervisorConvenienceConfiguration]:
    with NamedTemporaryFile("w", suffix=".cfg") as tf:
        cfg = SupervisorConvenienceConfiguration(
            port=f"*:{permissioned_open_port}",
            username="user1",
            password="testpassword1",
            path=tf.name,
            program={
                "test": ProgramConfiguration(
                    command="bash -c 'sleep 1; exit 1'",
                )
            },
        )
        yield cfg


@fixture(scope="module")
def supervisor_instance(
    supervisor_convenience_configuration: SupervisorConvenienceConfiguration,
) -> Iterator[SupervisorConvenienceConfiguration]:
    if not _supervisord_available():
        pytest.skip("supervisord is not installed")
    cfg = supervisor_convenience_configuration
    cfg.write()
    cfg.start(daemon=False)
    # Wait for process to start
    for _ in range(10):
        if cfg.running():
            break
        sleep(0.5)
    # Wait for HTTP server to accept connections
    port = _get_port_from_config(cfg)
    if not _wait_for_server_ready(port, timeout=10):
        pytest.skip(f"Supervisor HTTP server not ready on port {port}")
    yield cfg
    cfg.kill()


@fixture(scope="module")
def permissioned_supervisor_instance(
    permissioned_supervisor_convenience_configuration: SupervisorConvenienceConfiguration,
) -> Iterator[SupervisorConvenienceConfiguration]:
    if not _supervisord_available():
        pytest.skip("supervisord is not installed")
    cfg = permissioned_supervisor_convenience_configuration
    cfg.write()
    cfg.start(daemon=False)
    # Wait for process to start
    for _ in range(10):
        if cfg.running():
            break
        sleep(0.5)
    # Wait for HTTP server to accept connections
    port = _get_port_from_config(cfg)
    if not _wait_for_server_ready(port, timeout=10):
        pytest.skip(f"Supervisor HTTP server not ready on port {port}")
    yield cfg
    cfg.kill()
