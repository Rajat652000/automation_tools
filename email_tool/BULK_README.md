# Email bulk implementation checklist

The current `/email/` page sends one test email. To turn it into a real bulk
tool, add these pieces in this app only:

1. `Contact` model with email, name, `email_opt_in`, and `unsubscribed`.
2. `Campaign` model with subject, body, status, and timestamps.
3. `MessageLog` model with contact, status, provider error, and sent time.
4. CSV/JSON import with duplicate and email validation.
5. Preview and one-recipient test send before batch start.
6. Queue worker (Celery/RQ or a controlled management command) with a rate
   limit; never send all messages in one web request.
7. Unsubscribe link and suppression list.
8. Retry only transient failures and make sends idempotent.

Gmail/Outlook free accounts have provider sending limits; this is not an
unlimited free marketing channel.
