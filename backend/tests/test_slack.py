from unittest.mock import patch, MagicMock

import pytest
from app.notifications.slack import send_slack_notification

# def test_send_slack_notification():
#     result = send_slack_notification("Hello from Smart Workflow Automation!")
#     print(result)
#     if result:
#         assert True
#     else:
#         assert False


def test_send_slack_message_success():
    with patch("app.notifications.slack.requests.post") as mock_post:
        # Mock the response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = send_slack_notification("Hello, Slack!")
        mock_post.assert_called_once()  # ensure post was called
        args, kwargs = mock_post.call_args
        assert "json" in kwargs
        assert kwargs["json"]["text"] == "Hello, Slack!"
        assert result is True


# def test_send_slack_message_failure(monkeypatch):
#     with patch("app.notifications.slack.requests.post") as mock_post:
#         mock_post.side_effect = Exception("Slack webhook not configured")
#         with pytest.raises(Exception) as exc_info:
#             # Remove webhook for this test
#             monkeypatch.setattr("app.core.config.settings.SLACK_WEBHOOK_URL", None)

#             send_slack_notification("Hello, Slack!")
#         assert "Slack webhook not configured." in str(exc_info.value)
