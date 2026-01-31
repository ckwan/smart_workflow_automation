from pydantic import BaseModel, Field, field_validator
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


class TaskSchema(BaseModel):
    title: str
    description: str
    priority: str = Field(..., pattern="^(low|medium|high)$")
    due_date: Optional[datetime] = None
    assignee: Optional[str] = None

    @field_validator("assignee")
    def validate_email(cls, v):
        if v and "@" not in v:
            raise ValueError("assignee must be a valid email")
        return v

class TasksOutput(BaseModel):
    tasks: List[TaskSchema]
