# supervisor-pydantic

[Pydantic](https://docs.pydantic.dev/latest/) models for [supervisor](https://supervisord.org)

[![Build Status](https://github.com/airflow-laminar/supervisor-pydantic/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/airflow-laminar/supervisor-pydantic/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/airflow-laminar/supervisor-pydantic/branch/main/graph/badge.svg)](https://codecov.io/gh/airflow-laminar/supervisor-pydantic)
[![License](https://img.shields.io/github/license/airflow-laminar/supervisor-pydantic)](https://github.com/airflow-laminar/supervisor-pydantic)
[![PyPI](https://img.shields.io/pypi/v/supervisor-pydantic.svg)](https://pypi.python.org/pypi/supervisor-pydantic)

## Overview
This library provides type-validated [Pydantic](https://docs.pydantic.dev/latest/) models of all configuration options for [supervisor](https://supervisord.org).

It provides:
- `SupervisorConfiguration`: top-level wrapper around all supervisor configuration options, with a utility method to generate a [`supervisord.conf`](https://supervisord.org/configuration.html)
- `SupervisorConvenienceConfiguration`: wrapper around `SupervisorConfiguration` to make a few things easier to configure, for integration with [airflow-supervisor](https://github.com/airflow-laminar/airflow-supervisor) and other external tools
- `SupervisordConfiguration`: wrapper around [`supervisord`](https://supervisord.org/configuration.html#supervisord-section-settings)
- `SupervisorctlConfiguration`: wrapper around [`supervisorctl`](https://supervisord.org/configuration.html#supervisorctl-section-settings)
- `ProgramConfiguration`: wrapper around [`program`](https://supervisord.org/configuration.html#program-x-section-settings)
- `EventListenerConfiguration`: wrapper around [`eventlistener`](https://supervisord.org/configuration.html#eventlistener-x-section-settings)
- `FcgiProgramConfiguration`: wrapper around [`fcgi-program`](https://supervisord.org/configuration.html#fcgi-program-x-section-settings)
- `GroupConfiguration`: wrapper around [`group`](https://supervisord.org/configuration.html#group-x-section-settings)
- `IncludeConfiguration`: wrapper around [`include`](https://supervisord.org/configuration.html#include-section-settings)
- `InetHttpServerConfiguration`: wrapper around [`init-http-server`](https://supervisord.org/configuration.html#inet-http-server-section-settings)
- `RpcInterfaceConfiguration`: wrapper around [`rpcinterface`](https://supervisord.org/configuration.html#rpcinterface-x-section-settings)
- `UnixHttpServerConfiguration`: wrapper around [`unix-http-server`](https://supervisord.org/configuration.html#unix-http-server-section-settings)
- `ConvenienceConfiguration`: Required minimum set of configuration settings to run supervisor using the `SupervisorConvenienceConfiguration`

```mermaid
classDiagram
    SupervisorConfiguration <|-- SupervisorConvenienceConfiguration
    SupervisorConfiguration *-- SupervisordConfiguration
    SupervisorConfiguration *-- SupervisorctlConfiguration
    SupervisorConfiguration *-- InetHttpServerConfiguration
    SupervisorConfiguration *-- UnixHttpServerConfiguration
    SupervisorConfiguration *-- IncludeConfiguration
    SupervisorConfiguration *-- ProgramConfiguration
    SupervisorConfiguration *-- EventListenerConfiguration
    SupervisorConfiguration *-- FcgiProgramConfiguration
    SupervisorConfiguration *-- GroupConfiguration
    SupervisorConfiguration *-- RpcInterfaceConfiguration
    SupervisorConvenienceConfiguration *-- ConvenienceConfiguration

    class SupervisorConfiguration {
        supervisord: SupervisordConfiguration
        supervisorctl: SupervisorctlConfiguration
        inet_http_server: InetHttpServerConfiguration
        unix_http_server: UnixHttpServerConfiguration

        include: IncludeConfiguration

        program: Dict~str, ProgramConfiguration~
        eventlistener: Dict~str, EventListenerConfiguration~
        fcgiprogram: Dict~str, FcgiProgramConfiguration~
        group: Dict~str, GroupConfiguration~
        rpcinterface: Dict~str, RpcInterfaceConfiguration~

        config_path: Path
        working_dir: Path

        load(config_dir; str, config_name: str, overrides: List~str~)
        write()
        rmdir()
        start(daemon: bool)
        running()
        stop()
        kill()
    }
    class SupervisorConvenienceConfiguration {
        convenience ConvenienceConfiguration
    }
    class SupervisordConfiguration {
      logfile: Path
      logfile_maxbytes: str
      logfile_backups: int
      loglevel: LogLevel
      pidfile: Path
      umask: OctalUmask
      nodaemon: bool
      silent: bool
      minfds: int
      minprocs: int
      nocleanup: bool
      childlogdir: Path
      user: str
      directory: Path
      strip_ansi: bool
      environment: dict
      identifier: str
    }
    class SupervisorctlConfiguration {
      serverurl: str
      username: str
      password: str
      prompt: str
      history_file: Path
    }
    class InetHttpServerConfiguration {
      port: str
      username: str
      password: str
    }
    class UnixHttpServerConfiguration {
      file: Path
      chmod: Octal
      chown: str
      username: str
      password: str
    }
    class IncludeConfiguration {
      files: List~str~
    }
    class ProgramConfiguration {
      command: str
      process_name: str
      numprocs: int
      numprocs_start: int
      priority: int
      autostart: bool
      startsecs: int
      startretries: int
      autorestart: bool
      exitcodes: List~int~
      stopsignal: Signal
      stopwaitsecs: int
      stopasgroup: bool
      killasgroup: bool
      user: str
      redirect_stderr: bool
      stdout_logfile: Path
      stdout_logfile_maxbytes: str
      stdout_logfile_backups: int
      stdout_capture_maxbytes: int
      stdout_events_enabled: int
      stdout_syslog: bool
      stderr_logfile: Path
      stderr_logfile_maxbytes: str
      stderr_logfile_backups: int
      stderr_capture_maxbytes: int
      stderr_events_enabled: bool
      stderr_syslog: bool
      environment: Dict~str, str~
      directory: Path
      umask: OctalUmask
      serverurl: str
    }
    class EventListenerConfiguration {
      buffer_size: int
      events: List~EventType~
      result_handler: str
    }
    class FcgiProgramConfiguration {
      socket: str
      socket_backlog: str
      socket_owner: strOrGroup
      socket_mode: Octal
    }
    class GroupConfiguration {
      programs: List~str~
      priority: int
    }
    class RpcInterfaceConfiguration {
      rpcinterface_factory: str
      kwargs: Dict~str, Any~
    }
    class ConvenienceConfiguration {
      startsecs: int
      startretries: int
      exitcodes: List~int~
      stopsignal: Signal
      stopwaitsecs: int
      port: str
      password: str
      rpcinterface_factory: str
      local_or_remote: str
      host: str
      protocol: str
      rpcpath: str
      command_timeout: int
    }

```

Additionally, this library provides a small convenience CLI (`_supervisor_convenience`) for remotely managing supervisor. It is a simple wrapper around the [`supervisord`](https://supervisord.org/running.html#running-supervisord) and [`supervisorctl`](https://supervisord.org/running.html#running-supervisorctl) CLIs in supervisor.

- `check-programs`:  Check if programs are in a good state.
- `configure-supervisor`:  Write a SupervisorConvenienceConfiguration JSON as a supervisor config file
- `force-kill`:  Kill the supervisor instance with os.kill
- `restart-programs`:  Restart all programs in the supervisor instance
- `start-programs`:  Start all programs in the supervisor instance
- `start-supervisor`:  Start a supervisor instance using supervisord in background
- `stop-programs`:  Stop all programs in the supervisor instance
- `stop-supervisor`:  Stop the supervisor instance
- `unconfigure-supervisor`:  Remove the supervisor config file and working directory


> [!NOTE]
> This library was generated using [copier](https://copier.readthedocs.io/en/stable/) from the [Base Python Project Template repository](https://github.com/python-project-templates/base).
