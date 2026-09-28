import os
import requests
import time

def send_message(to_phone, body, image_url=""):
    if os.getenv("WHATSAPP_ENABLED", "false").lower() != "true":
        raise RuntimeError("WhatsApp sending is disabled")
    version = os.environ.get("WHATSAPP_GRAPH_VERSION", "v23.0")
    response = requests.post(
        f"https://graph.facebook.com/{version}/{os.environ['WHATSAPP_PHONE_NUMBER_ID']}/messages",
        headers={"Authorization": f"Bearer {os.environ['WHATSAPP_ACCESS_TOKEN']}"},
        json=(
            {"messaging_product": "whatsapp", "to": "".join(c for c in to_phone if c.isdigit()), "type": "image", "image": {"link": image_url, "caption": body}}
            if image_url else
            {"messaging_product": "whatsapp", "to": "".join(c for c in to_phone if c.isdigit()), "type": "text", "text": {"body": body}}
        ),
        timeout=30,
    )
    response.raise_for_status()


def send_bulk_messages(recipients, body, delay_seconds=3, max_batch=50, image_url=""):
    recipients = [item.strip() for item in recipients if item.strip()][:max_batch]
    sent, failed = [], []
    for index, recipient in enumerate(recipients):
        try:
            send_message(recipient, body, image_url=image_url)
            sent.append(recipient)
        except Exception as error:
            failed.append({"recipient": recipient, "error": str(error)})
        if index < len(recipients) - 1:
            time.sleep(max(0, float(delay_seconds)))
    return sent, failed
