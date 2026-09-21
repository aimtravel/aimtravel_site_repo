from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0009_alter_appuser_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='phone',
            field=models.CharField(
                blank=True,
                db_index=True,
                default='',
                help_text='Телефонът се използва за свързване с CRM профила на човека.',
                max_length=40,
                verbose_name='Телефон',
            ),
        ),
    ]
