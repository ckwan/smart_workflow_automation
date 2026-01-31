import smtplib
from email.message import EmailMessage
from app.core.config import settings


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Sends an email via SMTP.
    """
    msg = EmailMessage()
    msg["From"] = settings.SMTP_USER  # <-- used as "From" header
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()  # secure connection
            server.login(settings.SMTP_USER, settings.SMTP_PASS)  # <-- used for SMTP authentication
            server.send_message(msg)  # actually sends the email
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

