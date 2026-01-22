# Getting Started

This guide will help you get started with `supervisor-pydantic`, a library that provides type-validated Pydantic models for [supervisor](https://supervisord.org) configuration.

## Installation

Install `supervisor-pydantic` using pip:

```bash
pip install supervisor-pydantic
```

## Prerequisites

To actually run supervisor processes, you'll need to have `supervisord` installed:

```bash
pip install supervisor
```

## Quick Start

### Creating a Basic Configuration

The simplest way to get started is with `SupervisorConvenienceConfiguration`, which provides sensible defaults:

```python
from supervisor_pydantic import (
    SupervisorConvenienceConfiguration,
    ProgramConfiguration,
)

# Create a configuration with a single program
config = SupervisorConvenienceConfiguration(
    port="*:9001",
    working_dir="/tmp/my-supervisor",
    program={
        "my-worker": ProgramConfiguration(
            command="python worker.py",
        ),
    },
)

# Write the configuration file
config.write()

# Start supervisor
config.start(daemon=True)

# Check if it's running
if config.running():
    print("Supervisor is running!")
```

### Using the Full Configuration

For more control, use `SupervisorConfiguration` directly:

```python
from pathlib import Path
from supervisor_pydantic import (
    SupervisorConfiguration,
    SupervisordConfiguration,
    SupervisorctlConfiguration,
    InetHttpServerConfiguration,
    ProgramConfiguration,
)

config = SupervisorConfiguration(
    supervisord=SupervisordConfiguration(
        logfile=Path("/var/log/supervisord.log"),
        pidfile=Path("/var/run/supervisord.pid"),
    ),
    supervisorctl=SupervisorctlConfiguration(
        serverurl="http://localhost:9001",
    ),
    inet_http_server=InetHttpServerConfiguration(
        port="*:9001",
        username="admin",
        password="secret",
    ),
    program={
        "web-server": ProgramConfiguration(
            command="python -m http.server 8080",
            autostart=True,
            autorestart=True,
        ),
    },
    config_path=Path("/etc/supervisor/supervisord.conf"),
    working_dir=Path("/var/supervisor"),
)

# Generate the configuration file content
print(config.to_cfg())

# Write to disk
config.write()
```

### Using the CLI

`supervisor-pydantic` includes a CLI for managing supervisor instances:

```bash
# Start supervisor with a configuration
_supervisor_convenience start-supervisor --cfg pydantic.json

# Check program status
_supervisor_convenience check-programs --cfg pydantic.json

# Stop all programs
_supervisor_convenience stop-programs --cfg pydantic.json

# Stop supervisor
_supervisor_convenience stop-supervisor --cfg pydantic.json
```

> [!NOTE]
> This CLI should be considered work-in-progress, thus the underscore prefix

## Next Steps

- See the [Examples](examples.md) for more detailed use cases
- Check the [API Reference](API.md) for complete documentation of all configuration options
- Learn about integration with other airflow-laminar libraries below

## Integration with Other Libraries

`supervisor-pydantic` is designed to integrate seamlessly with other libraries in the [airflow-laminar](https://github.com/airflow-laminar) ecosystem:

### airflow-supervisor

[airflow-supervisor](https://github.com/airflow-laminar/airflow-supervisor) uses `supervisor-pydantic` to manage external processes as part of Airflow DAGs. It provides operators and sensors for starting, monitoring, and stopping supervised processes within your Airflow workflows.

```python
from airflow_supervisor import SupervisorOperator

# Use supervisor-pydantic configuration in Airflow
operator = SupervisorOperator(
    task_id="start_worker",
    configuration=SupervisorConvenienceConfiguration(...),
)
```

### airflow-config

[airflow-config](https://github.com/airflow-laminar/airflow-config) provides configuration management for Airflow. You can use supervisor configurations within your Airflow workflows that are managed by airflow-config.

See the documentation for each library for more details on integration patterns.
