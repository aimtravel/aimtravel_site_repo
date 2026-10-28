from __future__ import annotations

import os
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models, transaction
from django.utils import timezone


class _ContractStorage(FileSystemStorage):
    """Договорите съдържат ЕГН и адрес: пазят се извън публичния MEDIA_ROOT
    (settings.APPLY_PRIVATE_ROOT) и се свалят само през подписания линк.

    Папката се чете от settings при всяко ползване, не веднъж при старт."""

    @property
    def base_location(self):
        return settings.APPLY_PRIVATE_ROOT

    @property
    def location(self):
        return os.path.abspath(self.base_location)


def contract_storage() -> FileSystemStorage:
    return _ContractStorage()


class ProgramOption(models.TextChoices):
    FULL_ARRANGED = "full_arranged", "FULL ARRANGED"
    SELF_ARRANGED = "self_arranged", "SELF ARRANGED"


class Office(models.TextChoices):
    VARNA = "varna", "Варна"
    SOFIA = "sofia", "София"


class YearOfStudy(models.TextChoices):
    Y1 = "1", "1 курс"
    Y2 = "2", "2 курс"
    Y3 = "3", "3 курс"
    Y4 = "4", "4 курс"
    MASTER = "master", "Магистратура"


OFFICE_CODE = {Office.VARNA: "VAR", Office.SOFIA: "SOF"}
OFFICE_CITY = {Office.VARNA: "Варна", Office.SOFIA: "София"}
OPTION_PRICE_USD = {ProgramOption.FULL_ARRANGED: 1750, ProgramOption.SELF_ARRANGED: 1250}


class ContractCounter(models.Model):
    """Един ред на (офис, сезон).

    Номерацията е поредна и на офис, защото всеки офис работи независимо
    и агентът трябва да може да разчете номера на телефона. Резервирането
    минава през SELECT … FOR UPDATE, за да няма два еднакви номера при
    едновременни подавания.
    """

    office = models.CharField(max_length=8, choices=Office.choices)
    season = models.PositiveSmallIntegerField()
    last_number = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["office", "season"], name="uniq_counter_office_season"),
        ]

    def __str__(self) -> str:
        return f"{self.office}/{self.season}: {self.last_number}"

    @classmethod
    @transaction.atomic
    def reserve(cls, office: str, season: int) -> str:
        counter, _ = cls.objects.select_for_update().get_or_create(office=office, season=season)
        counter.last_number += 1
        counter.save(update_fields=["last_number"])
        return f"AIM-{OFFICE_CODE[Office(office)]}-{season}-{counter.last_number:05d}"


class ApplicationStatus(models.TextChoices):
    CONTRACT_ISSUED = "contract_issued", "Договорът е издаден"
    CONTRACT_FAILED = "contract_failed", "Договорът не се генерира"
    EMAIL_FAILED = "email_failed", "Имейлът не тръгна"
    CANCELLED = "cancelled", "Отказана"


