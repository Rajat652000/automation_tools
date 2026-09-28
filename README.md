# Automation Tools Platform

## Overview

`automation_tools` is a modular Django platform for business lead discovery,
contact-data extraction, consent-based email, WhatsApp, SMS campaigns, and an
inbound WhatsApp chatbot.

```text
Business discovery -> Contact extraction -> Consent-based campaigns
                   -> Email / WhatsApp / SMS -> Logs and follow-up
```

The applications are independent so the scraper, outbound messaging tools,
and chatbot can be maintained separately.

## Business idea

The platform is intended for marketing agencies, sales teams, local
businesses, recruitment teams, event organizers, and service providers. A
user discovers businesses, extracts contact details, exports leads as CSV or
JSON, and communicates only with recipients who have provided consent.

## Applications

### `web_scraper` — lead discovery

URL: `http://127.0.0.1:8000/scraper/`

Uses Google Places API and official business websites to collect business name,
category, address, website, email, phone, social links, source URL, and Place
ID. It supports CSV export at `/scraper/export/` and JSON export at
`/scraper/export/json/`.

Main files:

```text
web_scraper/models.py       Lead database model
web_scraper/services.py     Search, crawling, and extraction logic
web_scraper/views.py        Search jobs and exports
web_scraper/templates/      Scraper UI
```

### `email_tool` — SMTP email campaigns

URL: `http://127.0.0.1:8000/email/`

Supports multiple recipients, JSON import using the `email` field, subject,
message, delay, consent confirmation, and batches of up to 50 recipients.

Gmail setup:

1. Enable 2-Step Verification.
2. Create a Google App Password.
3. Do not use the normal Gmail password.
4. Add this to `.env`:

```dotenv
EMAIL_ENABLED=false
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### `whatsapp_tool` — WhatsApp Cloud API campaigns

URL: `http://127.0.0.1:8000/whatsapp/`

Uses the official Meta WhatsApp Cloud API. It supports phone-number JSON
import, approved message templates, batch delay, consent confirmation, and
public image URLs.

Meta setup:

1. Create a Meta for Developers account and application.
2. Add WhatsApp and configure a WhatsApp Business Account.
3. Copy the Phone Number ID and Business Account ID.
4. Generate an access token.
5. Add test recipients and create approved templates.

```dotenv
WHATSAPP_ENABLED=false
WHATSAPP_GRAPH_VERSION=v23.0
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_BUSINESS_ACCOUNT_ID=
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_WEBHOOK_VERIFY_TOKEN=
```

WhatsApp Web and Playwright automation are not used.

### `sms_tool` — SMS campaigns

URL: `http://127.0.0.1:8000/sms/`

Uses an official SMS provider, currently Twilio. It supports phone-number JSON
import, batch delay, consent confirmation, and public image URLs. Normal SMS
does not support photo attachments; MMS or an image URL is required.

```dotenv
SMS_ENABLED=false
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=
```

### `whatsapp_bot` — inbound WhatsApp chatbot

Webhook: `http://127.0.0.1:8000/webhook/`

The chatbot receives Meta webhook messages, matches active `ChatbotRule`
records, sends an official API reply, and stores `Conversation` records.
Rules can be managed at `/admin/`.

For Meta webhook development, expose Django through HTTPS:

```powershell
ngrok http 8000
```

Use `https://YOUR-NGROK-URL/webhook/` as the Meta callback URL and use the
same value for the Meta verify token and `WHATSAPP_WEBHOOK_VERIFY_TOKEN`.
Subscribe to the `messages` webhook field. Opening `/webhook/` directly in a
browser may return `403`; that is expected without Meta verification query
parameters.

## JSON input format

```json
[
  {
    "name": "ABC Salon",
    "email": "abc@example.com",
    "phone": "919876543210"
  }
]
```

The email tool reads `email`; WhatsApp and SMS read `phone`; `name` is reserved
for future personalization.

## Installation

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py runserver
```

Applications:

```text
http://127.0.0.1:8000/scraper/
http://127.0.0.1:8000/email/
http://127.0.0.1:8000/whatsapp/
http://127.0.0.1:8000/sms/
```

Keep all providers disabled until configuration is verified:

```dotenv
EMAIL_ENABLED=false
WHATSAPP_ENABLED=false
SMS_ENABLED=false
ENABLE_TAVILY=false
```

## Security and compliance

- Never commit `.env` or credentials to Git.
- Send only to opted-in recipients.
- Provide unsubscribe and STOP/opt-out handling.
- Use approved WhatsApp templates.
- Respect provider rate limits and batch limits.
- Keep delivery, failure, and opt-out logs.
- Use a background queue for production campaigns.
- Do not use WhatsApp Web automation for bulk sending.

## Roadmap

- Consent and contact database
- Campaign and message-log models
- CSV/JSON validation and deduplication
- Name personalization
- Email attachments and WhatsApp media upload
- Background queues, retry, pause/resume
- Delivery webhooks and campaign analytics
- Multi-user authentication and permissions

## Technology stack

```text
Python, Django, SQLite, Requests, BeautifulSoup,
Google Places API, SMTP, WhatsApp Cloud API, Twilio SMS API, HTML/CSS
```
