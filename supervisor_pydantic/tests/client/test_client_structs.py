from datetime import UTC, datetime

from supervisor_pydantic.client import ProcessInfo, ProcessState


def _gen() -> ProcessInfo:
    return ProcessInfo(
        name="test",
        group="test",
        state=ProcessState.UNKNOWN,
        description="",
        start=datetime.now(UTC),
        stop=datetime.now(UTC),
        now=datetime.now(UTC),
        spawner="",
        exitstatus=0,
        logfile="",
        stdout_logfile="",
        stderr_logfile="",
        pid=0,
    )


def test_ok():
    x = _gen()
    x.state = ProcessState.RUNNING
    assert x.ok()
    x.state = ProcessState.EXITED
    x.exitstatus = 0
    assert x.ok()
