from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.core.management import call_command
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.utils import timezone
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import django
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


@login_required
@require_GET
@never_cache
def download_backup(request):
    """Create a private, full data archive for a superuser."""
    if not request.user.is_superuser:
        raise PermissionDenied

    created_at = timezone.now()
    stamp = created_at.strftime("%Y%m%d_%H%M%S")
    temp_dir = tempfile.TemporaryDirectory(prefix="automation_tools_backup_")
    work = Path(temp_dir.name)
    fixture_path = work / "data.json"
    sqlite_path = work / "database.sqlite3"
    zip_path = work / f"automation_tools_backup_{stamp}.zip"

    try:
        with fixture_path.open("w", encoding="utf-8") as fixture:
            call_command(
                "dumpdata",
                format="json",
                indent=2,
                use_natural_foreign_keys=True,
                use_natural_primary_keys=True,
                exclude=["sessions.session"],
                stdout=fixture,
            )

        included_files = ["data.json", "README.txt"]
        if connection.vendor == "sqlite":
            connection.ensure_connection()
            destination = sqlite3.connect(sqlite_path)
            try:
                connection.connection.backup(destination)
            finally:
                destination.close()
            included_files.append("database.sqlite3")

        media_root_value = getattr(settings, "MEDIA_ROOT", "")
        media_root = Path(media_root_value) if media_root_value else None
        media_included = bool(media_root and media_root.is_dir() and any(media_root.iterdir()))
        if media_included:
            included_files.append("media/")

        manifest = {
            "created_at": created_at.isoformat(),
            "django_version": django.get_version(),
            "database_engine": settings.DATABASES["default"]["ENGINE"],
            "files": included_files,
            "notes": [
                "data.json is the portable Django fixture for migration to another database.",
                "database.sqlite3 is an exact database snapshot and is present only for SQLite.",
                "User password hashes and configured email SMTP credentials are included as application data.",
                "Environment files, API keys, Django SECRET_KEY, and runtime secrets are excluded.",
            ],
        }
        readme = (
            "Automation Tools backup\n\n"
            "Cross-database restore: use the matching application code, configure the destination database, "
            "run `python manage.py migrate`, then `python manage.py loaddata data.json`.\n"
            "SQLite restore: stop the application and replace db.sqlite3 with database.sqlite3.\n"
            "If media/ exists, restore it to the configured MEDIA_ROOT. Review environment configuration "
            "separately; it is intentionally not included.\n\n"
            "This archive contains sensitive user information, password hashes, and possibly SMTP credentials. "
            "Store and transfer it securely.\n"
        )
        (work / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        (work / "README.txt").write_text(readme, encoding="utf-8")

        with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
            archive.write(fixture_path, "data.json")
            archive.write(work / "manifest.json", "manifest.json")
            archive.write(work / "README.txt", "README.txt")
            if sqlite_path.exists():
                archive.write(sqlite_path, "database.sqlite3")
            if media_included:
                assert media_root is not None
                for item in media_root.rglob("*"):
                    if item.is_file():
                        archive.write(item, (Path("media") / item.relative_to(media_root)).as_posix())

        response = FileResponse(
            zip_path.open("rb"),
            as_attachment=True,
            filename=zip_path.name,
            content_type="application/zip",
        )
        response["Cache-Control"] = "private, no-store"
        response["X-Content-Type-Options"] = "nosniff"
        response._resource_closers.append(temp_dir.cleanup)
        return response
    except Exception:
        temp_dir.cleanup()
        raise
