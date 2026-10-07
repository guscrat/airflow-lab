import os
from pathlib import Path
from dotenv import load_dotenv

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
DBT_PROJECT_DIR = os.environ.get("DBT_PROJECT_DIR")

def alerta_falha(context):
    ti = context["ti"]
    print(
        f"❌ Task '{ti.task_id}' falhou na DAG '{ti.dag_id}' "
        f"(run: {context['run_id']}). "
        "Aqui entraria um alerta real — Slack ou e-mail."
    )


default_args = {
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
    "on_failure_callback": alerta_falha,
}

with DAG(
    dag_id="jaffle_shop_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["dbt", "bigquery", "jaffle_shop"],
) as dag:

    load_raw = BashOperator(
        task_id="load_raw",
        bash_command=f"cd {DBT_PROJECT_DIR} && uv run python load_raw.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && uv run dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && uv run dbt test",
    )

    load_raw >> dbt_run >> dbt_test # type: ignore