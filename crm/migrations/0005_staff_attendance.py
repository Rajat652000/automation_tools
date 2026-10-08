from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [("crm", "0004_attendance")]
    operations = [
        migrations.CreateModel(name="StaffMember", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("name", models.CharField(max_length=255)), ("phone", models.CharField(blank=True, max_length=100)), ("role", models.CharField(blank=True, max_length=100)), ("pay_type", models.CharField(choices=[("monthly", "Monthly salary"), ("hourly", "Hourly / part-time")], default="monthly", max_length=20)), ("pay_rate", models.DecimalField(decimal_places=2, default=0, max_digits=12)), ("standard_hours", models.DecimalField(decimal_places=2, default=8, max_digits=6)), ("active", models.BooleanField(default=True)), ("created_at", models.DateTimeField(auto_now_add=True)), ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_members", to=settings.AUTH_USER_MODEL))]),
        migrations.CreateModel(name="StaffAttendance", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("date", models.DateField()), ("status", models.CharField(choices=[("present", "Present"), ("absent", "Absent"), ("late", "Late")], max_length=20)), ("hours", models.DecimalField(decimal_places=2, default=0, max_digits=6)), ("note", models.CharField(blank=True, max_length=255)), ("member", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance", to="crm.staffmember"))], options={"constraints": [models.UniqueConstraint(fields=("member", "date"), name="unique_staff_attendance_date")]})
    ]
