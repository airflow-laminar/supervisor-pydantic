# supervisor_pydantic.SupervisordConfiguration

### *pydantic model* supervisor_pydantic.SupervisordConfiguration

Bases: `_BaseCfgModel`

#### *field* logfile *: Path | None* *= None*

The path to the activity log of the supervisord process. This option can include the value %(here)s, which expands to the directory in which the supervisord configuration file was found.

#### *field* logfile_maxbytes *: str | None* *= None*

The maximum number of bytes that may be consumed by the activity log file before it is rotated (suffix multipliers like “KB”, “MB”, and “GB” can be used in the value). Set this value to 0 to indicate an unlimited log size.

#### *field* logfile_backups *: int | None* *= None*

The number of backups to keep around resulting from activity log file rotation. If set to 0, no backups will be kept.

#### *field* loglevel *: Literal['critical', 'error', 'warn', 'info', 'debug', 'trace', 'blather'] | None* *= None*

The logging level, dictating what is written to the supervisord activity log. One of critical, error, warn, info, debug, trace, or blather. Note that at log level debug, the supervisord log file will record the stderr/stdout output of its child processes and extended info about process state changes, which is useful for debugging a process which isn’t starting properly. See also: Activity Log Levels.

#### *field* pidfile *: Path | None* *= None*

The location in which supervisord keeps its pid file. This option can include the value %(here)s, which expands to the directory in which the supervisord configuration file was found.

#### *field* umask *: \_check_is_octal)] | None* *= None*

The umask of the supervisord process.

#### *field* nodaemon *: bool | None* *= None*

If true, supervisord will start in the foreground instead of daemonizing.

#### *field* silent *: bool | None* *= None*

If true and not daemonized, logs will not be directed to stdout.

#### *field* minfds *: int | None* *= None*

The minimum number of file descriptors that must be available before supervisord will start successfully. A call to setrlimit will be made to attempt to raise the soft and hard limits of the supervisord process to satisfy minfds. The hard limit may only be raised if supervisord is run as root. supervisord uses file descriptors liberally, and will enter a failure mode when one cannot be obtained from the OS, so it’s useful to be able to specify a minimum value to ensure it doesn’t run out of them during execution. These limits will be inherited by the managed subprocesses. This option is particularly useful on Solaris, which has a low per-process fd limit by default.

#### *field* minprocs *: int | None* *= None*

The minimum number of process descriptors that must be available before supervisord will start successfully. A call to setrlimit will be made to attempt to raise the soft and hard limits of the supervisord process to satisfy minprocs. The hard limit may only be raised if supervisord is run as root. supervisord will enter a failure mode when the OS runs out of process descriptors, so it’s useful to ensure that enough process descriptors are available upon supervisord startup.

#### *field* nocleanup *: bool | None* *= None*

Prevent supervisord from clearing any existing AUTO child log files at startup time. Useful for debugging.

#### *field* childlogdir *: Path | None* *= None*

The directory used for AUTO child log files. This option can include the value %(here)s, which expands to the directory in which the supervisord configuration file was found.

#### *field* user *: Annotated[str, AfterValidator(func=\_is_username)] | None* *= None*

Instruct supervisord to switch users to this UNIX user account before doing any meaningful processing. The user can only be switched if supervisord is started as the root user.

#### *field* directory *: Path | None* *= None*

When supervisord daemonizes, switch to this directory. This option can include the value %(here)s, which expands to the directory in which the supervisord configuration file was found.

#### *field* strip_ansi *: bool | None* *= None*

Strip all ANSI escape sequences from child log files.

#### *field* environment *: dict | None* *= None*

A list of key/value pairs in the form KEY=”val”,KEY2=”val2” that will be placed in the environment of all child processes. This does not change the environment of supervisord itself. This option can include the value %(here)s, which expands to the directory in which the supervisord configuration file was found. Values containing non-alphanumeric characters should be quoted (e.g. KEY=”val:123”,KEY2=”val,456”). Otherwise, quoting the values is optional but recommended. To escape percent characters, simply use two. (e.g. URI=”/first%%20name”) Note that subprocesses will inherit the environment variables of the shell used to start supervisord except for the ones overridden here and within the program’s environment option. See Subprocess Environment.

#### *field* identifier *: str | None* *= None*

The identifier string for this supervisor process, used by the RPC interface.
