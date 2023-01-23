from django.contrib.auth import get_user_model
from django.db import models

from aimtravel_site.user_profile.validators import only_letters, only_digits

UserModel = get_user_model()


class Students(models.Model):
    MAX_NAME_LENGTH = 15
    BG_PERSONAL_ID_NUM = 10
    PASSPORT_NUM = 15
    PHONE_NUM = 15
    EMAIL_LENGTH = 40
    UNIVERSITY_NAME_LENGTH = 40
    ADDITIONAL_FIELD_LENGTH = 15

    user = models.OneToOneField(
        UserModel,
        primary_key=True,
        on_delete=models.CASCADE,
    )

    first_name = models.CharField(
        validators=(only_letters,),
        max_length=MAX_NAME_LENGTH,
        verbose_name='Име',
        blank=True,
        null=True,
    )
    middle_name = models.CharField(
        validators=(only_letters,),
        max_length=MAX_NAME_LENGTH,
        verbose_name='Презиме',
        blank=True,
        null=True,

    )
    last_name = models.CharField(
        validators=(only_letters,),
        max_length=MAX_NAME_LENGTH,
        verbose_name='Фамилия',
        blank=True,
        null=True,
    )
    date_of_birth = models.DateField(
        verbose_name='Дата на раждане',
        help_text='dd-mm-yyyy',
        blank=True,
        null=True,
    )
    place_of_birth = models.CharField(
        validators=(only_letters,),
        verbose_name='Място на раждане',
        max_length=MAX_NAME_LENGTH,
        blank=True,
        null=True,
    )
    city = models.CharField(
        verbose_name='Град',
        max_length=MAX_NAME_LENGTH,
        blank=True,
        null=True,
    )
    province = models.CharField(
        verbose_name='Област',
        max_length=MAX_NAME_LENGTH,
        blank=True,
        null=True,
    )
    street = models.CharField(
        verbose_name='Улица/ж.к.',
        max_length=30,
        blank=True,
        null=True,
    )
    bg_personal_number = models.CharField(
        validators=(only_digits,),
        max_length=BG_PERSONAL_ID_NUM,
        verbose_name='ЕГН',
        blank=True,
        null=True,
    )
    nationality = models.CharField(
        validators=(only_letters,),
        verbose_name='Националност',
        max_length=MAX_NAME_LENGTH,
        blank=True,
        null=True,
    )
    country_of_birth = models.CharField(
        verbose_name='Държава на раждане',
        max_length=MAX_NAME_LENGTH,
        blank=True,
        null=True,
    )

    id_passport_number = models.CharField(
        validators=(only_digits,),
        verbose_name='Номер на паспорт',
        max_length=PASSPORT_NUM,
        blank=True,
        null=True,
    )
    passport_date_of_issue = models.DateField(
        verbose_name='Дата на издаване',
        blank=True,
        null=True,
    )
    is_received_visa = models.BooleanField(
        verbose_name='Получена виза',
        blank=True,
        null=True,
    )
    phone = models.CharField(
        validators=(only_digits,),
        verbose_name='Телефон',
        max_length=PHONE_NUM,
        blank=True,
        null=True,
    )
    email = models.CharField(
        verbose_name='E-mail',
        max_length=EMAIL_LENGTH,
        blank=True,
        null=True,
    )
    university = models.CharField(
        validators=(only_letters,),
        verbose_name='Университет',
        max_length=UNIVERSITY_NAME_LENGTH,
        blank=True,
        null=True,
    )
    year_of_education = models.PositiveIntegerField(
        default=1,
        verbose_name='Курс',
        blank=True,
        null=True,
    )
    foreign_university = models.CharField(
        validators=(only_letters,),
        verbose_name='Чуждестранен университет',
        max_length=UNIVERSITY_NAME_LENGTH,
        blank=True,
        null=True,
    )
    is_fulltime_student = models.BooleanField(
        verbose_name='Студент "Редовно обучение"',
        blank=True,
        null=True,
    )
    search_job_pref = models.CharField(
        verbose_name='Предпочитана работа',
        max_length=ADDITIONAL_FIELD_LENGTH,
        blank=True,
        null=True,
    )
    how_to_reach = models.CharField(
        verbose_name='Как да комуникираме?',
        max_length=ADDITIONAL_FIELD_LENGTH,
        blank=True,
        null=True,
    )
    visa_photo = models.URLField(
        verbose_name='Снимка за ВИЗА',
        default='https://cdn5.vectorstock.com/i/1000x1000/54/34/a-student-boy-cartoon-character-isolated-on-white-vector-36115434.jpg',

        max_length=200,
        blank=True,
        null=True,
    )
    file_field = models.FileField(
        upload_to='files/%Y-%m-%d',
        null=True,
        blank=True,
    )

    def __str__(self):
        name_str = f"{self.user}\n"
        if self.first_name:
            name_str += '\n' + '-' + '\n' + self.first_name
        if self.last_name:
            name_str += '\n' + self.last_name
        return name_str


class Employee(models.Model):
    MAX_NAME_LENGTH = 15
    MAX_ROLE_LENGTH = 20
    PHONE_NUM = 15
    MAX_URL_LENGTH = 200
    EMAIL_LENGTH = 40

    user = models.OneToOneField(
        UserModel,
        primary_key=True,
        on_delete=models.CASCADE,
    )
    employee_first_name = models.CharField(
        verbose_name='Име',
        validators=(only_letters,),
        max_length=MAX_NAME_LENGTH,
        blank=True,
        null=True,
    )
    employee_last_name = models.CharField(
        verbose_name='Фамилия',
        validators=(only_letters,),
        max_length=MAX_NAME_LENGTH,
        blank=True,
        null=True,
    )
    employee_role = models.CharField(
        verbose_name='Позиция',
        max_length=MAX_ROLE_LENGTH,
        blank=True,
        null=True,
    )
    employee_pic = models.URLField(
        default='https://media.istockphoto.com/id/1300845620/vector/user-icon-flat-isolated-on-white-background-user-symbol-vector-illustration.jpg?s=612x612&w=0&k=20&c=yBeyba0hUkh14_jgv1OKqIH0CCSWU_4ckRkAoy2p73o=',
        max_length=MAX_URL_LENGTH,
        blank=True,
        null=True,
    )
    employee_phone = models.CharField(
        validators=(only_digits,),
        max_length=PHONE_NUM,
        blank=True,
        null=True,
    )
    employee_email = models.CharField(
        max_length=EMAIL_LENGTH,
        blank=True,
        null=True,
    )



