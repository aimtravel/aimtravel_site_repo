from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.db.models.signals import pre_delete
import os
import uuid

from django.urls import reverse
from model_utils import Choices

from aimtravel_site.web.validators import max_value


class City(models.Model):
    class Meta:
        verbose_name = 'Град'
        verbose_name_plural = 'Градове'

    CITY = 20
    STATES = (
        ('AL', 'AL'),
        ('AK', 'AK'),
        ('AZ', 'AZ'),
        ('AR', 'AR'),
        ('CA', 'CA'),
        ('CO', 'CO'),
        ('CT', 'CT'),
        ('DE', 'DE'),
        ('FL', 'FL'),
        ('GA', 'GA'),
        ('HI', 'HI'),
        ('ID', 'ID'),
        ('IL', 'IL'),
        ('IN', 'IN'),
        ('IA', 'IA'),
        ('KS', 'KS'),
        ('KY', 'KY'),
        ('LA', 'LA'),
        ('ME', 'ME'),
        ('MD', 'MD'),
        ('MA', 'MA'),
        ('MI', 'MI'),
        ('MN', 'MN'),
        ('MS', 'MS'),
        ('MO', 'MO'),
        ('MT', 'MT'),
        ('NE', 'NE'),
        ('NV', 'NV'),
        ('NH', 'NH'),
        ('NJ', 'NJ'),
        ('NM', 'NM'),
        ('NY', 'NY'),
        ('NC', 'NC'),
        ('ND', 'ND'),
        ('OH', 'OH'),
        ('OK', 'OK'),
        ('OR', 'OR'),
        ('PA', 'PA'),
        ('RI', 'RI'),
        ('SC', 'SC'),
        ('SD', 'SD'),
        ('TN', 'TN'),
        ('TX', 'TX'),
        ('UT', 'UT'),
        ('VT', 'VT'),
        ('VA', 'VA'),
        ('WA', 'WA'),
        ('WV', 'WV'),
        ('WI', 'WI'),
        ('WY', 'WY'),
    )

    name = models.CharField(
        unique=True,
        verbose_name='Град',
        max_length=CITY,
        blank=True,
        null=True,
    )
    state = models.CharField(
        choices=STATES,
        verbose_name='Щат',
        max_length=CITY,
        blank=True,
        null=True,
    )

    fact1 = models.TextField(

        verbose_name='Факт 1',
        blank=True,
        null=True,
    )
    fact2 = models.TextField(

        verbose_name='Факт 2',
        blank=True,
        null=True,
    )
    fact3 = models.TextField(

        verbose_name='Факт 3',
        blank=True,
        null=True,
    )
    city_pic = models.ImageField(
        upload_to='city_pics/',
        verbose_name='Снимка',
        blank=True,
        null=True,
    )

    def __str__(self):
        result = f'{self.name}'
        return result


class Feedback(models.Model):
    class Meta:
        verbose_name = 'Обратна връзка'
        verbose_name_plural = 'Обратна връзка'

    feedback_name = models.CharField(
        verbose_name='Оферта',
        max_length=100,
        unique=True,
        blank=True,
        null=True,
    )
    student_name_1 = models.CharField(
        verbose_name='Студент 1',
        max_length=20,
        blank=True,
        null=True,
    )
    student_pic_1 = models.ImageField(
        upload_to='feedback_student_pics/',
        verbose_name='Снимка 1',
        blank=True,
        null=True,
    )
    feedback_1 = models.TextField(
        verbose_name='Отзив 1',
        blank=True,
        null=True,
    )
    student_name_2 = models.CharField(
        verbose_name='Студент 2',
        max_length=20,
        blank=True,
        null=True,
    )
    student_pic_2 = models.ImageField(
        upload_to='feedback_student_pics/',
        verbose_name='Снимка 2',
        blank=True,
        null=True,
    )
    feedback_2 = models.TextField(
        verbose_name='Отзив 2',
        blank=True,
        null=True,
    )
    student_name_3 = models.CharField(
        verbose_name='Студент 3',
        max_length=20,
        blank=True,
        null=True,
    )
    student_pic_3 = models.ImageField(
        upload_to='feedback_student_pics/',
        verbose_name='Снимка 3',
        blank=True,
        null=True,
    )
    feedback_3 = models.TextField(
        verbose_name='Отзив 3',
        blank=True,
        null=True,
    )

    def __str__(self):
        result = f'{self.feedback_name}'
        return result


