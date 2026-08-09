# supervisor_pydantic.EventListenerConfiguration

### *pydantic model* supervisor_pydantic.EventListenerConfiguration[[source]](../../../_modules/supervisor_pydantic/config/eventlistener.html.md#EventListenerConfiguration)

Bases: [`ProgramConfiguration`](supervisor_pydantic.ProgramConfiguration.html.md#supervisor_pydantic.ProgramConfiguration)

#### to_cfg(key: str) → str[[source]](../../../_modules/supervisor_pydantic/config/eventlistener.html.md#EventListenerConfiguration.to_cfg)

#### *field* buffer_size *: int | None* *= None*

The event listener pool’s event queue buffer size. When a listener pool’s event buffer is overflowed (as can happen when an event listener pool cannot keep up with all of the events sent to it), the oldest event in the buffer is discarded.

#### *field* events *: list[Literal['PROCESS_STATE', 'PROCESS_STATE_STARTING', 'PROCESS_STATE_RUNNING', 'PROCESS_STATE_BACKOFF', 'PROCESS_STATE_STOPPING', 'PROCESS_STATE_EXITED', 'PROCESS_STATE_STOPPED', 'PROCESS_STATE_FATAL', 'PROCESS_STATE_UNKNOWN', 'REMOTE_COMMUNICATION', 'PROCESS_LOG', 'PROCESS_LOG_STDOUT', 'PROCESS_LOG_STDERR', 'PROCESS_COMMUNICATION', 'PROCESS_COMMUNICATION_STDOUT', 'PROCESS_COMMUNICATION_STDERR', 'SUPERVISOR_STATE_CHANGE', 'SUPERVISOR_STATE_CHANGE_RUNNING', 'SUPERVISOR_STATE_CHANGE_STOPPING', 'TICK', 'TICK_5', 'TICK_60', 'TICK_3600', 'PROCESS_GROUP', 'PROCESS_GROUP_ADDED', 'PROCESS_GROUP_REMOVED']] | None* *= None*

A comma-separated list of event type names that this listener is “interested” in receiving notifications for (see Event Types for a list of valid event type names).

#### *field* result_handler *: str | None* *= None*

A pkg_resources entry point string that resolves to a Python callable. The default value is supervisor.dispatchers:default_handler. Specifying an alternate result handler is a very uncommon thing to need to do, and as a result, how to create one is not documented.
