# WhatsApp Webhook Chatbot

This app handles inbound WhatsApp Cloud API webhook events and replies using
the configured `ChatbotRule` records. It is separate from `whatsapp_tool`,
which is for outbound consent-based campaign messages.

## Local setup

Set these values in the root `.env`:

```dotenv
WHATSAPP_ENABLED=false
WHATSAPP_GRAPH_VERSION=v23.0
WHATSAPP_WEBHOOK_VERIFY_TOKEN=create-your-own-random-token
WHATSAPP_ACCESS_TOKEN=meta-access-token
WHATSAPP_PHONE_NUMBER_ID=meta-phone-number-id
```

Keep `WHATSAPP_ENABLED=false` until the Meta test number and webhook are
configured. Run the server with:

```powershell
python manage.py runserver
```

## Meta webhook setup

1. Create a Meta developer app and add WhatsApp.
2. In WhatsApp configuration, set the callback URL to a public HTTPS URL:
   `https://your-domain.example/webhook/`.
3. Set the verify token to the same value as
   `WHATSAPP_WEBHOOK_VERIFY_TOKEN`.
4. Subscribe the app to the `messages` webhook field.
5. Add a test recipient and send a message to the business number.

The app exposes:

```text
GET/POST /webhook/
```

GET verifies Meta's challenge. POST reads incoming text, finds a matching
active `ChatbotRule`, sends the reply through the official Cloud API, and
stores a `Conversation` record.

## Add chatbot replies

Use Django admin:

```text
http://127.0.0.1:8000/admin/
```

Create a `ChatbotRule` with a keyword in `question` and the response in
`answer`. Keep rules specific and do not store secrets in answers.

## Production requirements

- HTTPS public webhook endpoint
- signature verification for webhook requests
- durable logging and idempotency for message IDs
- opt-out keywords such as STOP
- approved templates for business-initiated messages
- a production WSGI/ASGI server, not `runserver`
