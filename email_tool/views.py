import json
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render
from .services import send_bulk_emails
from .models import EmailProfile, EmailSendLog, EmailSuppression
from portal.decorators import tool_access

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+")


def extract_emails(value):
    """Find email addresses anywhere in nested JSON, regardless of field name."""
    found = []
    if isinstance(value, dict):
        for item in value.values():
            found.extend(extract_emails(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(extract_emails(item))
    elif isinstance(value, str):
        found.extend(EMAIL_PATTERN.findall(value))
    return list(dict.fromkeys(email.strip().lower() for email in found))

@tool_access("email")
def home(request):
    result = ""
    imported = ""
    if request.method == "POST":
        if request.FILES.get("json_file"):
            try:
                records = json.load(request.FILES["json_file"])
                emails = extract_emails(records)
                imported = "\n".join(emails)
                result = f"Found {len(emails)} unique email contacts anywhere in the JSON. Review and submit again."
            except Exception as error:
                result = f"JSON import failed: {error}"
        elif not request.POST.get("consent"):
            result = "Consent confirmation is required."
        else:
            try:
                recipients = list(dict.fromkeys(x.strip().lower() for x in request.POST["recipients"].splitlines() if x.strip()))
                blocked = set(EmailSuppression.objects.values_list("email", flat=True))
                recipients = [x for x in recipients if x not in blocked]
                for recipient in recipients:
                    try:
                        validate_email(recipient)
                    except ValidationError:
                        raise ValueError(f"Invalid email address: {recipient}")
                profile = getattr(request.user, "email_profile", None)
                attachment_file = request.FILES.get("attachment")
                attachment = None
                if attachment_file:
                    if attachment_file.size > 10 * 1024 * 1024:
                        raise ValueError("Attachment must be 10 MB or smaller")
                    attachment = (attachment_file.name, attachment_file.read(), attachment_file.content_type or "application/octet-stream")
                sent, failed = send_bulk_emails(
                    recipients, request.POST["subject"], request.POST["body"],
                    request.POST.get("delay", "2"), profile=profile, attachment=attachment,
                )
                EmailSendLog.objects.bulk_create([EmailSendLog(recipient=e, subject=request.POST["subject"], status="sent", sent_by=request.user) for e in sent] + [EmailSendLog(recipient=e["recipient"], subject=request.POST["subject"], status="failed", error=e["error"], sent_by=request.user) for e in failed])
                result = f"Sent: {len(sent)} | Failed: {len(failed)}"
            except Exception as error:
                result = f"Email failed: {error}"
    return render(request, "email_tool/home.html", {"result": result, "imported": imported})
