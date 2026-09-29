from django.db import migrations, models
import django.conf
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("email_tool", "0001_initial")]
    operations = [
        migrations.CreateModel(name="EmailSuppression", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("email", models.EmailField(max_length=254, unique=True)), ("reason", models.CharField(default="unsubscribe", max_length=100)), ("created_at", models.DateTimeField(auto_now_add=True))]),
        migrations.CreateModel(name="EmailSendLog", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("recipient", models.EmailField(max_length=254)), ("subject", models.CharField(max_length=255)), ("status", models.CharField(choices=[("sent", "Sent"), ("failed", "Failed"), ("skipped", "Skipped")], max_length=20)), ("error", models.TextField(blank=True)), ("created_at", models.DateTimeField(auto_now_add=True)), ("sent_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=django.conf.settings.AUTH_USER_MODEL))]),
    ]
