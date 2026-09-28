# WhatsApp bulk implementation checklist

The current `/whatsapp/` page sends one API test message. Production bulk
sending must use the official Cloud API:

1. Add contacts with `whatsapp_opt_in` and `unsubscribed` fields.
2. Add approved WhatsApp template name/language fields to campaigns.
3. Preview and send only to opted-in test numbers first.
4. Queue messages with a provider-safe rate limit.
5. Store Meta message IDs and process delivery/read/failure webhooks.
6. Implement STOP/opt-out handling and suppression.
7. Add campaign pause/resume and retry for transient errors.

Do not replace this with WhatsApp Web or Playwright automation. Delays do not
make unofficial bulk automation safe and can get the number blocked.
