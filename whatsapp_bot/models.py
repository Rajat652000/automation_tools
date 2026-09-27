from django.db import models


class ChatbotRule(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.question


class Conversation(models.Model):
    phone_number = models.CharField(max_length=30)
    incoming_message = models.TextField()
    bot_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_number