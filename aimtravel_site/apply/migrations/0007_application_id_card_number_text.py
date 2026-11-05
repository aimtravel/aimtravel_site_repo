from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("apply", "0006_application_sheets_sync")]
    operations = [
        migrations.AlterField(
            model_name="application", name="id_card_number", field=models.TextField(),
        ),
    ]
