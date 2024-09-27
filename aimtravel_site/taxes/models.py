import datetime

from django.contrib.auth import get_user_model
from django.db import models
from aimtravel_site.web.models import City

UserModel = get_user_model()


def get_current_year():
    date = datetime.date.today()
    year = date.year
    return year


def upload_to_path(instance, filename):
    return f'tax_documents/{instance.working_year}/{instance.first_name}_{instance.middle_name}_{instance.family_name}/{filename}'


# Create your models here.
class Taxes(models.Model):
    class Meta:
        verbose_name = 'Tax'
        verbose_name_plural = 'Taxes'

    NAME = 30
    ADDRESS = 100
    EMAIL = 50
    PHONE = 15
    YEAR = (
        (f'{get_current_year()}', f'{get_current_year()}'),
        (f'{get_current_year() - 1}', f'{get_current_year() - 1}'),
        (f'{get_current_year() - 2}', f'{get_current_year() - 2}'),
        (f'{get_current_year() - 3}', f'{get_current_year() - 3}'),
        (f'{get_current_year()-4}', f'{get_current_year()-4}')
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
    YES_NO = (
        ('No', 'Не'),
        ('Yes', 'Да')
    )
    STATUS_CHOICES = (
        ('1', 'Начало'),
        ('2', 'В прогрес'),
        ('3', 'Готово'),
    )
    BANK_ACCOUNT = (
        ('Checking', 'Checking'),
        ('Saving', 'Saving'),
    )
    GENERAL_STATUS_CHOICES = (
        ('registration', 'Регистрация'),
        ('declaration', 'Подадена декларация'),
        ('federal', 'Пристигнал Federal'),
        ('state', 'Пристигнал State'),
        ('federalfee', 'Платена комисионна Federal'),
        ('statefee', 'Платена комисионна State'),
        ('allpaid', 'Комисионна платена')
    )

    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='taxes'
    )
    first_name = models.CharField(max_length=NAME, blank=True, null=True)
    middle_name = models.CharField(max_length=NAME, blank=True, null=True)
    family_name = models.CharField(max_length=NAME, blank=True, null=True)
    first_name_en = models.CharField(max_length=NAME, blank=True, null=True)
    middle_name_en = models.CharField(max_length=NAME, blank=True, null=True)
    family_name_en = models.CharField(max_length=NAME, blank=True, null=True)
    mothers_maiden_name = models.CharField(max_length=NAME, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    birth_city = models.CharField(max_length=NAME, blank=True, null=True)
    address = models.CharField(max_length=ADDRESS, blank=True, null=True)
    city = models.CharField(max_length=NAME, blank=True, null=True)
    country = models.CharField(max_length=NAME, blank=True, null=True)
    id_number = models.CharField(max_length=15, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    email = models.CharField(max_length=EMAIL, blank=True, null=True)
    phone_number = models.CharField(max_length=PHONE, blank=True, null=True)
    personal_info_done = models.CharField(max_length=3, blank=True, null=True, default='no')

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
    previous_tax_declarations = models.CharField(
        max_length=3,
        choices=YES_NO,
        blank=True,
        null=True,
    )
    visa_changing = models.CharField(
        max_length=3,
        choices=YES_NO,
        blank=True,
        null=True,
    )
    pin_from_irs = models.CharField(
        max_length=3,
        choices=YES_NO,
        blank=True,
        null=True,
    )
    travel_info_done = models.CharField(max_length=3, blank=True, null=True, default='no')

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
    last_paycheck = models.CharField(
        max_length=3,
        choices=YES_NO,
        blank=True,
        null=True,
    )
    w_2 = models.CharField(
        max_length=3,
        choices=YES_NO,
        blank=True,
        null=True,
    )
    employer_info_done = models.CharField(max_length=3, blank=True, null=True, default='no')

    american_bank_account = models.CharField(
        max_length=3,
        choices=YES_NO,
        blank=True,
        null=True,
    )
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
    bank_info_done = models.CharField(max_length=3, blank=True, null=True, default='no')

    passport_copy = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='Копие на паспорт',
        blank=True,
        null=True,
    )
    passport_copy_used = models.BooleanField(default=False)
    visa_copy = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='Копие на виза',
        blank=True,
        null=True,
    )
    visa_copy_used = models.BooleanField(default=False)
    ssn_copy = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='Копие на Social Security',
        blank=True,
        null=True,
    )
    ssn_copy_used = models.BooleanField(default=False)
    last_paycheck_doc = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='Последни чекове',
        blank=True,
        null=True,
    )
    last_paycheck_doc_used = models.BooleanField(default=False)
    w2_form = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='W2 форма',
        blank=True,
        null=True,
    )
    w2_form_used = models.BooleanField(default=False)
    w2_lpc_e3 = models.FileField(
        upload_to=upload_to_path,
        verbose_name='Последен чек/W2 (работодател 3)',
        blank=True,
        null=True,
    )
    w2_lpc_e3_used = models.BooleanField(default=False)
    w2_lpc_e4 = models.FileField(
        upload_to=upload_to_path,
        verbose_name='Последен чек/W2 (работодател 4)',
        blank=True,
        null=True,
    )
    w2_lpc_e4_used = models.BooleanField(default=False)
    bank_account_screenshot = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='Screenshot на банковата ти сметка,потвържващ че ти си собственик на сметката',
        blank=True,
        null=True,
    )
    bank_account_screenshot_used = models.BooleanField(default=False)
    us_document_copy = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='Снимка на ID от САЩ/Американска Шофьорска книжка (само ако имате)',
        blank=True,
        null=True,
    )
    us_document_copy_used = models.BooleanField(default=False)
    signed_and_scanned_contract = models.FileField(
        upload_to=upload_to_path,
        # upload_to=f'tax_documents/{first_name}_{middle_name}_{family_name}/',
        verbose_name='Подписан и сканиран договор',
        blank=True,
        null=True,
    )
    signed_and_scanned_contract_used = models.BooleanField(default=False)
    attachments_info_done = models.CharField(max_length=3, blank=True, null=True, default='no')

    stat_reg = models.CharField(max_length=10, choices=STATUS_CHOICES, default='3', blank=True, null=True)
    stat_pers_dat = models.CharField(max_length=10, choices=STATUS_CHOICES, default='1', blank=True, null=True)
    stat_docs = models.CharField(max_length=10, choices=STATUS_CHOICES, default='1', blank=True, null=True)
    stat_in_progress = models.CharField(max_length=10, choices=STATUS_CHOICES, default='1', blank=True, null=True)
    stat_declaration_submitted = models.CharField(max_length=10, choices=STATUS_CHOICES, default='1', blank=True, null=True)
    stat_waiting_state = models.CharField(max_length=10, choices=STATUS_CHOICES, default='1', blank=True, null=True)
    stat_waiting_federal = models.CharField(max_length=10, choices=STATUS_CHOICES, default='1', blank=True, null=True)
    stat_state_customer = models.CharField(max_length=10, choices=STATUS_CHOICES, default='1', blank=True, null=True)
    stat_federal_customer = models.CharField(max_length=10, choices=STATUS_CHOICES, default='1', blank=True, null=True)
    stat_federal_fee_paid = models.CharField(max_length=10, choices=STATUS_CHOICES, default='1', blank=True, null=True)
    stat_state_fee_paid = models.CharField(max_length=10, choices=STATUS_CHOICES, default='1', blank=True, null=True)
    is_sent = models.BooleanField(null=True, blank=True)

    waiting_docs = models.CharField(max_length=100, null=True, blank=True)
    general_status = models.CharField(max_length=100, choices=GENERAL_STATUS_CHOICES, default='registration', null=True, blank=True)
    federal_amount = models.FloatField(null=True, blank=True, default=0)
    state_amount = models.FloatField(null=True, blank=True, default=0)
    fee_federal = models.FloatField(null=True, blank=True)
    fee_state = models.FloatField(null=True, blank=True)
    step = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.signed_and_scanned_contract:
            self.signed_and_scanned_contract_used = True
        else:
            self.signed_and_scanned_contract_used = False
        if self.passport_copy:
            self.passport_copy_used = True
        else:
            self.passport_copy_used = False
        if self.visa_copy:
            self.visa_copy_used = True
        else:
            self.visa_copy_used = False
        if self.ssn_copy:
            self.ssn_copy_used = True
        else:
            self.ssn_copy_used = False
        if self.last_paycheck_doc:
            self.last_paycheck_doc_used = True
        else:
            self.last_paycheck_doc_used = False
        if self.w2_form:
            self.w2_form_used = True
        else:
            self.w2_form_used = False
        if self.w2_lpc_e3:
            self.w2_lpc_e3_used = True
        else:
            self.w2_lpc_e3_used = False
        if self.w2_lpc_e4:
            self.w2_lpc_e4_used = True
        else:
            self.w2_lpc_e4_used = False
        if self.bank_account_screenshot:
            self.bank_account_screenshot_used = True
        else:
            self.bank_account_screenshot_used = False
        if self.us_document_copy:
            self.us_document_copy_used = True
        else:
            self.us_document_copy_used = False

        if self.federal_amount is not None:
            self.fee_federal = self.federal_amount * 0.1
        if self.state_amount is not None:
            self.fee_state = self.state_amount * 0.1

        if self.stat_declaration_submitted == '1' or self.stat_declaration_submitted is None:
            self.general_status = 'registration'
        elif self.stat_declaration_submitted == '3':
            if self.stat_waiting_federal == '3':
                if self.stat_waiting_state == '3':
                    if self.stat_federal_fee_paid == '3' and self.stat_state_fee_paid == '1':
                        self.general_status = 'federalfee'
                    elif self.stat_federal_fee_paid == '1' and self.stat_state_fee_paid == '3':
                        self.general_status = 'statefee'
                    elif self.stat_federal_fee_paid == '3' and self.stat_state_fee_paid == '3':
                        self.general_status = 'allpaid'
                    else:
                        self.general_status = 'state'
                else:
                    self.general_status = 'federal'
            else:
                self.general_status = 'declaration'

        super(Taxes, self).save(*args, **kwargs)

    def __str__(self):
        return f"Данъците на {self.first_name} {self.family_name}"
    