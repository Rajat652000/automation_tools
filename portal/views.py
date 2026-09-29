from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from .models import ToolAccess


@never_cache
def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    tools = [key for key, _ in ToolAccess.TOOLS] if request.user.is_superuser else list(ToolAccess.objects.filter(user=request.user).values_list("tool", flat=True))
    return render(request, "portal/home.html", {"tools": tools})


@never_cache
def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("home")
    return render(request, "portal/login.html", {"form": form})


@never_cache
def logout_view(request):
    logout(request)
    response = redirect("login")
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    return response
