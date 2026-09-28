import json
from django.shortcuts import render
from .services import send_bulk_messages

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
            result = "WhatsApp opt-in confirmation is required."
        else:
            try:
                body = request.POST["body"]
                if request.POST.get("image_url", "").strip():
                    body += f"\n\nPhoto: {request.POST['image_url'].strip()}"
                sent, failed = send_bulk_messages(
                    request.POST["recipients"].splitlines(), body,
                    request.POST.get("delay", "3"),
                    image_url=request.POST.get("image_url", "").strip(),
                )
                result = f"Sent: {len(sent)} | Failed: {len(failed)}"
            except Exception as error:
                result = f"WhatsApp send failed: {error}"
    return render(request, "whatsapp_tool/home.html", {"result": result, "imported": imported})
