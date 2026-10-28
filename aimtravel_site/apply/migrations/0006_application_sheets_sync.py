from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("apply", "0005_contractdocument_staff_notified_at")]
    operations = [
        migrations.AddField(model_name="application", name="sheets_synced_at",
                            field=models.DateTimeField(null=True, blank=True)),
        migrations.AddField(model_name="application", name="sheets_sync_error",
                            field=models.CharField(max_length=200, blank=True)),
    ]
