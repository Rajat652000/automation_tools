# SMS bulk implementation checklist

The current `/sms/` page sends one Twilio test SMS. To make it a bulk tool:

1. Add contacts with `sms_opt_in` and `unsubscribed` fields.
2. Import and validate E.164 phone numbers.
3. Add campaign/template and message-log models.
4. Send through a queue worker, not inside a page request.
5. Configure delivery-status callbacks and record provider IDs.
6. Add STOP/opt-out handling and a suppression list.
7. Add batch limits, retry policy and pause/resume controls.

SMS delivery is provider/carrier billed and country-specific compliance may
require registered sender IDs or templates.
