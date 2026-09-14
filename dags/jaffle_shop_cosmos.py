from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig

DBT_PROJECT_DIR = "/home/guscrat/Documents/projetos/dbt_project/DBT-Fundamentals---Jaffle-Shop"
DBT_EXECUTABLE = f"{DBT_PROJECT_DIR}/.venv/bin/dbt"
PROFILES_YML = "/home/guscrat/.dbt/profiles.yml"


def alerta_falha(context):
    ti = context["ti"]
    print(f"❌ Task '{ti.task_id}' falhou na DAG '{ti.dag_id}'. Aqui iria um alerta real.")


profile_config = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profiles_yml_filepath=PROFILES_YML,
)

execution_config = ExecutionConfig(
    dbt_executable_path=DBT_EXECUTABLE,
)

default_args = {
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
    "on_failure_callback": alerta_falha,
}

with DAG(
    dag_id="jaffle_shop_cosmos",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["dbt", "duckdb", "cosmos"],
) as dag:

    load_raw = BashOperator(
        task_id="load_raw",
        bash_command=f"cd {DBT_PROJECT_DIR} && uv run python load_raw.py",
    )

    transform = DbtTaskGroup(
        group_id="dbt_transform",
        project_config=ProjectConfig(DBT_PROJECT_DIR),
        profile_config=profile_config,
        execution_config=execution_config,
        operator_args={"pool": "duckdb_pool"},
    )

    load_raw >> transform