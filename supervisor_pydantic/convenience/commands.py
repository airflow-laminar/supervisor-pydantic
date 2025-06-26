from logging import getLogger
from pathlib import Path
from time import sleep
from typing import Callable, Optional, Union

from typer import Argument, Exit, Option, Typer
from typing_extensions import Annotated

from ..client import SupervisorRemoteXMLRPCClient
from ..config import SupervisorConvenienceConfiguration
from .common import SupervisorTaskStep

log = getLogger(__name__)

__all__ = (
    "write_supervisor_config",
    "start_supervisor",
    "start_programs",
    "check_programs",
    "stop_programs",
    "restart_programs",
    "stop_supervisor",
    "kill_supervisor",
    "remove_supervisor_config",
    "main",
)


def _check_exists(cfg: SupervisorConvenienceConfiguration) -> bool:
    log.info(f"Checking for working dir {cfg.working_dir} and config path {cfg.config_path}")
    if cfg.working_dir.exists() and cfg.config_path.exists():
        # its probably already been written
        log.info(f"Working dir {cfg.working_dir} and config path {cfg.config_path} exist")
        return True
    log.info(f"Working dir {cfg.working_dir} and/or config path {cfg.config_path} do not exist")
    return False


def _check_same(cfg: SupervisorConvenienceConfiguration) -> bool:
    log.info("Checking if config file matches")
    if _check_exists(cfg) and cfg.config_path.read_text().strip() == cfg.to_cfg().strip():
        # same file contents
        log.info(f"Config file {cfg.config_path} matches")
        return True
    elif not _check_exists(cfg):
        # no file exists, so we can write it
        log.info(f"Config file {cfg.config_path} does not exist, so we can write it")
        return True
    log.info(f"Config file {cfg.config_path} does not match")
    return False


def _check_running(cfg: SupervisorConvenienceConfiguration) -> bool:
    if _check_same(cfg):
        # check if running
        log.info("Checking if supervisor is running")
        if cfg.running():
            log.info("Supervisor is running")
            return True
        log.info("Supervisor is not running")
    log.info("Supervisor config file does not match, so we can't check if it's running")
    return False


def _wait_or_while(until: Callable, unless: Optional[Callable] = None, timeout: int = 5) -> bool:
    log.info(f"Waiting for {timeout} seconds")
    for _ in range(timeout):
        if until():
            log.info("`until` condition met")
            return True
        if unless and unless():
            log.info("`unless` condition met")
            return False
        sleep(1)
    log.info("Timed out after {timeout} seconds")
    return False


def _raise_or_exit(val: bool, exit: bool):
    if exit:
        raise Exit(int(not val))
    return val


def _load_or_pass(cfg: Union[str, SupervisorConvenienceConfiguration]) -> SupervisorConvenienceConfiguration:
    if isinstance(cfg, Path):
        cfg = SupervisorConvenienceConfiguration.model_validate_json(cfg.read_text())
    if isinstance(cfg, str):
        cfg = SupervisorConvenienceConfiguration.model_validate_json(cfg)
    if not isinstance(cfg, SupervisorConvenienceConfiguration):
        raise NotImplementedError
    return cfg


def write_supervisor_config(cfg_json: str, _exit: Annotated[bool, Argument(hidden=True)] = True):
    """Write a SupervisorConvenienceConfiguration JSON as a supervisor config file

    Args:
        cfg_json (str): JSON string of SupervisorConvenienceConfiguration
    """
    # NOTE: typer does not support union types
    log.info(f"Loading JSON config: {cfg_json}")
    cfg_obj = _load_or_pass(cfg_json)

    if not _check_same(cfg_obj):
        log.critical("Configurations don't match while writing supervisor config. This may lead to zombie supervisors")

    log.info(f"Writing supervisor config to {cfg_obj.config_path}")
    cfg_obj._write_self()

    return _raise_or_exit(True, _exit)


def start_supervisor(
    cfg: Annotated[Path, Option(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True)] = Path(
        "pydantic.json"
    ),
    _exit: Annotated[bool, Argument(hidden=True)] = True,
):
    """Start a supervisor instance using supervisord in background

    Args:
        cfg (Annotated[Path, Option, optional): Path to JSON file of SupervisorConvenienceConfiguration
    """
    # NOTE: typer does not support union types
    cfg_obj = _load_or_pass(cfg)

    if not _check_same(cfg_obj):
        log.critical("Configurations don't match while writing supervisor config. This may lead to zombie supervisors")

        # TODO check if "critical" things are different and restart
        # supervisor if necessary

        # Otherwise just write and reload
        log.info("Writing supervisor config to {cfg_obj.config_path}")
        cfg_obj._write_self()

        log.info("Reloading supervisor config")
        client = SupervisorRemoteXMLRPCClient(cfg=cfg_obj)
        client.reloadConfig()

    if _check_running(cfg_obj):
        log.info("Supervisor is already running")
        return _raise_or_exit(True, _exit)

    log.info("Starting supervisor")
    cfg_obj.start(daemon=True)
    running = _wait_or_while(until=lambda: cfg_obj.running(), timeout=cfg_obj.convenience.command_timeout)
    if not running:
        log.critical(f"Supervisor still not running {cfg_obj.convenience.command_timeout}s after start command!")
        return _raise_or_exit(False, _exit)
    log.info("Supervisor started")
    return _raise_or_exit(True, _exit)


