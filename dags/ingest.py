import datetime

from airflow import DAG
from airflow.providers.amazon.aws.operators.batch import BatchOperator

dag = DAG(
    dag_id="jan-capstone-summer-school-dag",
    default_view="graph",
    schedule_interval=None,
    start_date=datetime.datetime(2020, 1, 1),
    catchup=False,
)

BatchOperator(
    dag=dag,
    task_id="snowflake_ingest",
    job_definition="Jan-summer-school-capstone",
    job_queue="academy-capstone-summer-2023-job-queue",
    job_name="snowflake_ingest_jan",
    overrides={}
)