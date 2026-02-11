from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from app.workers.ai_pipeline import extract_tasks_from_text
from app.db.session import get_db

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=10),
}

def run_task_extraction(**kwargs):
    db = next(get_db())
    text = kwargs['text']
    tasks = extract_tasks_from_text(text, db)
    print("Extracted tasks:", tasks)

with DAG(
    dag_id='task_extraction_workflow',
    default_args=default_args,
    start_date=datetime(2026, 1, 27),
    schedule_interval=None,
    catchup=False
) as dag:

    extract_tasks = PythonOperator(
        task_id='extract_tasks',
        python_callable=run_task_extraction,
    )
