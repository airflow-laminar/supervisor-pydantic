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