def start_programs(
    cfg: Annotated[Path, Option(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True)] = Path(
        "pydantic.json"
    ),
    restart: bool = False,
    _exit: Annotated[bool, Argument(hidden=True)] = True,
):
    """Start all programs in the supervisor instance

    Args:
        cfg (Annotated[Path, Option, optional): Path to JSON file of SupervisorConvenienceConfiguration
        restart (bool, optional): if true, restart all programs. Defaults to False.
    """
    # NOTE: typer does not support union types
    cfg_obj = _load_or_pass(cfg)

    log.info(f"Initializing client with config: {cfg_obj}")
    client = SupervisorRemoteXMLRPCClient(cfg=cfg_obj)

    if restart:
        # No builtin restart, so stop everything then start again on the next line
        log.info("Stopping all processes before restarting")
        client.stopAllProcesses()

    log.info("Starting all processes")
    ret = client.startAllProcesses()
    log.info(ret)

    _wait_or_while(
        until=lambda: all(_.running() for _ in client.getAllProcessInfo()),
        unless=lambda: any(_.stopped() for _ in client.getAllProcessInfo()),
        timeout=cfg_obj.convenience.command_timeout,
    )
    all_ok = _wait_or_while(
        until=lambda: all(_.ok(ok_exitstatuses=cfg_obj.convenience.exitcodes) for _ in client.getAllProcessInfo()),
        unless=lambda: any(_.bad(ok_exitstatuses=cfg_obj.convenience.exitcodes) for _ in client.getAllProcessInfo()),
        timeout=cfg_obj.convenience.command_timeout,
    )
    if not all_ok:
        log.critical("Not all processes started successfully")
        for r in client.getAllProcessInfo():
            log.info(r.model_dump_json(exclude_unset=True))
        return _raise_or_exit(False, _exit)
    log.info("All processes started")
    return _raise_or_exit(True, _exit)


def check_programs(
    cfg: Annotated[Path, Option(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True)] = Path(
        "pydantic.json"
    ),
    check_running: bool = False,
    check_done: bool = False,
    _exit: Annotated[bool, Argument(hidden=True)] = True,
):
    """Check if programs are in a good state.

    Args:
        cfg (Annotated[Path, Option, optional): Path to JSON file of SupervisorConvenienceConfiguration
        check_running (bool, optional): if true, only return true if they're running
        check_done (bool, optional): if true, only return true if they're done (cleanly)
    """
    # NOTE: typer does not support union types
    cfg_obj = _load_or_pass(cfg)

    log.info(f"Initializing client with config: {cfg_obj}")
    client = SupervisorRemoteXMLRPCClient(cfg=cfg_obj)

    log.info("Checking all processes")
    ret = client.getAllProcessInfo()
    for r in ret:
        log.info(r.model_dump_json(exclude_unset=True))

    ok = False
    if check_running:
        if all(p.running() for p in ret):
            log.info("All processes running")
            ok = True
        else:
            log.warning("Not all processes running")
    elif check_done:
        if all(p.done(ok_exitstatuses=cfg_obj.convenience.exitcodes) for p in ret):
            log.info("All processes done")
            ok = True
        else:
            log.info("Not all processes done")
    else:
        if all(p.ok(ok_exitstatuses=cfg_obj.convenience.exitcodes) for p in ret):
            log.info("All processes ok")
            ok = True
        else:
            log.info("Not all processes ok")
    return _raise_or_exit(ok, _exit)


def stop_programs(
    cfg: Annotated[Path, Option(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True)] = Path(
        "pydantic.json"
    ),
    _exit: Annotated[bool, Argument(hidden=True)] = True,
):
    """Stop all programs in the supervisor instance

    Args:
        cfg (Annotated[Path, Option, optional): Path to JSON file of SupervisorConvenienceConfiguration
    """
    # NOTE: typer does not support union types
    cfg_obj = _load_or_pass(cfg)

    log.info(f"Initializing client with config: {cfg_obj}")
    client = SupervisorRemoteXMLRPCClient(cfg=cfg_obj)

    log.info("Stopping all processes")
    ret = client.stopAllProcesses()
    log.info(ret)

    all_stopped = _wait_or_while(until=lambda: all(_.stopped() for _ in client.getAllProcessInfo()), timeout=cfg_obj.convenience.command_timeout)
    if not all_stopped:
        log.critical("Not all processes stopped successfully")
        for r in client.getAllProcessInfo():
            log.info(r.model_dump_json(exclude_unset=True))
        return _raise_or_exit(False, _exit)
    log.info("All processes stopped")
    return _raise_or_exit(True, _exit)


