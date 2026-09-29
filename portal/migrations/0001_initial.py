from django.db import migrations, models
import django.conf
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="ToolAccess", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("tool", models.CharField(choices=[("email", "Email"), ("whatsapp", "WhatsApp"), ("sms", "SMS"), ("chatbot", "WhatsApp Chatbot")], max_length=30)), ("granted_at", models.DateTimeField(auto_now_add=True)), ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tool_access", to=django.conf.settings.AUTH_USER_MODEL))], options={"constraints": [models.UniqueConstraint(fields=("user", "tool"), name="unique_user_tool_access")]})]
