from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('web', '0003_offerlead'),
    ]

    operations = [
        migrations.AddField(
            model_name='offerlead',
            name='user',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='offer_lead',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Потребителски профил',
            ),
        ),
        migrations.AddField(
            model_name='offerlead',
            name='lifecycle_stage',
            field=models.CharField(
                choices=[
                    ('lead', 'Lead / потенциал'),
                    ('customer', 'Customer / попълнена application форма'),
                    ('enrolled', 'Записан / договор подписан'),
                ],
                default='lead',
                max_length=20,
                verbose_name='Тип профил',
            ),
        ),
        migrations.AddField(
            model_name='offerlead',
            name='application_submitted_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Application изпратена на'),
        ),
        migrations.AddField(
            model_name='offerlead',
            name='contract_status',
            field=models.CharField(
                choices=[
                    ('none', 'Няма генериран договор'),
                    ('generated', 'Генериран'),
                    ('sent', 'Изпратен за подпис'),
                    ('signed', 'Подписан'),
                ],
                default='none',
                max_length=20,
                verbose_name='Статус на договора',
            ),
        ),
        migrations.AddField(
            model_name='offerlead',
            name='contract_file',
            field=models.FileField(blank=True, null=True, upload_to='contracts/%Y/%m/', verbose_name='Договор'),
        ),
        migrations.AlterField(
            model_name='offerlead',
            name='first_name',
            field=models.CharField(blank=True, default='', max_length=80, verbose_name='Име'),
        ),
        migrations.AlterField(
            model_name='offerlead',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=80, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='offerlead',
            name='university',
            field=models.CharField(blank=True, default='', max_length=160, verbose_name='Университет'),
        ),
        migrations.AlterField(
            model_name='offerlead',
            name='course',
            field=models.CharField(blank=True, default='', max_length=40, verbose_name='Курс'),
        ),
        migrations.AlterField(
            model_name='offerlead',
            name='specialty',
            field=models.CharField(blank=True, default='', max_length=160, verbose_name='Специалност'),
        ),
    ]
