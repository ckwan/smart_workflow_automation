from sqlalchemy import create_engine
from app.config import DATABASE_URL, get_db
from celery import Celery, shared_task
from app.core.config import settings
from app.workers.ai_pipeline import extract_tasks_from_text
from app.db import crud
from app.db.models import Base
from app.workers.ai_pipeline import extract_tasks_from_text
from app.db.crud import create_task
from app.notifications.slack import send_slack_notification

# Celery config
celery_app = Celery(
    "worker",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
)

engine = create_engine(DATABASE_URL)

# Ensure DB tables exist
Base.metadata.create_all(engine)

@celery_app.task(name="process_message")
def process_message(payload: dict):
    """
    Async task:
    - Runs AI extraction
    - Persists structured tasks into Postgres
    """

    content = payload.get("content", "")
    tasks = extract_tasks_from_text(content)

    db = next(get_db())
    persisted_tasks = []

    try:
        for task in tasks:
            db_task = crud.create_task(db, task)
            persisted_tasks.append(db_task.id)
        db.commit()
    finally:
        db.close()

    return {
        "status": "processed",
        "task_ids": persisted_tasks,
        "message_source": payload.get("source", "unknown"),
    }

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_email_task(self, email_text):
    try:
        persisted_tasks = []
        tasks = extract_tasks_from_text(email_text)
        for task in tasks:
            db_task = create_task(task)
            if db_task:  # Ensure task was created successfully
                persisted_tasks.append(db_task.id)
            send_slack_notification(task)

        return {
            "status": "processed",
            "task_ids": persisted_tasks,
            "message_source": payload.get("source", "unknown"),
        }
    except Exception as e:
        print("Celery task failed:", e)
        raise self.retry(exc=e)
