from django.contrib import admin
from .models import ChatbotRule, Conversation


@admin.register(ChatbotRule)
class ChatbotRuleAdmin(admin.ModelAdmin):
    list_display = ("question", "answer", "active")
    list_filter = ("active",)
    search_fields = ("question", "answer")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "phone_number",
        "incoming_message",
        "bot_reply",
        "created_at",
    )

    search_fields = (
        "phone_number",
        "incoming_message",
    )