class Application(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Пази POST-а от двойно кликване и от retry на мрежата.
    idempotency_key = models.CharField(max_length=64, unique=True, null=True, blank=True)

    # --- лични данни ---
    email = models.EmailField()
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=16)
    date_of_birth = models.DateField(null=True, blank=True)
    egn = models.CharField(max_length=10, blank=True)
    id_card_number = models.CharField(max_length=9)
    place_of_birth = models.CharField(max_length=80, blank=True)

    # --- образование ---
    university = models.CharField(max_length=160, blank=True)
    major = models.CharField(max_length=120, blank=True)
    year_of_study = models.CharField(max_length=8, choices=YearOfStudy.choices, blank=True)

    # --- програма ---
    program_option = models.CharField(max_length=16, choices=ProgramOption.choices)
    season = models.PositiveSmallIntegerField()
    office = models.CharField(max_length=8, choices=Office.choices)

    # Snapshots preserve agreed prices even if a code is changed later.
    currency = models.CharField(max_length=3, default="USD")
    base_price_eur = models.PositiveIntegerField(null=True, blank=True)
    discount_eur = models.PositiveIntegerField(default=0)
    price_eur = models.PositiveIntegerField(null=True, blank=True)
    discount_code = models.CharField(max_length=32, blank=True)
    save_exchange = models.BooleanField(default=False)
    protection_fee_eur = models.PositiveIntegerField(default=0)

    # --- декларации (доказателство за съгласие по ЗЗЛД и чл. 313 НК) ---
    accepted_terms_at = models.DateTimeField()
    declared_truth_at = models.DateTimeField()
    accepted_gdpr_at = models.DateTimeField()
    consent_ip = models.GenericIPAddressField(null=True, blank=True)
    consent_user_agent = models.TextField(blank=True)

    contract_number = models.CharField(max_length=32, unique=True)
    status = models.CharField(max_length=24, choices=ApplicationStatus.choices,
                              default=ApplicationStatus.CONTRACT_ISSUED)
    created_at = models.DateTimeField(auto_now_add=True)
    sheets_synced_at = models.DateTimeField(null=True, blank=True)
    sheets_sync_error = models.CharField(max_length=200, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["office", "season"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.contract_number} · {self.full_name_latin}"

    @property
    def full_name_latin(self) -> str:
        return f"{self.first_name} {self.middle_name} {self.last_name}"

    @property
    def office_city(self) -> str:
        return OFFICE_CITY[Office(self.office)]

    @property
    def price_usd(self) -> int:
        return OPTION_PRICE_USD[ProgramOption(self.program_option)]

    def mark(self, status: str) -> None:
        self.status = status
        self.save(update_fields=["status"])


class ContractDocument(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE,
                                       related_name="contract_document")
    pdf = models.FileField(upload_to="contracts/%Y/%m/", storage=contract_storage)
    docx = models.FileField(upload_to="contracts/%Y/%m/", storage=contract_storage,
                            null=True, blank=True)
    annex_pdf = models.FileField(upload_to="contracts/%Y/%m/", storage=contract_storage, blank=True)
    generated_at = models.DateTimeField(default=timezone.now)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    staff_notified_at = models.DateTimeField(null=True, blank=True)

    def signed_download_url(self, ttl_seconds: int = 3600) -> str:
        """Договорът съдържа ЕГН — линкът не бива да е публичен и вечен.

        При S3/MinIO storage това е presigned URL. При локален storage
        Devin трябва да върне URL към view-то `contract_download`, което
        проверява подписан токен (виж docs/05-security-and-legal.md).
        """
        from .storage import signed_url  # локален импорт: избягва цикъл при миграции

        return signed_url(self.pdf, ttl_seconds=ttl_seconds)


class ApplicationDraft(models.Model):
    """Автозапис на чернова. Анонимна — ключът живее в localStorage на браузъра.

    Черновите се чистят с management команда след 30 дни: съдържат ЕГН,
    а нямаме основание да ги пазим за незавършена заявка.
    """

    draft_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    payload = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["updated_at"])]


class DiscountCode(models.Model):
    code = models.CharField(max_length=32, unique=True)
    amount_eur = models.PositiveIntegerField()
    season = models.PositiveSmallIntegerField(default=2027)
    active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0, editable=False)

    def clean(self):
        from django.core.exceptions import ValidationError
        import re
        self.code = self.code.strip().upper()
        if not re.fullmatch(r"[A-Z0-9-]{3,32}", self.code):
            raise ValidationError({"code": "Използвай латински букви, цифри или тире."})
        if not 10 <= self.amount_eur <= 690 or self.amount_eur % 10:
            raise ValidationError({"amount_eur": "Отстъпка от 10 до 690 евро, кратна на 10."})
        if self.max_uses < 1 or self.max_uses < self.used_count:
            raise ValidationError({"max_uses": "Лимитът трябва да покрива използваните кодове."})
        if self.starts_at and self.expires_at and self.expires_at <= self.starts_at:
            raise ValidationError({"expires_at": "Крайният срок трябва да е след началния."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code}: {self.amount_eur} EUR"
