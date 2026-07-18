# supervisor_pydantic.ProcessInfo

### *pydantic model* supervisor_pydantic.ProcessInfo

Bases: `BaseModel`

#### *field* name *: str* *[Required]*

#### *field* group *: str* *[Required]*

#### *field* state *: [ProcessState](supervisor_pydantic.ProcessState.md#supervisor_pydantic.ProcessState)* *[Required]*

#### *field* description *: str* *[Required]*

#### *field* start *: datetime* *[Required]*

#### *field* stop *: datetime* *[Required]*

#### *field* now *: datetime* *[Required]*

#### *field* spawner *: str* *= ''*

#### *field* exitstatus *: int* *[Required]*

#### *field* logfile *: str* *[Required]*

#### *field* stdout_logfile *: str* *[Required]*

#### *field* stderr_logfile *: str* *[Required]*

#### *field* pid *: int* *[Required]*

#### running()

#### stopped()

#### done(ok_exitstatuses=None)

#### ok(ok_exitstatuses=None)

#### bad(ok_exitstatuses=None)
