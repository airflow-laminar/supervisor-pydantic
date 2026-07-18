# supervisor_pydantic.SupervisorRemoteXMLRPCClient

### *class* supervisor_pydantic.SupervisorRemoteXMLRPCClient(cfg: [SupervisorConvenienceConfiguration](supervisor_pydantic.SupervisorConvenienceConfiguration.md#supervisor_pydantic.SupervisorConvenienceConfiguration))

Bases: `object`

A light wrapper over the supervisor xmlrpc api: [http://supervisord.org/api.html](http://supervisord.org/api.html)

#### \_\_init_\_(cfg: [SupervisorConvenienceConfiguration](supervisor_pydantic.SupervisorConvenienceConfiguration.md#supervisor_pydantic.SupervisorConvenienceConfiguration))

### Methods

| [`__init__`](#supervisor_pydantic.SupervisorRemoteXMLRPCClient.__init__)(cfg)   |    |
|---------------------------------------------------------------------------------|----|
| `getAllProcessInfo`()                                                           |    |
| `getProcessInfo`(name)                                                          |    |
| `getState`()                                                                    |    |
| `readProcessLog`(name)                                                          |    |
| `readProcessStderrLog`(name)                                                    |    |
| `readProcessStdoutLog`(name)                                                    |    |
| `reloadConfig`([start_new])                                                     |    |
| `restart`()                                                                     |    |
| `shutdown`()                                                                    |    |
| `signalProcess`(name, signal)                                                   |    |
| `startAllProcesses`()                                                           |    |
| `startProcess`(name)                                                            |    |
| `stopAllProcesses`()                                                            |    |
| `stopProcess`(name)                                                             |    |
