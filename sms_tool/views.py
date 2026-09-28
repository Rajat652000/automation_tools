import json
from django.shortcuts import render
from .services import send_bulk_sms

def home(request):
    result = ""
    imported = ""
    if request.method == "POST":
        if request.FILES.get("json_file"):
            try:
                records = json.load(request.FILES["json_file"])
                if not isinstance(records, list):
                    raise ValueError("JSON root must be an array")
                imported = "\n".join(str(item.get("phone", "")).strip() for item in records if isinstance(item, dict) and item.get("phone"))
                result = f"Imported {len(imported.splitlines())} phone contacts. Review and submit again."
            except Exception as error:
                result = f"JSON import failed: {error}"
        elif not request.POST.get("consent"):
            result = "SMS opt-in confirmation is required."
        else:
            try:
                body = request.POST["body"]
                if request.POST.get("image_url", "").strip():
                    body += f"\n\nPhoto: {request.POST['image_url'].strip()}"
                sent, failed = send_bulk_sms(
                    request.POST["recipients"].splitlines(), body,
                    request.POST.get("delay", "2"),
                )
                result = f"Sent: {len(sent)} | Failed: {len(failed)}"
            except Exception as error:
                result = f"SMS send failed: {error}"
    return render(request, "sms_tool/home.html", {"result": result, "imported": imported})
