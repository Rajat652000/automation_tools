from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):

    list_display = (
        "business_name",
        "category",
        "location",
        "has_website",
        "email",
        "phone",
        "created_at",
    )

    list_filter = (
        "has_website",
        "category",
        "location",
    )

    search_fields = (
        "business_name",
        "email",
        "phone",
        "location",
    )