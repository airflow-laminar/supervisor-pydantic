import socket
from tempfile import NamedTemporaryFile, TemporaryDirectory
from time import sleep
from typing import Iterator

from pytest import fixture

from supervisor_pydantic import ConvenienceConfiguration, ProgramConfiguration, SupervisorConvenienceConfiguration


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
            convenience=ConvenienceConfiguration(port=f"*:{open_port}"),
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
            convenience=ConvenienceConfiguration(port=f"*:{permissioned_open_port}", username="user1", password="testpassword1"),
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
    cfg = supervisor_convenience_configuration
    cfg.write()
    cfg.start(daemon=False)
    for _ in range(5):
        if not cfg.running():
            sleep(1)
    yield cfg
    cfg.kill()


@fixture(scope="module")
def permissioned_supervisor_instance(
    permissioned_supervisor_convenience_configuration: SupervisorConvenienceConfiguration,
) -> Iterator[SupervisorConvenienceConfiguration]:
    cfg = permissioned_supervisor_convenience_configuration
    cfg.write()
    cfg.start(daemon=False)
    for _ in range(5):
        if not cfg.running():
            sleep(1)
    yield cfg
    cfg.kill()
