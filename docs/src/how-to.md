# How-to guides

These guides cover configuration loading, process control, and integrations.

## How to load YAML with Hydra

Create `config/worker.yaml`:

```yaml
# @package _global_
working_dir: /var/tmp/worker-supervisor
port: "127.0.0.1:9001"
program:
  worker:
    command: python /opt/jobs/worker.py
    environment:
      MODE: production
```

Load it relative to the calling script:

```python
from supervisor_pydantic import SupervisorConvenienceConfiguration

config = SupervisorConvenienceConfiguration.load("config", "worker")
```

Pass Hydra overrides through `overrides`, for example
`overrides=["program.worker.environment.MODE=staging"]`.

## How to manage a supervisord instance

Install Supervisor, write the configuration, and start the daemon:

```bash
pip install supervisor
```

```python
config.write()
config.start(daemon=True)

if config.running():
    config.stop()
```

Call `kill()` only when graceful shutdown does not complete. Call `rmdir()` only
after the instance has stopped.

## How to replace a running instance's configuration

Create a convenience configuration with the same working directory and config
path as the existing instance. Apply it through the convenience commands:

```python
from supervisor_pydantic.convenience import start_programs, start_supervisor, write_supervisor_config

if not write_supervisor_config(config.model_dump_json(), _exit=False):
    raise RuntimeError("Supervisor did not stop; existing configuration was preserved")
if not start_supervisor(config, _exit=False):
    raise RuntimeError("Supervisor did not start")
if not start_programs(config, _exit=False):
    raise RuntimeError("Programs did not start")
```

Plan for an interruption: a changed configuration stops supervisord and its
managed processes before replacing the files. Keep the existing
`supervisord.conf` until the convenience command applies the new settings.
Unchanged configurations leave the running daemon in place. If graceful shutdown
times out, resolve the shutdown failure before retrying; the files remain intact.

## How to control programs over XML-RPC

Create a client from the same convenience configuration:

```python
from supervisor_pydantic import SupervisorRemoteXMLRPCClient

client = SupervisorRemoteXMLRPCClient(config)
for process in client.getAllProcessInfo():
    print(process.name, process.state)

client.stopProcess("worker")
client.startProcess("worker")
```

Set `host`, `protocol`, `port`, `username`, and `password` for remote access.
Restrict the HTTP server at the network layer because it controls processes.

## How to forward program output incrementally

Create an XML-RPC client from your local or remote configuration. Keep a byte
cursor for each process and output channel, and reuse the returned offset on
the next poll:

```python
import logging

from supervisor_pydantic import SupervisorRemoteXMLRPCClient

client = SupervisorRemoteXMLRPCClient(config)
log = logging.getLogger(__name__)
cursors = {}


def forward_logs():
    received = False
    for process in client.getProgramProcessInfo():
        name = f"{process.group}:{process.name}"
        for channel in ("stdout", "stderr"):
            key = (name, channel)
            chunk = client.readProcessLogChunk(name, channel, offset=cursors.get(key, 0))
            cursors[key] = chunk.offset
            if chunk.truncated:
                log.warning("%s %s log shrank; reading from start", name, channel)
            if chunk.text:
                received = True
                log.info("%s %s: %s", name, channel, chunk.text.rstrip("\n"))
    return received
```

Call `forward_logs()` during monitoring. After stopping workloads, keep calling
it until it returns `False` before restarting or removing their files.
To forward only future output, initialize each cursor with
`client.getProcessLogSize(name, channel)` before starting the workload.
Refer to the [log cursor reference](api.md) for rotation limits.

## How to check workloads while an event listener runs

Use `getProgramProcessInfo()` when checking modeled programs. Use
`getAllProcessInfo()` when inspecting the daemon, including event listeners:

```python
from supervisor_pydantic.convenience import check_programs, start_programs, stop_programs

start_programs(config, _exit=False)
finished = check_programs(config, check_done=True, _exit=False)
stop_programs(config, _exit=False)
```

The convenience commands start, check, and stop configured workloads while
leaving event listeners running. Stop the supervisord instance after stopping
programs when you also want to shut down listeners.

## How to use the model with airflow-config

Use the Airflow task model supplied by `airflow-supervisor`:

```yaml
dags:
  nightly-supervisor:
    schedule: "@daily"
    tasks:
      run-job:
        _target_: airflow_supervisor.SupervisorTask
        cfg:
          working_dir: /var/tmp/nightly-supervisor
          port: "127.0.0.1:9001"
          program:
            nightly:
              command: python /opt/jobs/nightly.py
```

Refer to the [airflow-supervisor tutorial](https://github.com/airflow-laminar/airflow-supervisor/blob/main/docs/src/tutorial.md)
for the generated lifecycle and Airflow installation extras.

## How to use the convenience CLI

The installed `_supervisor_convenience` command exposes the lifecycle used by
external orchestrators:

```bash
_supervisor_convenience --help
```

Commands configure and remove files, start and stop supervisord, and start,
check, restart, or stop all configured programs. Use the API reference for the
corresponding Python callables.
