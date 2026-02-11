from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from app.workers.ai_pipeline import extract_tasks_from_text, get_new_emails
from app.config import get_db

def run_slack_pipeline():
    db = next(get_db())
    emails = get_new_emails()  # fetch new emails
    for email_text in emails:
        get_new_emails(email_text, db)

with DAG(
    dag_id="email_task_pipeline",
    start_date=datetime(2026, 1, 28),
    schedule_interval="*/1 * * * *",
    catchup=False,
) as dag:

    process_emails = PythonOperator(
        task_id="process_emails",
        python_callable=run_slack_pipeline
    )
