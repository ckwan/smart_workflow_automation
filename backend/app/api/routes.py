from fastapi import APIRouter
from app.api.schemas import EmailIngestRequest
from app.workers.tasks import process_message
from app.workers.ai_pipeline import get_new_emails
router = APIRouter()


@router.post("/ingest")
async def ingest_message(payload: EmailIngestRequest):
    """
    Entry point for emails / webhooks.
    """

    get_new_emails();

    process_message.delay(payload.dict())
    return {"status": "queued"}