class JobOffer(models.Model):
    class Meta:

        verbose_name = 'Работна оферта'
        verbose_name_plural = 'Работни оферти'

    POSITION_NAME = 30
    EMPLOYER = 30
    CITY_NAME = 20
    STATE_NAME = 20
    SPONSOR_NAME = 20

    SUITABLE_FOR = (
        ('Студенти', 'Студенти'),
        ('Нестуденти', 'Нестуденти'),
    )

    ENGLISH_LEVEL = (
        ('Ниско', 'Ниско'),
        ('Средно', 'Средно'),
        ('Високо', 'Високо'),
    )

    YES_NO = (
        ('Да', 'Да'),
        ('Не', 'Не'),
    )

    TRUE_FALSE = (
        ('True', 'Да'),
        ('False', 'Не'),
    )

    SPONSOR_CHOICES = (
        ('CHI', 'CHI'),
        ('United', 'United'),
        ('Dynamic', 'Dynamic'),
        ('AWA', 'AWA'),
    )

    AVAILABILITY_CHOICES = (
        ('available', 'Свободна'),
        ('last_seats', 'Последни места'),
        ('occupied', 'Заета'),
    )

    employer_name = models.CharField(
        verbose_name='Име на работодател',
        max_length=EMPLOYER,
        blank=True,
        null=True,
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        to_field='name'
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
    tips = models.CharField(
        choices=YES_NO,
        max_length=2,
        verbose_name='Бакшиши',
        blank=True,
        null=True,
    )
    bonus = models.CharField(
        verbose_name='Бонус',
        choices=YES_NO,
        max_length=2,
        blank=True,
        null=True,
    )
    minimum_hours = models.FloatField(
        verbose_name='Минимум часове на седмица',
        blank=True,
        null=True,
    )
    overtime = models.CharField(
        verbose_name='Overtime',
        choices=YES_NO,
        max_length=2,
        blank=True,
        null=True,
    )
    housing = models.CharField(
        default="Не",
        max_length=10,
        verbose_name="Housing",
        blank=True,
        null=True,
    )
    english_level = models.CharField(
        verbose_name='Ниво на английски език',
        choices=ENGLISH_LEVEL,
        max_length=10,
        blank=True,
        null=True,
    )
    begin_date = models.DateField(
        verbose_name='Най-ранно заминаване',
        blank=True,
        null=True,
    )
    end_date = models.DateField(
        verbose_name='Най-късно заминаване',
        blank=True,
        null=True,
    )
    groups = models.CharField(
        verbose_name='Подходящо за групи',
        choices=YES_NO,
        max_length=2,
        blank=True,
        null=True,
    )
    couples = models.CharField(
        verbose_name='Подходящо за двойки',
        choices=YES_NO,
        max_length=2,
        blank=True,
        null=True,
    )
    suitable_for = models.CharField(
        choices=SUITABLE_FOR,
        max_length=20,
        verbose_name="Подходящо за",
        blank=True,
        null=True,
    )
    job_description = models.TextField(
        verbose_name='Описание на работата',
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
    new_offer = models.CharField(
        verbose_name='Нова оферта',
        choices=TRUE_FALSE,
        max_length=5,
        default=False,
        blank=True,
        null=True,
    )
    sold_out_offer = models.CharField(
        verbose_name='Sold out',
        choices=TRUE_FALSE,
        default=False,
        max_length=5,
        blank=True,
        null=True,
    )
    last_seats = models.CharField(
        verbose_name='Последни места',
        choices=TRUE_FALSE,
        max_length=5,
        default=False,
        blank=True,
        null=True,
    )
    sponsor = models.CharField(
        verbose_name='Спонсор',
        choices=SPONSOR_CHOICES,
        max_length=10,
        blank=True,
        default='',
    )
    assignment = models.BooleanField(
        verbose_name='Assignment',
        default=False,
    )
    availability_status = models.CharField(
        verbose_name='Реална наличност',
        choices=AVAILABILITY_CHOICES,
        max_length=20,
        blank=True,
        default='',
    )
    availability_updated_at = models.DateTimeField(
        verbose_name='Наличността е обновена на',
        blank=True,
        null=True,
    )
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        to_field='feedback_name',
        blank=True,
        null=True,
    )

    def __str__(self):
        result = f'{self.job_position} at {self.employer_name} - {self.city}'
        return result

    def delete(self, *args, **kwargs):
        pre_delete.send(sender=self.__class__, instance=self)

        super().delete(*args, **kwargs)

    def delete_picture_file(self):
        if self.offer_pic:
            path = os.path.join(settings.MEDIA_ROOT, str(self.offer_pic))
            if os.path.exists(path):
                os.remove(path)

    def get_absolute_url(self):
        return reverse('offers')


class OfferLead(models.Model):
    STATUS_CHOICES = (
        ('new', 'Нов потенциал'),
        ('contacted', 'Потърсен'),
        ('enrolled', 'Записан студент'),
        ('closed', 'Затворен'),
    )

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    first_name = models.CharField('Име', max_length=80)
    last_name = models.CharField('Фамилия', max_length=80)
    email = models.EmailField('Имейл', unique=True)
    phone = models.CharField('Телефон', max_length=40)
    university = models.CharField('Университет', max_length=160)
    course = models.CharField('Курс', max_length=40)
    specialty = models.CharField('Специалност', max_length=160)
    favorite_offers = models.ManyToManyField(
        JobOffer, verbose_name='Любими оферти', related_name='offer_leads', blank=True,
    )
    status = models.CharField(
        'CRM статус', max_length=20, choices=STATUS_CHOICES, default='new',
    )
    source = models.CharField('Източник', max_length=80, default='Работни оферти')
    privacy_consent = models.BooleanField('Съгласие за контакт', default=True)
    created_at = models.DateTimeField('Създаден на', auto_now_add=True)
    updated_at = models.DateTimeField('Обновен на', auto_now=True)

    class Meta:
        verbose_name = 'CRM потенциал от офертите'
        verbose_name_plural = 'CRM потенциали от офертите'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.first_name} {self.last_name} – {self.email}'


