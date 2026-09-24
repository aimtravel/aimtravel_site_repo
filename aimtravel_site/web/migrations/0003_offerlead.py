import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_joboffer_live_availability'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfferLead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('first_name', models.CharField(max_length=80, verbose_name='Име')),
                ('last_name', models.CharField(max_length=80, verbose_name='Фамилия')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Имейл')),
                ('phone', models.CharField(max_length=40, verbose_name='Телефон')),
                ('university', models.CharField(max_length=160, verbose_name='Университет')),
                ('course', models.CharField(max_length=40, verbose_name='Курс')),
                ('specialty', models.CharField(max_length=160, verbose_name='Специалност')),
                ('status', models.CharField(choices=[('new', 'Нов потенциал'), ('contacted', 'Потърсен'), ('enrolled', 'Записан студент'), ('closed', 'Затворен')], default='new', max_length=20, verbose_name='CRM статус')),
                ('source', models.CharField(default='Работни оферти', max_length=80, verbose_name='Източник')),
                ('privacy_consent', models.BooleanField(default=True, verbose_name='Съгласие за контакт')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Създаден на')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновен на')),
                ('favorite_offers', models.ManyToManyField(blank=True, related_name='offer_leads', to='web.joboffer', verbose_name='Любими оферти')),
            ],
            options={
                'verbose_name': 'CRM потенциал от офертите',
                'verbose_name_plural': 'CRM потенциали от офертите',
                'ordering': ('-created_at',),
            },
        ),
    ]
