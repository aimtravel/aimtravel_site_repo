from django.db import models
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import os
from model_utils import Choices

from aimtravel_site.web.validators import max_value


class JobOffer(models.Model):
    POSITION_NAME = 30
    EMPLOYER = 30
    CITY_NAME = 20
    STATE_NAME = 20
    SPONSOR_NAME = 20

    employer_name = models.CharField(
        verbose_name='Име на работодател',
        max_length=EMPLOYER,
        blank=True,
        null=True,
    )
    city = models.CharField(
        verbose_name='Град',
        max_length=CITY_NAME,
        blank=True,
        null=True,
    )
    state = models.CharField(
        verbose_name='Щат',
        max_length=STATE_NAME,
        blank=True,
        null=True,
    )
    job_position = models.CharField(
        verbose_name='Работна позиция',
        max_length=POSITION_NAME,
        blank=True,
        null=True,
    )
    wage = models.FloatField(
        verbose_name='Заплащане',
        blank=True,
        null=True,
    )
    tips = models.BooleanField(
        verbose_name='Бакшиши',
        blank=True,
        null=True,
    )
    bonus = models.BooleanField(
        verbose_name='Бонус',
        blank=True,
        null=True,
    )
    minimum_hours = models.FloatField(
        verbose_name='Минимум часове на седмица',
        blank=True,
        null=True,
    )
    overtime = models.BooleanField(
        verbose_name='Overtime',
        blank=True,
        null=True,
    )
    housing = models.BooleanField(
        verbose_name='Хаузинг',
        blank=True,
        null=True,
    )
    english_level = models.CharField(
        verbose_name='Ниво на английски език',
        max_length=10,
        blank=True,
        null=True,
    )
    begin_date = models.DateField(
        verbose_name='Стартова дата',
        blank=True,
        null=True,
    )
    end_date = models.DateField(
        verbose_name='Крайна дата',
        blank=True,
        null=True,
    )
    groups = models.BooleanField(
        verbose_name='Подходящо за групи',
        blank=True,
        null=True,
    )
    couples = models.BooleanField(
        verbose_name='Подходящо за двойки',
        blank=True,
        null=True,
    )
    job_description = models.TextField(
        verbose_name='Описание на работата',
        blank=True,
        null=True,
    )
    interesting = models.TextField(
        verbose_name='Интересно'
                     '',
        blank=True,
        null=True,
    )
    students_feedback = models.TextField(
        verbose_name='Отзиви от студенти',
        blank=True,
        null=True,
    )
    offer_pic = models.ImageField(
        upload_to='job_offer_pics/',
        verbose_name='Снимка',
        blank=True,
        null=True,
    )
    ranking = models.PositiveIntegerField(
        validators=(max_value,),
        default=1,
        blank=True,
        null=True,
    )
    new_offer = models.BooleanField(
        verbose_name='Нова оферта',
        blank=True,
        null=True,
    )
    sold_out_offer = models.BooleanField(
        verbose_name='Sold out',
        blank=True,
        null=True,
    )
    last_seats = models.BooleanField(
        verbose_name='Последни места',
        blank=True,
        null=True,
    )

    def __str__(self):
        result = f'{self.job_position} at {self.employer_name} - {self.city}, {self.state}'
        return result

    def delete(self, *args, **kwargs):
        pre_delete.send(sender=self.__class__, instance=self)

        super().delete(*args, **kwargs)

    def delete_picture_file(self):
        if self.offer_pic:
            path = os.path.join(settings.MEDIA_ROOT, str(self.offer_pic))
            if os.path.exists(path):
                os.remove(path)


class Prices(models.Model):
    PRICING_TYPE = Choices('Self Arranged', 'Full Placement Standard', 'Premium Full Placement', )
    DEFAULT_PRICING_TYPE = 'Full Placement Standard'
    MAX_NAME = 25

    pricing_type = models.CharField(
        verbose_name='Ценови план:',
        max_length=MAX_NAME,
        default=DEFAULT_PRICING_TYPE,
        choices=PRICING_TYPE,
        blank=True,
        null=True,
    )

    price = models.FloatField(
        verbose_name='Цена:',
    )

    price_description = models.TextField(
        verbose_name='В цената е включено:',
        blank=True,
        null=True,
        help_text="Моля добавете описание",
    )

    def __str__(self):
        return f"{self.pricing_type}: $ {self.price:.2f}"


class AdditionalServices(models.Model):
    MAX_NAME = 30

    service_type = models.CharField(
        verbose_name='Вид услуга',
        max_length=MAX_NAME,
        blank=True,
        null=True,
    )
    service_description = models.TextField(
        verbose_name='Описание на услугата',
        blank=True,
        null=True,
    )
    service_price = models.FloatField(
        verbose_name='Цена на услугата',
        blank=True,
        null=True,
    )


class Company(models.Model):
    EMPLOYER_NAME = 30
    CITY_NAME = 20
    STATE_NAME = 2
    EMPLOYER_HISTORY = 250

    employer_name = models.CharField(
        verbose_name="Работодател",
        max_length=EMPLOYER_NAME,
        blank=False,
        null=True,
    )
    employer_city = models.CharField(
        verbose_name='Град',
        max_length=CITY_NAME,
        blank=False,
        null=True,
    )
    employer_state = models.CharField(
        verbose_name='Щат',
        max_length=STATE_NAME,
        blank=False,
        null=True,
    )
    employer_history = models.TextField(
        verbose_name='Кратка история',
        max_length=EMPLOYER_HISTORY,
        blank=False,
        null=True,
    )
    employer_photo = models.URLField(
        verbose_name='Снимка-URL',
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.employer_name}'
