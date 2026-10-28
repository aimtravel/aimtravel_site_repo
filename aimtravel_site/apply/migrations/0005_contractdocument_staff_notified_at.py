from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('apply', '0004_eur_pricing_and_protection')]
    operations = [
        migrations.AddField(
            model_name='contractdocument', name='staff_notified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
