from django.shortcuts import redirect
from .models import ToolAccess


class ToolRouteMiddleware:
    """Protect the scraper route without changing the web_scraper app."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/scraper/"):
            if not request.user.is_authenticated:
                return redirect("/login/")
            if not request.user.is_superuser and not ToolAccess.objects.filter(user=request.user, tool="scraper").exists():
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("You do not have access to this tool.")
        return self.get_response(request)
