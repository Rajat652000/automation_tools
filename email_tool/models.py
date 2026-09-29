from django.conf import settings
from django.db import models


class EmailProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_profile")
    host = models.CharField(max_length=255, default="smtp.gmail.com")
    port = models.PositiveIntegerField(default=587)
    username = models.EmailField()
    app_password = models.CharField(max_length=255)
    from_email = models.EmailField()
    enabled = models.BooleanField(default=False)


class EmailSuppression(models.Model):
    email = models.EmailField(unique=True)
    reason = models.CharField(max_length=100, default="unsubscribe")
    created_at = models.DateTimeField(auto_now_add=True)


class EmailSendLog(models.Model):
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[("sent", "Sent"), ("failed", "Failed"), ("skipped", "Skipped")])
    error = models.TextField(blank=True)
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