class Prices(models.Model):
    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цени'

    actual_self_arrange = models.FloatField(
        verbose_name='Актуална цена за Self Arranged:',
        blank=True,
        null=True,
    )
    discounted_self_arrange = models.FloatField(
        verbose_name='Промо цена за Self Arranged(задраскана):',
        blank=True,
        null=True,
    )

    actual_standard = models.FloatField(
        verbose_name='Актуална цена за Full Standard:',
        blank=True,
        null=True,
    )
    discounted_standard = models.FloatField(
        verbose_name='Промо цена за Full Standard(задраскана):',
        blank=True,
        null=True,
    )

    actual_premium = models.FloatField(
        verbose_name='Актуална цена за Full Premium:',
        blank=True,
        null=True,
    )
    discounted_premium = models.FloatField(
        verbose_name='Промо цена за Full Premium(задраскана):',
        blank=True,
        null=True,
    )

    sevis = models.FloatField(
        verbose_name='Такса Sevis:',
        blank=True,
        null=True,
    )

    visa_interview = models.FloatField(
        verbose_name='Такса визово интервю:',
        blank=True,
        null=True,
    )

    plane_ticket_lowest = models.FloatField(
        verbose_name='Самолетен билет - най-ниска цена:',
        blank=True,
        null=True,
    )

    plane_ticket_highest = models.FloatField(
        verbose_name='Самолетен билет - най-висока цена:',
        blank=True,
        null=True,
    )

    sign_up_fees = models.FloatField(
        verbose_name='Такса при записване:',
        blank=True,
        null=True,
    )

    validity_date_day = models.IntegerField(
        verbose_name='Валидно до - Ден:',
        blank=True,
        null=True,
    )
    validity_date_month = models.CharField(
        max_length=15,
        verbose_name='Валидно до - Месец:',
        validators=[RegexValidator('^[A-ZА-Я]*$', 'Използвай само главни букви.')],
        blank=True,
        null=True,
    )
    validity_date_year = models.IntegerField(
        verbose_name='Валидно до - Година:',
        blank=True,
        null=True,
    )

    amount_of_discount = models.IntegerField(
        verbose_name='Отстъпка до ($):',
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Ценови план"


class AdditionalServices(models.Model):
    class Meta:
        verbose_name = 'Допълнителни услуги'
        verbose_name_plural = 'Допълнителни услуги'

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
    class Meta:
        verbose_name = 'Работодател'
        verbose_name_plural = 'Работодатели'

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
