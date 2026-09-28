import os
import smtplib
import time
from email.message import EmailMessage

def send_email(to_email, subject, body):
    if os.getenv("EMAIL_ENABLED", "false").lower() != "true":
        raise RuntimeError("Email sending is disabled")
    message = EmailMessage()
    message["From"] = os.environ["DEFAULT_FROM_EMAIL"]
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)
    with smtplib.SMTP(os.environ.get("EMAIL_HOST", "smtp.gmail.com"), int(os.environ.get("EMAIL_PORT", "587")), timeout=30) as smtp:
        smtp.starttls()
        smtp.login(os.environ["EMAIL_HOST_USER"], os.environ["EMAIL_HOST_PASSWORD"])
        smtp.send_message(message)


def send_bulk_emails(recipients, subject, body, delay_seconds=2, max_batch=50):
    recipients = [item.strip() for item in recipients if item.strip()][:max_batch]
    sent, failed = [], []
    for index, recipient in enumerate(recipients):
        try:
            send_email(recipient, subject, body)
            sent.append(recipient)
        except Exception as error:
            failed.append({"recipient": recipient, "error": str(error)})
        if index < len(recipients) - 1:
            time.sleep(max(0, float(delay_seconds)))
    return sent, failed
