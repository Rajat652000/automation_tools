from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portal", "0002_add_scraper_tool")]
    operations = [
        migrations.AlterField(model_name="toolaccess", name="tool", field=models.CharField(choices=[("email", "Email"), ("scraper", "Web Scraper"), ("crm", "CRM")], max_length=30)),
        migrations.RunSQL("DELETE FROM portal_toolaccess WHERE tool IN ('whatsapp', 'sms', 'chatbot')", reverse_sql=migrations.RunSQL.noop),
    ]
