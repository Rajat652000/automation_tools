from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("business_name", "owner", "email", "phone", "category", "created_at")
    list_filter = ("owner", "category", "created_at")
    search_fields = ("business_name", "email", "phone", "owner__username", "owner__email")
    list_select_related = ("owner",)
    list_editable = ("owner",)
