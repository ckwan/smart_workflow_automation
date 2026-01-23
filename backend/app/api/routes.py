from fastapi import APIRouter
from app.api.schemas import EmailIngestRequest
from app.workers.tasks import process_message

router = APIRouter()


@router.post("/ingest")
async def ingest_message(payload: EmailIngestRequest):
    """
    Entry point for emails / webhooks.
    """

    process_message.delay(payload.dict())
    return {"status": "queued"}
