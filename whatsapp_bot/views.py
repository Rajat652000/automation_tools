import os
import requests

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from .models import ChatbotRule, Conversation

load_dotenv()

VERIFY_TOKEN = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN") or os.getenv("WHATSAPP_VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
GRAPH_VERSION = os.getenv("WHATSAPP_GRAPH_VERSION", "v23.0")


def find_reply(message):
    message = message.lower().strip()

    rules = ChatbotRule.objects.filter(active=True)

    for rule in rules:
        if rule.question.lower().strip() in message:
            return rule.answer

    return (
        "Sorry, mujhe aapka question samajh nahi aaya. 😅\n"
        "Aap Price, Location ya Timing ke baare mein pooch sakte hain."
    )


def send_whatsapp_message(phone_number, message):

    if os.getenv("WHATSAPP_ENABLED", "false").lower() != "true":
        raise RuntimeError("WhatsApp sending is disabled")

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_VERSION}/{PHONE_NUMBER_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=30
    )

    print("WhatsApp API:", response.status_code)
    print(response.text)

    return response


def webhook_verify(request):

    mode = request.GET.get("hub.mode")
    token = request.GET.get("hub.verify_token")
    challenge = request.GET.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return HttpResponse(challenge)

    return HttpResponse("Verification failed", status=403)


@csrf_exempt
def webhook(request):

    if request.method == "GET":
        return webhook_verify(request)

    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    data = request.body

    import json

    try:
        data = json.loads(data)

        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        messages = value.get("messages", [])

        if not messages:
            return JsonResponse({"status": "ignored"})

        message = messages[0]

        if message.get("type") != "text":
            return JsonResponse({
                "status": "unsupported_message"
            })

        phone_number = message["from"]
        incoming_message = message["text"]["body"]

        print("FROM:", phone_number)
        print("MESSAGE:", incoming_message)

        reply = find_reply(incoming_message)

        send_whatsapp_message(
            phone_number,
            reply
        )

        Conversation.objects.create(
            phone_number=phone_number,
            incoming_message=incoming_message,
            bot_reply=reply
        )

        return JsonResponse({
            "status": "success"
        })

    except Exception as error:

        print("ERROR:", error)

        return JsonResponse({
            "status": "error",
            "message": str(error)
        }, status=500)
