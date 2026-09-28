import os
import time
from twilio.rest import Client

def send_sms(to_phone, body):
    if os.getenv("SMS_ENABLED", "false").lower() != "true":
        raise RuntimeError("SMS sending is disabled")
    Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"]).messages.create(
        body=body, from_=os.environ["TWILIO_FROM_NUMBER"], to=to_phone.strip()
    )


def send_bulk_sms(recipients, body, delay_seconds=2, max_batch=50):
    recipients = [item.strip() for item in recipients if item.strip()][:max_batch]
    sent, failed = [], []
    for index, recipient in enumerate(recipients):
        try:
            send_sms(recipient, body)
            sent.append(recipient)
        except Exception as error:
            failed.append({"recipient": recipient, "error": str(error)})
        if index < len(recipients) - 1:
            time.sleep(max(0, float(delay_seconds)))
    return sent, failed
