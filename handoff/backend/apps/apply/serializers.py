"""DRF сериализатори за заявката „Запиши се“.

Съобщенията за грешка са ключове от i18n namespace-а `apply`, не готов текст.
Фронтендът ги подава на t(), за да няма два източника на българските низове.
Ако някога добавите английска версия, бекендът не се пипа.
"""
from __future__ import annotations

from django.utils import timezone
from rest_framework import serializers

from .models import Application, Office, ProgramOption, YearOfStudy
from .validators import (
    age_is_eligible,
    dob_from_egn,
    egn_checksum_ok,
    is_valid_latin_name,
    normalize_phone,
    upcoming_season,
)


class ApplicationCreateSerializer(serializers.Serializer):
    # --- лични данни ---
    email = serializers.EmailField(error_messages={"invalid": "errors.email.invalid",
                                                   "blank": "errors.email.invalid"})
    first_name = serializers.CharField(max_length=30, trim_whitespace=True)
    middle_name = serializers.CharField(max_length=30, trim_whitespace=True)
    last_name = serializers.CharField(max_length=30, trim_whitespace=True)
    phone = serializers.CharField(max_length=24)
    date_of_birth = serializers.DateField()
    egn = serializers.RegexField(r"^\d{10}$", error_messages={"invalid": "errors.egn.checksum"})
    id_card_number = serializers.RegexField(r"^\d{9}$",
                                            error_messages={"invalid": "errors.idCard.invalid"})
    place_of_birth = serializers.CharField(max_length=80, min_length=2)

    # --- образование ---
    university = serializers.CharField(max_length=160, min_length=3)
    major = serializers.CharField(max_length=120, min_length=2)
    year_of_study = serializers.ChoiceField(choices=YearOfStudy.choices)

    # --- програма ---
    program_option = serializers.ChoiceField(choices=ProgramOption.choices)
    season = serializers.IntegerField()
    office = serializers.ChoiceField(choices=Office.choices)

    # --- декларации ---
    accepts_terms = serializers.BooleanField()
    declares_truth = serializers.BooleanField()
    accepts_gdpr = serializers.BooleanField()

    # --- анти-бот ---
    turnstile_token = serializers.CharField(write_only=True, allow_blank=False)

    # ------------------------------------------------------------------
    def validate_first_name(self, v: str) -> str:
        return self._latin(v, "firstName")

    def validate_middle_name(self, v: str) -> str:
        return self._latin(v, "middleName")

    def validate_last_name(self, v: str) -> str:
        return self._latin(v, "lastName")

    @staticmethod
    def _latin(value: str, field: str) -> str:
        value = value.strip().upper()
        if not is_valid_latin_name(value):
            raise serializers.ValidationError(f"errors.{field}.latin")
        return value

    def validate_phone(self, v: str) -> str:
        normalized = normalize_phone(v)
        from .validators import is_valid_phone

        if not is_valid_phone(normalized):
            raise serializers.ValidationError("errors.phone.invalid")
        return normalized

    def validate_egn(self, v: str) -> str:
        if not egn_checksum_ok(v):
            raise serializers.ValidationError("errors.egn.checksum")
        return v

    def validate_season(self, v: int) -> int:
        """Сезонът не е избор на потребителя. Ако дойде друг, браузърът е
        стоял отворен през нощта на 1 юни — по-добре да го отхвърлим, отколкото
        да издадем договор за приключила кампания."""
        expected = upcoming_season()
        if v != expected:
            raise serializers.ValidationError("errors.season.stale")
        return v

    def _consent(self, value: bool, key: str) -> bool:
        if value is not True:
            raise serializers.ValidationError(f"errors.consent.{key}")
        return value

    def validate_accepts_terms(self, v):
        return self._consent(v, "terms")

    def validate_declares_truth(self, v):
        return self._consent(v, "truth")

    def validate_accepts_gdpr(self, v):
        return self._consent(v, "gdpr")

    # ------------------------------------------------------------------
    def validate(self, attrs):
        egn, dob, season = attrs["egn"], attrs["date_of_birth"], attrs["season"]

        # Ако тези две се разминат, договорът излиза с едни данни,
        # а DS-2019 с други — грешка, която се хваща чак в посолството.
        if dob_from_egn(egn) != dob:
            raise serializers.ValidationError({"egn": "errors.egn.dobMismatch"})

        # Възрастовият критерий по чл. 8.1.3 се мери спрямо старта на програмата.
        if not age_is_eligible(dob, season):
            raise serializers.ValidationError({"date_of_birth": "errors.dateOfBirth.age"})

        return attrs

    # ------------------------------------------------------------------
    def create(self, validated_data) -> Application:
        """Създава заявката БЕЗ номер на договор — номерът се резервира
        от сервиза, за да е в същата транзакция като брояча."""
        raise NotImplementedError("Използвай services.create_application()")


class ApplicationResultSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(source="public_id", read_only=True)
    contract_number = serializers.CharField(read_only=True)
    contract_pdf_url = serializers.SerializerMethodField()
    email_sent_to = serializers.EmailField(source="email", read_only=True)

    def get_contract_pdf_url(self, obj: Application) -> str:
        return obj.contract_document.signed_download_url(ttl_seconds=3600)


class DraftSerializer(serializers.Serializer):
    """Черновата е свободна форма — валидира се едва при подаване.

    Нарочно не валидираме тук: студентът може да запише „ЕГН: 054“ по средата
    на писането и това не бива да е грешка.
    """

    draft_id = serializers.UUIDField(required=False, allow_null=True)
    values = serializers.DictField(child=serializers.JSONField(), allow_empty=True)

    MAX_KEYS = 40

    def validate_values(self, values: dict) -> dict:
        if len(values) > self.MAX_KEYS:
            raise serializers.ValidationError("errors.draft.tooLarge")
        allowed = set(ApplicationCreateSerializer().fields) - {"turnstile_token"}
        return {k: v for k, v in values.items() if k in allowed}


def consent_metadata(request) -> dict:
    """Кой, кога и откъде е приел договора — това е доказателството при спор."""
    now = timezone.now()
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")
    return {
        "accepted_terms_at": now,
        "declared_truth_at": now,
        "accepted_gdpr_at": now,
        "consent_ip": ip or None,
        "consent_user_agent": request.META.get("HTTP_USER_AGENT", "")[:1000],
    }
