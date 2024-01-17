from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    bg_personal_number = models.CharField(
        validators=(only_digits,),
        max_length=BG_PERSONAL_ID_NUM,
        verbose_name='ЕГН',
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

    nationality = models.CharField(
        validators=(only_letters,),
        verbose_name='Националност',
        max_length=MAX_NAME_LENGTH,
        blank=True,
        null=True,
    )
    family_status = models.CharField(
        validators=(only_letters,),
        verbose_name='Семеен статус',
        max_length=10,
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
    emergency_contact_name = models.CharField(
        verbose_name='Контакт за спешни случаи',
        max_length=40,
        blank=True,
        null=True,
    )
    emergency_contact_phone = models.CharField(
        verbose_name='Телефон',
        max_length=13,
        blank=True,
        null=True,
    )
    emergency_contact_email = models.CharField(
        verbose_name='E-mail',
        max_length=EMAIL_LENGTH,
        blank=True,
        null=True,
    )
    emergency_contact_relationship = models.CharField(
        verbose_name='Връзка',
        max_length=15,
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
    major_study = models.CharField(
        verbose_name="Специалност",
        max_length=50,
        blank=True,
        null=True,
    )

    year_of_education = models.PositiveIntegerField(
        default=1,
        verbose_name='Курс',
        blank=True,
        null=True,
    )
    is_fulltime_student = models.BooleanField(
        verbose_name='Студент "Редовно обучение"',
        blank=True,
        null=True,
    )
    possible_begin_date = models.DateField(
        verbose_name='Дата на започване',
        blank=True,
        null=True,
    )
    possible_finish_date = models.DateField(
        verbose_name='Дата на приключване',
        blank=True,
        null=True,
    )
    is_wat_before = models.BooleanField(
        verbose_name='Участвал ли си в WAT преди?',
        blank=True,
        null=True,
    )
    wat_before_year = models.CharField(
        verbose_name='Ако да, коя година',
        max_length=4,
        blank=True,
        null=True,
    )

    position_held1 = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )
    position_period1 = models.CharField(
        max_length=25,
        blank=True,
        null=True,
    )
    employer_name1 = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )
    employer_city1 = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )
    position_held2 = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )
    position_period2 = models.CharField(
        max_length=25,
        blank=True,
        null=True,
    )
    employer_name2 = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )
    employer_city2 = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )
    visa_before = models.BooleanField(
        blank=True,
        null=True,
    )
    visa_before_year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
    )
    issued_visa_before = models.BooleanField(
        blank=True,
        null=True,
    )
    issued_visa_before_type = models.CharField(
        max_length=4,
        blank=True,
        null=True,
    )
    purpose_of_visit = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )
    any_relatives_in_USA = models.BooleanField(
        blank=True,
        null=True,
    )
    relatives_kind = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    knowledge_of_english = models.CharField(
        max_length=10,
        blank=True,
        null=True,
    )
    other_language = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )
    other_language_level = models.CharField(
        max_length=10,
        blank=True,
        null=True,
    )
    hobby = models.TextField(
        blank=True,
        null=True,
    )
    personal_qualities = models.TextField(
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

    foreign_university = models.CharField(
        validators=(only_letters,),
        verbose_name='Чуждестранен университет',
        max_length=UNIVERSITY_NAME_LENGTH,
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

    file_field = models.FileField(
        upload_to='files/%Y-%m-%d',
        null=True,
        blank=True,
    )
    visa_photo = models.FileField(
        upload_to='students/student_pic/',
        default='profile/default_profile_pic.jpg',
        verbose_name="Снимка за виза",
        blank=True,
        null=True,
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


@receiver(post_save, sender=UserModel)
def update_employee_names(sender, instance, **kwargs):
    # Update Employee names when UserModel names are updated
    try:
        employee_instance = Employee.objects.get(user=instance)
        employee_instance.employee_first_name = instance.first_name
        employee_instance.employee_last_name = instance.last_name
        employee_instance.save()
    except Employee.DoesNotExist:
        # Handle the case where Employee instance does not exist for the given UserModel
        pass


# Connect the signal
post_save.connect(update_employee_names, sender=UserModel)
