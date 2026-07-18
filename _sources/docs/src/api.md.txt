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
   ProcessState
   SupervisorState
   SupervisorMethodResult
```

## Convenience operations

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
