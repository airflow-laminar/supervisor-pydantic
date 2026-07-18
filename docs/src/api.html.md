# API reference

## Configuration models

| [`SupervisorConfiguration`](_build/supervisor_pydantic.SupervisorConfiguration.md#supervisor_pydantic.SupervisorConfiguration)                                  |                                                                               |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| [`SupervisorConvenienceConfiguration`](_build/supervisor_pydantic.SupervisorConvenienceConfiguration.md#supervisor_pydantic.SupervisorConvenienceConfiguration) | Convenience layer, settings that MUST be set when running via convenience API |
| [`SupervisordConfiguration`](_build/supervisor_pydantic.SupervisordConfiguration.md#supervisor_pydantic.SupervisordConfiguration)                               |                                                                               |
| [`SupervisorctlConfiguration`](_build/supervisor_pydantic.SupervisorctlConfiguration.md#supervisor_pydantic.SupervisorctlConfiguration)                         |                                                                               |
| [`ProgramConfiguration`](_build/supervisor_pydantic.ProgramConfiguration.md#supervisor_pydantic.ProgramConfiguration)                                           |                                                                               |
| [`EventListenerConfiguration`](_build/supervisor_pydantic.EventListenerConfiguration.md#supervisor_pydantic.EventListenerConfiguration)                         |                                                                               |
| [`FcgiProgramConfiguration`](_build/supervisor_pydantic.FcgiProgramConfiguration.md#supervisor_pydantic.FcgiProgramConfiguration)                               |                                                                               |
| [`GroupConfiguration`](_build/supervisor_pydantic.GroupConfiguration.md#supervisor_pydantic.GroupConfiguration)                                                 |                                                                               |
| [`IncludeConfiguration`](_build/supervisor_pydantic.IncludeConfiguration.md#supervisor_pydantic.IncludeConfiguration)                                           |                                                                               |
| [`InetHttpServerConfiguration`](_build/supervisor_pydantic.InetHttpServerConfiguration.md#supervisor_pydantic.InetHttpServerConfiguration)                      |                                                                               |
| [`RpcInterfaceConfiguration`](_build/supervisor_pydantic.RpcInterfaceConfiguration.md#supervisor_pydantic.RpcInterfaceConfiguration)                            |                                                                               |
| [`UnixHttpServerConfiguration`](_build/supervisor_pydantic.UnixHttpServerConfiguration.md#supervisor_pydantic.UnixHttpServerConfiguration)                      |                                                                               |
| [`load_config`](_build/supervisor_pydantic.load_config.md#supervisor_pydantic.load_config)([config_dir, config_name, ...])                                      |                                                                               |
| [`load_convenience_config`](_build/supervisor_pydantic.load_convenience_config.md#supervisor_pydantic.load_convenience_config)([config_dir, ...])               |                                                                               |

## Runtime client

| [`SupervisorRemoteXMLRPCClient`](_build/supervisor_pydantic.SupervisorRemoteXMLRPCClient.md#supervisor_pydantic.SupervisorRemoteXMLRPCClient)(cfg)   | A light wrapper over the supervisor xmlrpc api: [http://supervisord.org/api.html](http://supervisord.org/api.html)   |
|------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| [`ProcessInfo`](_build/supervisor_pydantic.ProcessInfo.md#supervisor_pydantic.ProcessInfo)                                                           |                                                                                                                      |
| [`ProcessState`](_build/supervisor_pydantic.ProcessState.md#supervisor_pydantic.ProcessState)(value)                                                 |                                                                                                                      |
| [`SupervisorState`](_build/supervisor_pydantic.SupervisorState.md#supervisor_pydantic.SupervisorState)(value)                                        |                                                                                                                      |
| [`SupervisorMethodResult`](_build/supervisor_pydantic.SupervisorMethodResult.md#supervisor_pydantic.SupervisorMethodResult)(value)                   |                                                                                                                      |

## Convenience operations

| [`write_supervisor_config`](_build/supervisor_pydantic.write_supervisor_config.md#supervisor_pydantic.write_supervisor_config)(cfg_json[, \_exit])   | Write a SupervisorConvenienceConfiguration JSON as a supervisor config file   |
|------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| [`start_supervisor`](_build/supervisor_pydantic.start_supervisor.md#supervisor_pydantic.start_supervisor)([cfg, \_exit])                             | Start a supervisor instance using supervisord in background                   |
| [`start_programs`](_build/supervisor_pydantic.start_programs.md#supervisor_pydantic.start_programs)([cfg, restart, \_exit])                          | Start all programs in the supervisor instance                                 |
| [`check_programs`](_build/supervisor_pydantic.check_programs.md#supervisor_pydantic.check_programs)([cfg, check_running, ...])                       | Check if programs are in a good state.                                        |
| [`restart_programs`](_build/supervisor_pydantic.restart_programs.md#supervisor_pydantic.restart_programs)([cfg, force, \_exit])                      | Restart all programs in the supervisor instance                               |
| [`stop_programs`](_build/supervisor_pydantic.stop_programs.md#supervisor_pydantic.stop_programs)([cfg, \_exit])                                      | Stop all programs in the supervisor instance                                  |
| [`stop_supervisor`](_build/supervisor_pydantic.stop_supervisor.md#supervisor_pydantic.stop_supervisor)([cfg, \_exit])                                | Stop the supervisor instance                                                  |
| [`kill_supervisor`](_build/supervisor_pydantic.kill_supervisor.md#supervisor_pydantic.kill_supervisor)([cfg, \_exit])                                | Kill the supervisor instance with os.kill                                     |
| [`remove_supervisor_config`](_build/supervisor_pydantic.remove_supervisor_config.md#supervisor_pydantic.remove_supervisor_config)([cfg, \_exit])     | Remove the supervisor config file and working directory                       |
