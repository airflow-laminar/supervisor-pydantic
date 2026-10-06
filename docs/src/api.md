# API reference

## Configuration models

```{eval-rst}
.. currentmodule:: supervisor_pydantic

.. autosummary::
   :toctree: _build

   SupervisorConfiguration
   SupervisorConvenienceConfiguration
   SupervisordConfiguration
   SupervisorctlConfiguration
   ProgramConfiguration
   EventListenerConfiguration
   FcgiProgramConfiguration
   GroupConfiguration
   IncludeConfiguration
   InetHttpServerConfiguration
   RpcInterfaceConfiguration
   UnixHttpServerConfiguration
   load_config
   load_convenience_config
```

## Runtime client

```{eval-rst}
.. currentmodule:: supervisor_pydantic

.. autosummary::
   :toctree: _build

   SupervisorRemoteXMLRPCClient
   ProcessInfo
   ProcessLogChunk
   ProcessState
   SupervisorState
   SupervisorMethodResult
```

### Workload processes

`SupervisorRemoteXMLRPCClient.getAllProcessInfo()` returns every Supervisor
process, including event listeners. `getProgramProcessInfo()` returns processes
in the configured `program` and `fcgiprogram` groups, including heterogeneous
`group` sections and `numprocs` instances. It raises `RuntimeError` when a
configured group has fewer processes than its modeled workloads require.

`startAllProcesses()` and `stopAllProcesses()` act on those workload processes.
Workload groups start in ascending configured priority and stop in descending
priority; an unspecified priority is `999`. Supervisor's group RPC methods
control process ordering within each group.
They leave listeners running and return a dictionary of `ProcessInfo` values.
For ordinary single-process programs, keys remain the program name. For grouped
or differently named processes, keys are `group:process` names. Individual
process methods also accept these qualified names.

### Log cursors

| Method                                                       | Result                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------------- |
| `getProcessLogSize(name, channel)`                           | Current output file size in bytes.                                  |
| `readProcessLogChunk(name, channel, offset=0, length=65536)` | A `ProcessLogChunk` containing new UTF-8 output from a byte offset. |

`channel` is `"stdout"` or `"stderr"`. `offset` is nonnegative; `length` is
positive and measured in bytes. A chunk can include up to three additional
bytes to complete a UTF-8 character. Logs must contain UTF-8 text, and offsets
must start at character boundaries. Invalid arguments raise `ValueError`;
names outside configured workload groups raise `RuntimeError`. XML-RPC and HTTP errors propagate
when the read cannot complete.

`ProcessLogChunk.text` contains decoded output. `offset` is the byte position
after that output, suitable for the next read. `truncated` is true when the
current file is shorter than the supplied cursor; that read starts at byte
zero. An unchanged cursor at the current file size returns empty text.
XML parsing normalizes carriage returns in `text`; offsets still count bytes
in the source file.

Supervisor XML-RPC exposes file size, but no file identity or rotation
generation. Replacement or rotation to a file at least as large as the cursor
cannot be detected. These methods read the current file; they do not recover
rotated backups. Reusing returned cursors prevents replay during ordinary
append-only logging, but does not guarantee complete delivery across rotation.

## Convenience operations

With `_exit=False`, lifecycle operations return `True` on success and `False`
when their checks fail. Configuration, transport, and filesystem exceptions
propagate. The default `_exit=True` exits with a CLI status code instead.
`kill_supervisor()` succeeds when the daemon stops; `remove_supervisor_config()`
requires successful shutdown before removing its working directory.

`write_supervisor_config()` stops a running daemon before replacing a changed
configuration. It uses the existing config's PID file path, including when the
new config changes that path. A shutdown timeout returns `False` without
overwriting either `supervisord.conf` or `pydantic.json`.

`start_supervisor()` applies the same shutdown-before-write behavior for changed
configs, then starts the daemon. Unchanged running configs return success
without restarting. These operations interrupt managed programs when the config
changes; `start_programs()` starts workloads after daemon startup.

```{eval-rst}
.. currentmodule:: supervisor_pydantic

.. autosummary::
   :toctree: _build

   write_supervisor_config
   start_supervisor
   start_programs
   check_programs
   restart_programs
   stop_programs
   stop_supervisor
   kill_supervisor
   remove_supervisor_config
```
