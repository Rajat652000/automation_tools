from django.conf import settings
from django.db import models


class ToolAccess(models.Model):
    TOOLS = [("email", "Email"), ("whatsapp", "WhatsApp"), ("sms", "SMS"), ("chatbot", "WhatsApp Chatbot"), ("scraper", "Web Scraper")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tool_access")
    tool = models.CharField(max_length=30, choices=TOOLS)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "tool"], name="unique_user_tool_access")]
