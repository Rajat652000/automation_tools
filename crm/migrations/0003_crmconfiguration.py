from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("crm", "0002_contactnote_segment_subscription")]
    operations = [migrations.CreateModel(name="CRMConfiguration", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("industry", models.CharField(choices=[("school", "School"), ("shop", "Small Shop"), ("business", "Small Business")], default="business", max_length=30)), ("modules", models.JSONField(default=list)), ("updated_at", models.DateTimeField(auto_now=True)), ("owner", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="crm_configuration", to=settings.AUTH_USER_MODEL))])]
