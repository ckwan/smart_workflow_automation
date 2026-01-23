import requests
from app.core.config import settings


def send_slack_notification(message: str) -> bool:
    """
    Sends a message to Slack using a webhook URL.
    Returns True if successful.
    """
    webhook_url = settings.SLACK_WEBHOOK_URL
    if not webhook_url:
        return Exception("Slack webhook not configured.")

    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Slack notification failed: {e}")
        return False
