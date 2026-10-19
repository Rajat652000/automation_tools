from django.shortcuts import redirect
from .models import ToolAccess


class ToolRouteMiddleware:
    """Protect the scraper route without changing the web_scraper app."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # The Django admin exposes cross-user records and credentials, so keep
        # it restricted to superusers rather than any account marked staff.
        if request.path.startswith("/admin/"):
            if not request.user.is_authenticated:
                return redirect("/login/")
            if not request.user.is_superuser:
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("Administrator access is restricted to superusers.")
        if request.path.startswith("/scraper/"):
            if not request.user.is_authenticated:
                return redirect("/login/")
            if not request.user.is_superuser and not ToolAccess.objects.filter(user=request.user, tool="scraper").exists():
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("You do not have access to this tool.")
        return self.get_response(request)
