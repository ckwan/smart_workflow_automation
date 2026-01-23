from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EmailIngestRequest(BaseModel):
    source: str  # email | slack | webhook
    sender: str
    subject: Optional[str]
    content: str


class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    priority: str
    due_date: Optional[datetime]
    assignee: Optional[str]


class TaskResponse(TaskCreate):
    id: int
    created_at: datetime
