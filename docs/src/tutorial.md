# Tutorial: render a supervisord configuration

In this tutorial, we will model one worker process, render its supervisord
configuration, and write the files to a temporary directory.

## Install the package

```bash
pip install supervisor-pydantic
```

## Create the model

Create `example.py`:

```python
from supervisor_pydantic import ProgramConfiguration, SupervisorConvenienceConfiguration

config = SupervisorConvenienceConfiguration(
    working_dir="/tmp/tutorial-supervisor",
    port="127.0.0.1:9001",
    program={
        "worker": ProgramConfiguration(
            command="python -m http.server 8080",
            environment={"MODE": "tutorial"},
        )
    },
)

print(config.to_cfg())
config.write()
print(config.config_path)
```

Run it:

```bash
python example.py
```

The rendered text contains `[program:worker]`, its command, and the environment
setting. The final line points to:

```text
/tmp/tutorial-supervisor/supervisord.conf
```

## Inspect the generated layout

List the directory:

```bash
find /tmp/tutorial-supervisor -maxdepth 2 -type f
```

The configuration file exists, and the worker directory has been created for
its output and error logs. No supervisord process has been started.

You have now built and persisted a validated supervisord configuration.
