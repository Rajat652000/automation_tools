from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [("crm", "0005_staff_attendance")]
    operations = [migrations.CreateModel(name="InventoryTransaction", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("kind", models.CharField(choices=[("sale", "Sale"), ("purchase", "Purchase")], max_length=20)), ("item_name", models.CharField(max_length=255)), ("quantity", models.DecimalField(decimal_places=2, max_digits=12)), ("unit_price", models.DecimalField(decimal_places=2, max_digits=12)), ("date", models.DateField()), ("note", models.CharField(blank=True, max_length=255)), ("created_at", models.DateTimeField(auto_now_add=True)), ("contact", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="transactions", to="crm.contact")), ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="crm_transactions", to=settings.AUTH_USER_MODEL))])]
