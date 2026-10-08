from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("crm", "0006_inventory_transaction")]
    operations = [migrations.AlterField(model_name="crmconfiguration", name="modules", field=models.JSONField(default=list))]
