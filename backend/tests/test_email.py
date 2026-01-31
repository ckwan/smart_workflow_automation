import pytest
from unittest.mock import patch, MagicMock
from app.notifications.email import send_email
from app.workers.ai_pipeline import get_new_emails
from app.core.config import settings


def test_retrieving_email():
    response = get_new_emails()

    assert isinstance(response, str)
    assert response  # not empty



@pytest.mark.skip(reason="Skipping this test for now")
def test_send_email_success():
    result = send_email(
        settings.SMTP_USER,
        "Test Email",
        "Hello! This is a test."
    )
    print("Email sent:", result)

    assert result is True

#     # Patch exactly where it's used
#     with patch("app.notifications.email.smtplib.SMTP") as mock_smtp:
#         # Get the instance returned by the context manager
#         instance = mock_smtp.return_value.__enter__.return_value
#         instance.send_email_notification.return_value = {}

#         result = send_email_notification("test@example.com", "Test Subject", "Hello World")

#         # Assert send_email_notification was called
#         instance.send_email_notification.assert_called_once()
#         # Function should return True
#         assert result is True


# def test_send_email_exception():
#     with patch("app.notifications.email.smtplib.SMTP") as mock_smtp:
#         instance = mock_smtp.return_value.__enter__.return_value
#         # Simulate exception
#         instance.send_email_notification.side_effect = Exception("SMTP error")
#         result = send_email_notification("test@example.com", "Test Subject", "Hello World")
#         # Function should return False
#         assert result is False
