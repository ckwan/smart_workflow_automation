from sqlalchemy.orm import Session
from .models import Task
from app.api.schemas import TaskCreate


def create_task(db: Session, task: TaskCreate) -> Task:
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
