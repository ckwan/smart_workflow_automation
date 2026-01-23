"""
AI Pipeline:
- Parse unstructured text
- Extract tasks, deadlines, assignees
- Return structured data
"""

from app.api.schemas import TaskCreate
from datetime import datetime


def extract_tasks_from_text(text: str) -> list[TaskCreate]:
    """
    Placeholder AI logic.
    Replace with DSPy + LLM later.
    """

    # Mock output (for pipeline testing)
    return [
        TaskCreate(
            title="Review extracted task",
            description=text[:200],
            priority="medium",
            due_date=None,
            assignee=None,
        )
    ]
