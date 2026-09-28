# Outreach Campaign Setup

This project can support three delivery channels:

| Channel | Recommended integration | Automatic sending |
|---|---|---|
| Email | User-owned SMTP or OAuth provider | Yes, within provider limits |
| WhatsApp | Official WhatsApp Business Cloud API | Yes, with opt-in/templates |
| SMS | Official SMS gateway API | Yes, provider/carrier limits apply |

WhatsApp Web/browser automation is intentionally not used. Delays do not make
unofficial automation safe or compliant and can result in a blocked number.

## Common safety requirements

Every contact must have explicit permission for the selected channel. The app
should store `email_opt_in`, `whatsapp_opt_in`, and `sms_opt_in` separately.
Do not send to a channel when its opt-in flag is false. Every campaign must
support unsubscribe/opt-out and keep a message log with `pending`, `sent`,
`failed`, and `unsubscribed` states.

Use small batches and provider-approved rate limits. Never put secrets in
Python files, templates, Git, CSV exports, or browser JavaScript.

## Environment configuration

Copy the project environment template when the campaign module is enabled:

```powershell
Copy-Item .env.example .env
```

The values below are examples only. Use an app password/OAuth token rather
than a normal mailbox password.

```dotenv
# Email: SMTP option
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-address@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=your-address@gmail.com

# WhatsApp Cloud API
WHATSAPP_ENABLED=false
WHATSAPP_GRAPH_VERSION=v23.0
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_BUSINESS_ACCOUNT_ID=
WHATSAPP_ACCESS_TOKEN=

# SMS provider (provider-specific; Twilio shown as an example)
SMS_ENABLED=false
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=
```

## Gmail SMTP setup

1. Use a Gmail/Google Workspace account dedicated to campaigns.
2. Enable 2-Step Verification on the Google account.
3. Open Google Account → Security → 2-Step Verification → App passwords.
4. Create an app password for Mail. Google shows a 16-character password once.
5. Put that app password in `EMAIL_HOST_PASSWORD`; do not use the normal Gmail
   password.
6. Use `smtp.gmail.com`, port `587`, TLS enabled.
7. Send a test email to yourself before any batch.

Provider limits still apply. Free mailbox SMTP is suitable for small,
consent-based batches, not high-volume marketing.

## Microsoft/Outlook SMTP setup

Use the mailbox/provider's approved SMTP or OAuth settings. Common Outlook
settings are `smtp.office365.com`, port `587`, STARTTLS, but an administrator
may need to enable authenticated SMTP. If SMTP AUTH is disabled, use Microsoft
Graph OAuth instead of trying to bypass the restriction.

## WhatsApp Cloud API setup

1. Create/log in to a Meta for Developers account.
2. Create a Meta Business app and add the WhatsApp product.
3. Create/select a WhatsApp Business Account and add a business phone number.
4. In WhatsApp → API Setup, note the Phone Number ID and Business Account ID.
5. Create a system user in Business Manager and grant WhatsApp management and
   messaging permissions.
6. Generate a long-lived access token and store it only in `.env`.
7. Add and verify recipient test numbers during development.
8. Create and submit message templates for business-initiated messages.
9. Configure the webhook URL and verify token for delivery/read/failure events.
10. Move from test mode to production only after opt-in, privacy and opt-out
    flows are working.

The API endpoint is conceptually:

```text
POST https://graph.facebook.com/<GRAPH_VERSION>/<PHONE_NUMBER_ID>/messages
Authorization: Bearer <ACCESS_TOKEN>
```

Business-initiated conversations normally require an approved template. The
recipient's phone number alone is not permission to message them.

## SMS setup

Choose an official gateway available in the target country. Examples include
Twilio, MSG91, Textlocal, Vonage, and AWS SNS. The provider dashboard supplies
the API credentials, sender ID/number, delivery webhook and country-specific
compliance requirements.

For Twilio:

1. Create and verify an account.
2. Buy or enable an SMS-capable sender number.
3. Copy Account SID and Auth Token from the console.
4. Put them in `.env` and keep the account in test mode initially.
5. Register templates/sender IDs where local regulations require it.
6. Configure status callbacks for delivered, failed and undelivered messages.

SMS is generally paid per message. A free trial may restrict destination
numbers and include provider branding; it is not an unlimited free service.

## Recommended product flow

```text
Import leads (CSV/JSON)
        ↓
Validate contact and consent per channel
        ↓
Create campaign and personalize template
        ↓
Preview and send a test to the owner
        ↓
Start a rate-limited batch
        ↓
Record provider message ID/status
        ↓
Process delivery and opt-out webhooks
```

## Implementation order

1. Add contact consent and unsubscribe fields.
2. Add campaign/message-log models.
3. Implement email test-send and small batch sender.
4. Add retry/idempotency and provider status logging.
5. Add WhatsApp Cloud API templates and webhook handling.
6. Add SMS provider adapter and delivery callbacks.
7. Add admin screens, campaign pause/resume, exports and audit logs.

## Local verification

Before enabling a real provider:

```powershell
python manage.py check
python manage.py test
```

Use a test recipient, a one-message batch, and `*_ENABLED=false` by default.
