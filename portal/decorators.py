from functools import wraps
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.exceptions import PermissionDenied
from .models import ToolAccess


def tool_access(tool):
    def decorator(view):
        @wraps(view)
        @never_cache
        @login_required(login_url="/login/")
        def wrapped(request, *args, **kwargs):
            if request.user.is_superuser or ToolAccess.objects.filter(user=request.user, tool=tool).exists():
                return view(request, *args, **kwargs)
            raise PermissionDenied("You do not have access to this tool.")
        return wrapped
    return decorator
