import json
from django.shortcuts import render
from .services import send_bulk_emails

def home(request):
    result = ""
    imported = ""
    if request.method == "POST":
        if request.FILES.get("json_file"):
            try:
                records = json.load(request.FILES["json_file"])
                if not isinstance(records, list):
                    raise ValueError("JSON root must be an array")
                imported = "\n".join(str(item.get("email", "")).strip() for item in records if isinstance(item, dict) and item.get("email"))
                result = f"Imported {len(imported.splitlines())} email contacts. Review and submit again."
            except Exception as error:
                result = f"JSON import failed: {error}"
        elif not request.POST.get("consent"):
            result = "Consent confirmation is required."
        else:
            try:
                recipients = request.POST["recipients"].splitlines()
                sent, failed = send_bulk_emails(
                    recipients, request.POST["subject"], request.POST["body"],
                    request.POST.get("delay", "2"),
                )
                result = f"Sent: {len(sent)} | Failed: {len(failed)}"
            except Exception as error:
                result = f"Email failed: {error}"
    return render(request, "email_tool/home.html", {"result": result, "imported": imported})
