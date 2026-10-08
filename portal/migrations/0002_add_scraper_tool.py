from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portal", "0001_initial")]
    operations = [migrations.AlterField(model_name="toolaccess", name="tool", field=models.CharField(choices=[("email", "Email"), ("scraper", "Web Scraper"), ("crm", "CRM")], max_length=30))]
