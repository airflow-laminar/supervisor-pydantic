# Why the convenience layer exists

`SupervisorConfiguration` mirrors supervisord's native configuration structure.
It is appropriate when every section and directive should be selected directly.
External orchestrators need a smaller, stable contract: consistent process
defaults, predictable file locations, a control endpoint, and persisted state
that later lifecycle steps can reload.

`SupervisorConvenienceConfiguration` provides that contract. It applies common
start, stop, signal, exit-code, and logging defaults across programs. It also
builds the HTTP/XML-RPC sections and stores a Pydantic JSON file beside the
rendered configuration. The `_supervisor_convenience` CLI and
[airflow-supervisor](https://github.com/airflow-laminar/airflow-supervisor) use
that persisted model to perform separate lifecycle steps safely.

## Configuration and runtime layers

Section models such as `ProgramConfiguration` and
`SupervisordConfiguration` describe the file. `SupervisorConfiguration`
assembles and persists it. `SupervisorRemoteXMLRPCClient` communicates with a
running daemon. Convenience commands combine those pieces into coarse operations
such as configure, start, check, and remove.

This separation keeps rendering usable without installing Supervisor while
making runtime dependencies explicit when lifecycle methods are called.

## Relationship to systemd and cron

Supervisord creates a dedicated process manager for the modeled programs. That
can be useful inside application-owned environments where depending on the host
service manager is undesirable.

[systemd-pydantic](https://github.com/airflow-laminar/systemd-pydantic) instead
uses the host's existing service manager and its unit lifecycle.
[cron-pydantic](https://github.com/airflow-laminar/cron-pydantic) models launch
schedules but does not supervise the processes it starts. The aligned model
names and convenience layers make the supervisor and systemd integrations
familiar without hiding their different ownership models.
