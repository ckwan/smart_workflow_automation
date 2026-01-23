from celery import Celery
from app.core.config import settings
from app.workers.ai_pipeline import extract_tasks_from_text

celery_app = Celery(
    "worker",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
)


@celery_app.task(name="process_message")
def process_message(payload: dict):
    """
    Async task:
    - Runs AI extraction
    - Persists structured tasks
    """

    content = payload.get("content", "")
    tasks = extract_tasks_from_text(content)

    # DB persistence will be wired next
    return {
        "extracted_tasks": [task.dict() for task in tasks],
        "status": "processed",
    }
