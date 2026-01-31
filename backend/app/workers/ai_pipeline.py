import requests
from app.core.config import settings
from sqlalchemy.orm import Session
from app.db import crud, models
from app.notifications import slack
from ollama import chat
from app.api.schemas import TaskCreate, TaskSchema
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import dspy
from app.api.schemas import TasksOutput
import json
import mlflow
import subprocess
import imaplib
import email
from email.header import decode_header
from typing import List

# Configure LM
# lm = dspy.LM(lm=settings.LOCAL_LLM_MODEL)
# dspy.configure(lm=lm)

# DSPy module
sig = dspy.Signature("text -> tasks")
module = dspy.Predict(sig)


# def call_ollama(prompt_text: str) -> str:
#     """
#     Calls Ollama LLaMA model via Docker.
#     Make sure the Ollama server is running (ollama serve).
#     """
#     try:
#         # result = subprocess.run(
#         #     ["docker", "exec", "-i", "ollama-server", "ollama", "run", "llama3.2", text],
#         #     capture_output=True,
#         #     text=True,
#         #     check=True  # raises CalledProcessError if non-zero exit
#         # )

#         url = "http://localhost:11434/v1/completions"  # example endpoint
#         payload = {
#             "model": "llama3.2",
#             "prompt": prompt_text,
#             "max_tokens": 200
#         }
#         response = requests.post(url, json=payload)
#         return response.json()

#         # print(result)
#         # return result.stdout.strip()
#     except subprocess.CalledProcessError as e:
#         print("Ollama call failed:", e.stderr)
#         return ""

def get_new_emails() -> str:
    EMAIL_USER = settings.SMTP_USER
    EMAIL_PASS = settings.SMTP_PASS

    # Connect to Gmail IMAP
    imap = imaplib.IMAP4_SSL(settings.IMAP_SERVER, settings.IMAP_PORT)
    imap.login(EMAIL_USER, EMAIL_PASS)

    # Select the inbox (readonly=False to mark emails as read)
    imap.select(settings.SMTP_MAILBOX)

    # Search for UNSEEN emails (new messages)
    status, messages = imap.search(None, 'UNSEEN')
    if status != "OK":
        print("No new messages.")
    else:
        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} new messages.")

        for e_id in email_ids:
            # Fetch the email by ID
            res, msg_data = imap.fetch(e_id, "(RFC822)")
            if res != "OK":
                continue

            msg = email.message_from_bytes(msg_data[0][1])

            # Decode subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

            # From field
            from_ = msg.get("From")
            print(f"From: {from_}, Subject: {subject}")

            # Get the body
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_dispo = str(part.get("Content-Disposition"))

                    if content_type == "text/plain" and "attachment" not in content_dispo:
                        body = part.get_payload(decode=True).decode()
                        print("Body:", body)
            else:
                body = msg.get_payload(decode=True).decode()
                print("Body:", body)

            # Mark as read
            imap.store(e_id, "+FLAGS", "\\Seen")

        # Logout
        imap.logout()

        return body



def call_ollama(prompt_text: str):
    url = "http://host.docker.internal:11434/v1/completions"  # use host.docker.internal if inside container
    payload = {
        "model": "llama3.2",
        "messages": [
            {"role": "system", "content": "You are a task extraction assistant."},
            {"role": "user", "content": prompt_text}
        ]
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json=payload)
    print(resp.text)
    resp.raise_for_status()
    return resp.json()["choices"][0]["text"]

