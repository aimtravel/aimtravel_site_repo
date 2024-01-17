from django.contrib.auth import get_user_model
from django.db import models
from aimtravel_site.web.models import City

UserModel = get_user_model()


def upload_to_path(instance, filename):
    return f'tax_documents/{instance.working_year}/{instance.first_name}_{instance.middle_name}_{instance.family_name}/{filename}'


# Create your models here.
class Taxes(models.Model):

    class Meta:
        verbose_name = 'Tax-Refund'
        verbose_name_plural = 'Taxes'

    NAME = 30
    ADDRESS = 100
    EMAIL = 50
    PHONE = 15

    HOW_DID_YOU_FIND_US = (
        ('friends', 'friends'),
        ('brochure', 'brochure'),
        ('internet', 'internet'),
        ('posters', 'posters'),
        ('agency', 'agency'),
    )

    YEAR = (
        ('2020', '2020'),
        ('2021', '2021'),
        ('2022', '2022'),
        ('2023', '2023'),
    )

    VISA = (
        ('J1', 'J1'),
        ('J2', 'J2'),
        ('F1', 'F1'),
        ('F2', 'F2'),
        ('Green card', 'Green Card'),
        ('H1B', 'H1B'),
        ('H2B', 'H2B'),
        ('M', 'M'),
        ('Other', 'Other'),
        ('None', 'None'),
    )

    PROGRAM_TYPE = (
        ('Internship', 'Internship'),
        ('Work and Travel', 'Work and Travel'),
        ('Career Training', 'Career Training'),
        ('Other', 'Other'),
        ('None', 'None'),
    )

    BANK_ACCOUNT = (
        ('Checking', 'Checking'),
        ('Saving', 'Saving'),
    )

    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='taxes'
    )

    first_name = models.CharField(max_length=NAME, blank=True, null=True)
    middle_name = models.CharField(max_length=NAME, blank=True, null=True)
    family_name = models.CharField(max_length=NAME, blank=True, null=True)
    mothers_maiden_name = models.CharField(max_length=NAME, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    birth_city = models.CharField(max_length=NAME, blank=True, null=True)
    address = models.CharField(max_length=ADDRESS, blank=True, null=True)
    city = models.CharField(max_length=NAME, blank=True, null=True)
    country = models.CharField(max_length=NAME, blank=True, null=True)
    email = models.CharField(max_length=EMAIL, blank=True, null=True)
    phone_number = models.CharField(max_length=PHONE, blank=True, null=True)
    how_did_you_find_us = models.CharField(
        max_length=15,
        choices=HOW_DID_YOU_FIND_US,
        blank=True,
        null=True,
    )
    social_security = models.CharField(max_length=12, blank=True, null=True)
    working_year = models.CharField(
        max_length=4,
        choices=YEAR,
        blank=True,
        null=True,
    )
    arrival_date_in_usa = models.DateField(blank=True, null=True)
    departure_date_in_usa = models.DateField(blank=True, null=True)
    visa_type = models.CharField(
        max_length=10,
        choices=VISA,
        blank=True,
        null=True,
    )
    program_type = models.CharField(
        max_length=20,
        choices=PROGRAM_TYPE,
        blank=True,
        null=True,
    )
    previous_tax_declarations = models.BooleanField(default=False)
    visa_changing = models.BooleanField(default=False)
    pin_from_irs = models.BooleanField(default=False)
    company_name = models.CharField(max_length=40, blank=True, null=True)
    company_address = models.CharField(max_length=ADDRESS, blank=True, null=True)
    company_city = models.CharField(max_length=NAME, blank=True, null=True)
    company_state = models.CharField(
        max_length=2,
        choices=City.STATES,
        blank=True,
        null=True,
    )
    company_zip = models.CharField(max_length=6, blank=True, null=True)
    company_phone = models.CharField(max_length=PHONE, blank=True, null=True)
    company_fax = models.CharField(max_length=PHONE, blank=True, null=True)
    company_email = models.CharField(max_length=EMAIL, blank=True, null=True)
    last_paycheck = models.BooleanField(default=False)
    w_2 = models.BooleanField(default=False)
    american_bank_account = models.BooleanField(default=False)
    type_of_account = models.CharField(
        max_length=8,
        choices=BANK_ACCOUNT,
        blank=True,
        null=True,
    )
    bank_name = models.CharField(max_length=NAME, blank=True, null=True)
    account_holder = models.CharField(max_length=100, blank=True, null=True)
    routing_number = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    passport_copy = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='Копие на паспорт',
        blank=True,
        null=True,
    )
    visa_copy = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='Копие на виза',
        blank=True,
        null=True,
    )
    ssn_copy = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='Копие на Social Security',
        blank=True,
        null=True,
    )
    last_paycheck_copy = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='Последни чекове',
        blank=True,
        null=True,
    )
    w2_copy = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='W-2 форми',
        blank=True,
        null=True,
    )
    bank_account_screenshot = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='Screenshot на банковата ти сметка,потвържващ че ти си собственик на сметката',
        blank=True,
        null=True,
    )
    us_document_copy = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='Снимка на ID от САЩ/Американска Шофьорска книжка (само ако имате)',
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Данъци на {self.first_name} {self.middle_name} {self.family_name}"
