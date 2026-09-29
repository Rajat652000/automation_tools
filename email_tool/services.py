import os
import smtplib
import time
from email.message import EmailMessage

def send_email(to_email, subject, body, profile=None, attachment=None):
    if profile is None and os.getenv("EMAIL_ENABLED", "false").lower() != "true":
        raise RuntimeError("Email sending is disabled")
    host = profile.host if profile else os.getenv("EMAIL_HOST", "smtp.gmail.com")
    port = profile.port if profile else int(os.getenv("EMAIL_PORT", "587"))
    username = profile.username if profile else os.environ["EMAIL_HOST_USER"]
    password = profile.app_password if profile else os.environ["EMAIL_HOST_PASSWORD"]
    sender = profile.from_email if profile else os.environ["DEFAULT_FROM_EMAIL"]
    message = EmailMessage()
    message["From"] = sender
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)
    if attachment:
        filename, content, content_type = attachment
        maintype, subtype = content_type.split("/", 1)
        message.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)
    with smtplib.SMTP(host, int(port), timeout=30) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)


def send_bulk_emails(recipients, subject, body, delay_seconds=2, max_batch=50, profile=None, attachment=None):
    recipients = [item.strip() for item in recipients if item.strip()][:max_batch]
    sent, failed = [], []
    for index, recipient in enumerate(recipients):
        try:
            send_email(recipient, subject, body, profile=profile, attachment=attachment)
            sent.append(recipient)
        except Exception as error:
            failed.append({"recipient": recipient, "error": str(error)})
        if index < len(recipients) - 1:
            time.sleep(max(0, float(delay_seconds)))
    return sent, failed
