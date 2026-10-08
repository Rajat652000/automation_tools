from django.contrib import admin
from .models import Contact, Tag


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "company_name", "owner", "phone", "email", "status", "created_at")
    list_filter = ("owner", "status", "source")
    search_fields = ("name", "company_name", "phone", "email", "owner__username")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    list_filter = ("owner",)
