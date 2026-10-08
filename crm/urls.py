from django.urls import path
from . import views

app_name = "crm"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("transactions/", views.transactions, name="transactions"),
    path("transactions/<int:transaction_id>/edit/", views.transaction_edit, name="transaction_edit"),
    path("customize/", views.customize, name="customize"),
    path("attendance/", views.attendance_dashboard, name="attendance_dashboard"),
    path("attendance/members/add/", views.add_attendance_member, name="add_attendance_member"),
    path("contacts/", views.contacts, name="contacts"),
    path("contacts/add/", views.contact_create, name="contact_create"),
    path("contacts/<int:contact_id>/", views.contact_detail, name="contact_detail"),
    path("contacts/<int:contact_id>/edit/", views.contact_edit, name="contact_edit"),
    path("contacts/<int:contact_id>/status/", views.contact_status_update, name="contact_status_update"),
    path("contacts/<int:contact_id>/delete/", views.contact_delete, name="contact_delete"),
    path("contacts/<int:contact_id>/attendance/", views.attendance, name="attendance"),
    path("import/csv/", views.import_csv, name="import_csv"),
    path("segments/", views.segments, name="segments"),
    path("bulk/", views.bulk_action, name="bulk_action"),
    path("tags/", views.tags, name="tags"),
    path("export/json/", views.export_json, name="export_json"),
    path("export/csv/", views.export_csv, name="export_csv"),
]
