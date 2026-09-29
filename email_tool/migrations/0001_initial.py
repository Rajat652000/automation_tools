from django.db import migrations, models
import django.conf
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="EmailProfile", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("host", models.CharField(default="smtp.gmail.com", max_length=255)), ("port", models.PositiveIntegerField(default=587)), ("username", models.EmailField(max_length=254)), ("app_password", models.CharField(max_length=255)), ("from_email", models.EmailField(max_length=254)), ("enabled", models.BooleanField(default=False)), ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="email_profile", to=django.conf.settings.AUTH_USER_MODEL))])]
