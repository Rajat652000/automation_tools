from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("crm", "0003_crmconfiguration")]
    operations = [migrations.CreateModel(name="Attendance", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("date", models.DateField()), ("status", models.CharField(choices=[("present", "Present"), ("absent", "Absent"), ("late", "Late")], max_length=20)), ("note", models.CharField(blank=True, max_length=255)), ("created_at", models.DateTimeField(auto_now_add=True)), ("contact", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="crm.contact"))])]
