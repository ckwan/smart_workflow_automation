from celery import Celery
from app.core.config import settings
from app.workers.ai_pipeline import extract_tasks_from_text
from app.db import crud, session
from app.db.models import Base
from sqlalchemy.orm import Session

# Celery config
celery_app = Celery(
    "worker",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
)

# Ensure DB tables exist
Base.metadata.create_all(bind=session.engine)


@celery_app.task(name="process_message")
def process_message(payload: dict):
    """
    Async task:
    - Runs AI extraction
    - Persists structured tasks into Postgres
    """

    content = payload.get("content", "")
    tasks = extract_tasks_from_text(content)

    db: Session = session.SessionLocal()
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
