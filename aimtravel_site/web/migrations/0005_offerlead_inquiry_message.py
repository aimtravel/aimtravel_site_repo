from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_offerlead_portal_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='offerlead',
            name='inquiry_message',
            field=models.TextField(
                blank=True,
                default='',
                verbose_name='Запитвания от любими оферти',
            ),
        ),
    ]
