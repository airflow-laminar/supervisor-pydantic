# Examples

This page provides practical examples of using `supervisor-pydantic` for common use cases.

## Basic Examples

### Running a Simple Worker Process

```python
from supervisor_pydantic import (
    SupervisorConvenienceConfiguration,
    ProgramConfiguration,
)

config = SupervisorConvenienceConfiguration(
    port="*:9001",
    working_dir="/tmp/worker-supervisor",
    program={
        "worker": ProgramConfiguration(
            command="python my_worker.py",
            autostart=True,
            autorestart=True,
            startsecs=5,
        ),
    },
)

config.write()
config.start(daemon=True)
```

### Multiple Programs

Run multiple programs under a single supervisor instance:

```python
from supervisor_pydantic import (
    SupervisorConvenienceConfiguration,
    ProgramConfiguration,
)

config = SupervisorConvenienceConfiguration(
    port="*:9001",
    working_dir="/tmp/multi-supervisor",
    program={
        "web": ProgramConfiguration(
            command="python -m http.server 8080",
            directory="/var/www",
        ),
        "worker": ProgramConfiguration(
            command="celery -A tasks worker",
            numprocs=4,  # Run 4 worker processes
        ),
        "scheduler": ProgramConfiguration(
            command="celery -A tasks beat",
        ),
    },
)

config.write()
config.start(daemon=True)
```

### With Authentication

Secure your supervisor HTTP interface with username and password:

```python
from supervisor_pydantic import (
    SupervisorConvenienceConfiguration,
    ProgramConfiguration,
)

config = SupervisorConvenienceConfiguration(
    port="*:9001",
    username="admin",
    password="secure-password-123",
    working_dir="/tmp/secure-supervisor",
    program={
        "app": ProgramConfiguration(
            command="python app.py",
        ),
    },
)

config.write()
config.start(daemon=True)
```

## Advanced Examples

### Environment Variables

Pass environment variables to your programs:

```python
from supervisor_pydantic import (
    SupervisorConvenienceConfiguration,
    ProgramConfiguration,
)

config = SupervisorConvenienceConfiguration(
    port="*:9001",
    working_dir="/tmp/env-supervisor",
    program={
        "app": ProgramConfiguration(
            command="python app.py",
            environment={
                "DATABASE_URL": "postgresql://localhost/mydb",
                "REDIS_URL": "redis://localhost:6379",
                "LOG_LEVEL": "INFO",
            },
        ),
    },
)
```

### Custom Exit Codes

Configure which exit codes are considered successful:

```python
from supervisor_pydantic import (
    SupervisorConvenienceConfiguration,
    ProgramConfiguration,
)

config = SupervisorConvenienceConfiguration(
    port="*:9001",
    working_dir="/tmp/exitcode-supervisor",
    exitcodes=[0, 1, 2],  # Consider 0, 1, and 2 as successful exits
    program={
        "batch-job": ProgramConfiguration(
            command="python batch_job.py",
            autorestart=False,  # Don't restart after completion
            exitcodes=[0, 1],  # Program-specific exit codes
        ),
    },
)
```

### Using Groups

Organize programs into groups for batch control:

```python
from supervisor_pydantic import (
    SupervisorConfiguration,
    SupervisordConfiguration,
    InetHttpServerConfiguration,
    ProgramConfiguration,
    GroupConfiguration,
)
from pathlib import Path

config = SupervisorConfiguration(
    supervisord=SupervisordConfiguration(
        logfile=Path("/var/log/supervisord.log"),
        pidfile=Path("/var/run/supervisord.pid"),
    ),
    inet_http_server=InetHttpServerConfiguration(port="*:9001"),
    program={
        "web-1": ProgramConfiguration(command="gunicorn app:app -b :8001"),
        "web-2": ProgramConfiguration(command="gunicorn app:app -b :8002"),
        "worker-1": ProgramConfiguration(command="celery -A tasks worker"),
        "worker-2": ProgramConfiguration(command="celery -A tasks worker"),
    },
    group={
        "web-servers": GroupConfiguration(programs=["web-1", "web-2"]),
        "workers": GroupConfiguration(programs=["worker-1", "worker-2"]),
    },
    config_path=Path("/etc/supervisor/supervisord.conf"),
    working_dir=Path("/var/supervisor"),
)

# Now you can control groups:
# supervisorctl start web-servers:*
# supervisorctl stop workers:*
```

