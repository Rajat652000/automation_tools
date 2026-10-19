# Automation Tools

A Django platform for business lead discovery, CRM, and consent based email
campaigns.

## Modules

### Web scraper

Open `/scraper/` after signing in. The scraper searches business listings,
extracts publicly listed contact details from business websites, saves leads,
and supports CSV and JSON exports. Google Places and optional Tavily settings
are read from the environment.

Main files: `web_scraper/models.py` stores leads,
`web_scraper/services.py` performs search and extraction, and
`web_scraper/views.py` handles the UI and exports.

### CRM

Open `/crm/` after a user has CRM access. It provides contact management,
tags, segments, notes, import/export, attendance, staff attendance, and sales
and purchase records. The selected industry and modules can be configured per
user.

Main files: `crm/models.py` defines CRM records, `crm/views.py` contains the
module workflows, and `crm/urls.py` maps CRM pages.

### Email tool

Open `/email/` after a user has email access. It supports consent-confirmed
email campaigns, recipient imports, batching, and delivery logs. Configure SMTP
in `.env`; keep `EMAIL_ENABLED=false` until sending is intentionally enabled.

## Project layout

```text
config/       Django settings and root URLs
portal/       Login, tool access, and home page
web_scraper/  Business search, extraction, and lead exports
crm/          Contact management and business records
email_tool/   SMTP campaigns and email logs
```

The root routes are `/`, `/login/`, `/scraper/`, `/crm/`, `/email/`, and
`/admin/`. Tool access is managed through the portal's `ToolAccess` records;
superusers can access all tools.

## Setup

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cp .env.example .env  # Windows: Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Environment variables

Set `GOOGLE_MAPS_API_KEY` to enable Google Places search. Tavily enrichment is
optional and stays off unless `ENABLE_TAVILY=true` and `TAVILY_API_KEY` are
configured. Email uses `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`,
`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `DEFAULT_FROM_EMAIL`.

Never commit `.env` or send email to recipients who have not opted in. Use an
SMTP app password or provider approved credentials rather than an account's
normal password.

## Full backup and migration

Sign in as a superuser and select **Download full backup** on the home page.
The ZIP contains a portable `data.json` Django fixture, a manifest and restore
notes, and an exact `database.sqlite3` snapshot when the active database is
SQLite. If `MEDIA_ROOT` is configured and contains files, those are included
under `media/`.

To move to another database, deploy matching application code, configure the
destination database, run `python manage.py migrate`, and then
`python manage.py loaddata data.json`. For a SQLite restore, stop the app and
replace `db.sqlite3` with the archived snapshot. Restore `media/` to the
configured media directory if present. Keep the application version and schema
compatible when restoring.

The archive contains all users and application records, including password
hashes and configured SMTP credentials. Protect it like production credentials.
Environment files, API keys, Django `SECRET_KEY`, and runtime secrets are not
included; configure those separately on the destination.
