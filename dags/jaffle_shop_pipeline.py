from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

DBT_DIR = "/home/guscrat/Documents/projetos/dbt_project/DBT-Fundamentals---Jaffle-Shop"

with DAG(
    dag_id="jaffle_shop_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["dbt", "duckdb", "jaffle_shop"],
) as dag:

    load_raw = BashOperator(
        task_id="load_raw",
        bash_command=f"cd {DBT_DIR} && uv run python load_raw.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && uv run dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && uv run dbt test",
    )

    load_raw >> dbt_run >> dbt_test