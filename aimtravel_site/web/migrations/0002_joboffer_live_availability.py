from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='joboffer',
            name='sponsor',
            field=models.CharField(
                blank=True,
                choices=[
                    ('CHI', 'CHI'),
                    ('United', 'United'),
                    ('Dynamic', 'Dynamic'),
                    ('AWA', 'AWA'),
                ],
                default='',
                max_length=10,
                verbose_name='Спонсор',
            ),
        ),
        migrations.AddField(
            model_name='joboffer',
            name='assignment',
            field=models.BooleanField(default=False, verbose_name='Assignment'),
        ),
        migrations.AddField(
            model_name='joboffer',
            name='availability_status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('available', 'Свободна'),
                    ('last_seats', 'Последни места'),
                    ('occupied', 'Заета'),
                ],
                default='',
                max_length=20,
                verbose_name='Реална наличност',
            ),
        ),
        migrations.AddField(
            model_name='joboffer',
            name='availability_updated_at',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Наличността е обновена на',
            ),
        ),
    ]
