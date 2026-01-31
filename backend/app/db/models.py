from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    __abstract__ = True

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(50))
    assignee = Column(String(255))
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
