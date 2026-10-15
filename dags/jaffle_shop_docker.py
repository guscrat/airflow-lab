import os
from dotenv import load_dotenv
from pathlib import Path
from cosmos import DbtDag
from datetime import datetime

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


DBT_IMAGE = "jaffle-shop-analytics-bigquery-dbt"
DBT_PROJECT_PATH=os.environ.get("DBT_PROJECT_PATH")

dbt_dag = DbtDag(
    dag_id="dbt_cosmos",
    start_date=datetime(2026, 1, 1),
    schedule="@daily"
)