def restart_programs(
    cfg: Annotated[Path, Option(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True)] = Path(
        "pydantic.json"
    ),
    force: bool = False,
    _exit: Annotated[bool, Argument(hidden=True)] = True,
):
    """Restart all programs in the supervisor instance

    Args:
        cfg (Annotated[Path, Option, optional): Path to JSON file of SupervisorConvenienceConfiguration
        force (bool, optional): if true, force restart. Defaults to False.
    """
    if force:
        log.info("Force restarting all processes")
        if not stop_programs(cfg, False):
            log.warning("Could not stop programs")
            return _raise_or_exit(False, _exit)
    if not start_programs(cfg, False):
        log.warning("Could not start programs")
        return _raise_or_exit(False, _exit)
    return _raise_or_exit(True, _exit)


def stop_supervisor(
    cfg: Annotated[Path, Option(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True)] = Path(
        "pydantic.json"
    ),
    _exit: Annotated[bool, Argument(hidden=True)] = True,
):
    """Stop the supervisor instance

    Args:
        cfg (Annotated[Path, Option, optional): Path to JSON file of SupervisorConvenienceConfiguration
    """
    # NOTE: typer does not support union types
    cfg_obj = _load_or_pass(cfg)

    log.info("Stopping supervisor")
    cfg_obj.stop()

    not_running = _wait_or_while(until=lambda: not cfg_obj.running(), timeout=cfg_obj.convenience.command_timeout)
    if not not_running:
        log.critical(f"Still running {cfg_obj.convenience.command_timeout}s after stop command!")
        return _raise_or_exit(False, _exit)
    return _raise_or_exit(True, _exit)


def kill_supervisor(
    cfg: Annotated[Path, Option(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True)] = Path(
        "pydantic.json"
    ),
    _exit: Annotated[bool, Argument(hidden=True)] = True,
):
    """Kill the supervisor instance with os.kill

    Args:
        cfg (Annotated[Path, Option, optional): Path to JSON file of SupervisorConvenienceConfiguration
    """
    try:
        if not stop_programs(cfg, False):
            log.warning("could not stop programs")
    except ConnectionRefusedError:
        # supervisor already down, continue
        ...

    # NOTE: typer does not support union types
    cfg_obj = _load_or_pass(cfg)
    log.info("Killing supervisor")
    cfg_obj.kill()

    still_running = _wait_or_while(until=lambda: not cfg_obj.running(), timeout=cfg_obj.convenience.command_timeout)
    if still_running:
        log.critical(f"Still running {cfg_obj.convenience.command_timeout}s after kill command!")
        return _raise_or_exit(False, _exit)
    return _raise_or_exit(True, _exit)


def remove_supervisor_config(
    cfg: Annotated[Path, Option(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True)] = Path(
        "pydantic.json"
    ),
    _exit: Annotated[bool, Argument(hidden=True)] = True,
):
    """Remove the supervisor config file and working directory

    Args:
        cfg (Annotated[Path, Option, optional): Path to JSON file of SupervisorConvenienceConfiguration
    """
    # NOTE: typer does not support union types
    cfg_obj = _load_or_pass(cfg)

    log.info("Removing supervisor config")
    still_running = stop_supervisor(cfg_obj, _exit=False)
    if still_running:
        log.critical("Supervisor still running after stop command!")
        still_running = kill_supervisor(cfg_obj, _exit=False)

    if still_running:
        log.critical("Supervisor still running after kill command!")
        return _raise_or_exit(False, _exit)

    log.info(f"Sleeping for {cfg_obj.convenience.command_timeout} seconds")
    sleep(cfg_obj.convenience.command_timeout)

    log.info("Removing supervisor config and folder")
    cfg_obj.rmdir()
    return _raise_or_exit(True, _exit)


def _add_to_typer(app, command: SupervisorTaskStep, foo):
    """Helper function to ensure correct command names"""
    app.command(command)(foo)


def main():
    app = Typer()
    _add_to_typer(app, "configure-supervisor", write_supervisor_config)
    _add_to_typer(app, "start-supervisor", start_supervisor)
    _add_to_typer(app, "start-programs", start_programs)
    _add_to_typer(app, "stop-programs", stop_programs)
    _add_to_typer(app, "check-programs", check_programs)
    _add_to_typer(app, "restart-programs", restart_programs)
    _add_to_typer(app, "stop-supervisor", stop_supervisor)
    _add_to_typer(app, "force-kill", kill_supervisor)
    _add_to_typer(app, "unconfigure-supervisor", remove_supervisor_config)
    app()
