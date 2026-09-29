from django.contrib import admin
from .models import EmailProfile, EmailSendLog, EmailSuppression


@admin.register(EmailProfile)
class EmailProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "username", "enabled")
    list_filter = ("enabled",)

admin.site.register(EmailSendLog)
admin.site.register(EmailSuppression)
