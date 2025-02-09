from pathlib import Path

from supervisor_pydantic import AirflowConfiguration, ProgramConfiguration, SupervisorConvenienceConfiguration

if __name__ == "__main__":
    path = Path(__file__).parent.parent.parent
    cfg = SupervisorConvenienceConfiguration(
        airflow=AirflowConfiguration(port="*:9090"),
        working_dir=path,
        path=path,
        program={
            "test": ProgramConfiguration(
                command="bash -c 'sleep 60; exit 1'",
            )
        },
    )
    print(cfg._pydantic_path)
    cfg._write_self()