### Event Listeners

Configure event listeners for monitoring:

```python
from supervisor_pydantic import (
    SupervisorConfiguration,
    SupervisordConfiguration,
    InetHttpServerConfiguration,
    ProgramConfiguration,
    EventListenerConfiguration,
)
from pathlib import Path

config = SupervisorConfiguration(
    supervisord=SupervisordConfiguration(
        logfile=Path("/var/log/supervisord.log"),
        pidfile=Path("/var/run/supervisord.pid"),
    ),
    inet_http_server=InetHttpServerConfiguration(port="*:9001"),
    program={
        "app": ProgramConfiguration(command="python app.py"),
    },
    eventlistener={
        "crashmail": EventListenerConfiguration(
            command="crashmail -a -m admin@example.com",
            events=["PROCESS_STATE_EXITED"],
        ),
    },
    config_path=Path("/etc/supervisor/supervisord.conf"),
    working_dir=Path("/var/supervisor"),
)
```

## Remote Management with XML-RPC Client

Use the XML-RPC client to manage supervisor remotely:

```python
from supervisor_pydantic import (
    SupervisorConvenienceConfiguration,
    SupervisorRemoteXMLRPCClient,
    ProgramConfiguration,
)

# Create configuration
config = SupervisorConvenienceConfiguration(
    port="*:9001",
    host="remote-server.example.com",
    working_dir="/tmp/remote-supervisor",
    program={
        "app": ProgramConfiguration(command="python app.py"),
    },
)

# Connect to running supervisor
client = SupervisorRemoteXMLRPCClient(config)

# Get process info
info = client.getProcessInfo("app")
print(f"Process state: {info.state}")

# Start/stop processes
client.startProcess("app")
client.stopProcess("app")

# Get all process info
all_info = client.getAllProcessInfo()
for proc in all_info:
    print(f"{proc.name}: {proc.state}")
```

## Using with Hydra

`supervisor-pydantic` integrates with [Hydra](https://hydra.cc/) for configuration management:

```yaml
# config.yaml
supervisor:
  _target_: supervisor_pydantic.SupervisorConvenienceConfiguration
  port: "*:9001"
  working_dir: /tmp/hydra-supervisor
  program:
    worker:
      _target_: supervisor_pydantic.ProgramConfiguration
      command: python worker.py
```

```python
import hydra
from omegaconf import DictConfig

@hydra.main(config_path=".", config_name="config")
def main(cfg: DictConfig):
    from hydra.utils import instantiate

    config = instantiate(cfg.supervisor)
    config.write()
    config.start(daemon=True)

if __name__ == "__main__":
    main()
```

## Programmatic Lifecycle Management

Complete lifecycle management example:

```python
from supervisor_pydantic import (
    SupervisorConvenienceConfiguration,
    ProgramConfiguration,
)
import time

def run_supervised_job():
    config = SupervisorConvenienceConfiguration(
        port="*:9001",
        working_dir="/tmp/lifecycle-supervisor",
        program={
            "job": ProgramConfiguration(
                command="python long_running_job.py",
                autorestart=False,
            ),
        },
    )

    try:
        # Write config and start
        config.write()
        config.start(daemon=True)

        # Wait for startup
        for _ in range(10):
            if config.running():
                break
            time.sleep(1)
        else:
            raise RuntimeError("Supervisor failed to start")

        print("Supervisor started successfully")

        # ... do work or monitor ...

    finally:
        # Clean shutdown
        if config.running():
            config.stop()

            # Wait for shutdown
            for _ in range(10):
                if not config.running():
                    break
                time.sleep(1)
            else:
                # Force kill if graceful shutdown fails
                config.kill()

        # Clean up files
        config.rmdir()
        print("Cleanup complete")

if __name__ == "__main__":
    run_supervised_job()
```