def extract_tasks_from_text(text: str, db: Session) -> List[TaskCreate]:

    mlflow.set_experiment("email_task_extraction")
    tasks = []

    with mlflow.start_run(run_name=f"extract_tasks_{datetime.utcnow().isoformat()}"):
        mlflow.log_text(text, "input_email.txt")

        try:
            prompt = f"""
                You are a task extraction assistant.
                From the text below, extract all actionable tasks as a JSON array.
                Each task should include:
                    - title
                    - description
                    - priority (low/medium/high)
                    - due_date (ISO format or null)
                    - assignee (email or null)

                Text:
                \"\"\"
                {text}
                \"\"\"
                """
            print(prompt)
            response_str = call_ollama(prompt)
            print("Raw Ollama response:", response_str)

            # Parse JSON safely
            try:
                raw_tasks = json.loads(response_str)
            except json.JSONDecodeError:
                print("Failed to parse Ollama response as JSON. Wrapping raw text.")
                raw_tasks = [{"title": "Review extracted task", "description": response_str, "priority": "medium", "due_date": None, "assignee": None}]

            # Validate with Pydantic / DSPy schema
            for item in raw_tasks:
                try:
                    task = TaskSchema(**item)
                    tasks.append(task)
                except Exception as e:
                    print("Validation error:", e)

            # Save tasks to Postgres
            for task in tasks:
                crud.create_task(db, models.Task(**task.dict()))

            # Notify stakeholders
            for task in tasks:
                if task.assignee:
                    slack.send_slack_notification(task)
                    # email.send_task_notification(task)  # optional

            # Log metrics
            mlflow.log_metric("num_tasks_extracted", len(tasks))
            mlflow.log_text(str(tasks), "validated_tasks.json")


        # try:
        #     # Extract tasks using DSPy
        #     output = module(text=text)
        #     raw_tasks = output.tasks
        #     mlflow.log_text(str(raw_tasks), "raw_tasks.txt")

        #     # Validate with Pydantic
        #     for item in raw_tasks:
        #         try:
        #             task = TaskSchema(**item)
        #             tasks.append(task)
        #         except Exception as e:
        #             print("Validation error:", e)

        #     # Log metrics
        #     mlflow.log_metric("num_tasks_extracted", len(tasks))
        #     print(tasks)
        #     # Save tasks to PostgreSQL
        #     for task in tasks:
        #         crud.create_task(db, models.Task(**task.dict()))

        #     # Notify stakeholders
        #     for task in tasks:
        #         if task.assignee:
        #             slack.send_task_notification(task)
        #             # email.send_task_notification(task) @TODO: implement email notifications

        except Exception as e:
            print("DSPy extraction failed:", e)
            mlflow.log_text(str(e), "error.log")

    return tasks

    # agent = run(
    #     output_schema=TasksOutput,
    #     model_name="llama3.2",
    #     system_prompt="""
    #         You are a task extraction assistant.
    #         Extract all actionable tasks from the input text as JSON.
    #         Each task must include: title, description, priority (low/medium/high), due_date, assignee.
    #         """
    # )

    # try:
    #     # DSPy internally sends text to LLaMA and validates output
    #     result = agent.run(text=text)
    #     tasks_data = result.tasks
    # except Exception as e:
    #     print("DSPy validation failed:", e)
    #     return [
    #         TaskCreate(
    #             title="Review extracted task",
    #             description=text[:200],
    #             priority="medium",
    #             due_date=None,
    #             assignee=None,
    #         )
    #     ]

    # # Convert DSPy output to TaskCreate objects
    # tasks = []
    # for t in tasks_data:
    #     tasks.append(
    #         TaskCreate(
    #             title=t.title,
    #             description=t.description,
    #             priority=t.priority,
    #             due_date=t.due_date,
    #             assignee=t.assignee,
    #         )
    #     )

    # return tasks


# def extract_tasks_from_text_old(text: str) -> list[TaskCreate]:
#     prompt = f"""
#         You are a task extraction assistant.
#         From the text below, extract all actionable tasks as a JSON array.
#         Each task should include: title, description, priority (low/medium/high), due_date (ISO format or null), assignee (email or null).
#         Text:
#         \"\"\"
#         {text}
#         \"\"\"
#     """

#     try:
#         print("PROMPT SENT TO LLAMA:\n", prompt)
#         response = chat(
#             model="llama3.2",  # or your local model name
#             messages=[{"role": "user", "content": prompt}]
#         )
#         print("LLAMA RAW RESPONSE:\n", response["message"]["content"])
#         tasks_data = json.loads(response["message"]["content"])
#     except Exception as e:
#         print("LLM extraction failed:", e)
#         return [
#             TaskCreate(
#                 title="Review extracted task",
#                 description=text[:200],
#                 priority="medium",
#                 due_date=None,
#                 assignee=None,
#             )
#         ]

#     tasks = []
#     for t in tasks_data:
#         tasks.append(
#             TaskCreate(
#                 title=t.get("title", "Untitled Task"),
#                 description=t.get("description"),
#                 priority=t.get("priority", "medium"),
#                 due_date=datetime.fromisoformat(t["due_date"]) if t.get("due_date") else None,
#                 assignee=t.get("assignee"),
#             )
#         )
#     return tasks
