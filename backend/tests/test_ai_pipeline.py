from app.workers.ai_pipeline import extract_tasks_from_text

def test_extract_tasks_returns_structured_output():
    email_text = "Please submit the report by Friday. Assign to John."

    tasks = extract_tasks_from_text(email_text)

    assert isinstance(tasks, list)
    assert len(tasks) == 1

    task = tasks[0]
    assert task.title
    assert task.description
    assert task.priority == "medium"
