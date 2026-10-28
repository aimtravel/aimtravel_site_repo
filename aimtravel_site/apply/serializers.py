"""DRF сериализатори за заявката „Запиши се“.

Съобщенията за грешка са ключове от i18n namespace-а `apply`, не готов текст.
Фронтендът ги подава на t(), за да няма два източника на българските низове.
Ако някога добавите английска версия, бекендът не се пипа.
"""

from __future__ import annotations

from django.utils import timezone
from rest_framework import serializers

from .models import Application, ProgramOption
from .validators import (
    egn_checksum_ok,
    normalize_phone,
    upcoming_season,
)


class ApplicationCreateSerializer(serializers.Serializer):
    # --- лични данни ---
    email = serializers.EmailField(
        error_messages={"invalid": "errors.email.invalid", "blank": "errors.email.invalid"}
    )
    first_name = serializers.CharField(max_length=30, trim_whitespace=True)
    middle_name = serializers.CharField(max_length=30, trim_whitespace=True)
    last_name = serializers.CharField(max_length=30, trim_whitespace=True)
    phone = serializers.CharField(max_length=24)
    # ЕГН е незадължително. Ако е дадено, чака се точно 10 цифри + checksum.
    egn = serializers.RegexField(
        r"^\d{10}$",
        required=True,
        allow_blank=False,
        error_messages={"invalid": "errors.egn.checksum"},
    )
    id_card_number = serializers.RegexField(
        r"^[A-Za-zА-Яа-яЍѝ0-9]{9}$", error_messages={"invalid": "errors.idCard.invalid"}
    )
    # --- програма ---
    program_option = serializers.ChoiceField(choices=ProgramOption.choices)
    season = serializers.IntegerField()
    save_exchange = serializers.BooleanField()
    discount_code = serializers.CharField(max_length=32, required=False, allow_blank=True, default="")
    fee_adjustment_eur = serializers.IntegerField(min_value=0, max_value=690, required=False, default=0)

    # --- декларации ---
    accepts_terms = serializers.BooleanField()
    declares_truth = serializers.BooleanField()
    accepts_gdpr = serializers.BooleanField()

    # --- анти-бот ---
    turnstile_token = serializers.CharField(write_only=True, allow_blank=True, required=False)

    # ------------------------------------------------------------------
    def validate_first_name(self, v: str) -> str:
        return self._cyrillic(v, "firstName")

    def validate_middle_name(self, v: str) -> str:
        return self._cyrillic(v, "middleName")

    def validate_last_name(self, v: str) -> str:
        return self._cyrillic(v, "lastName")

    @staticmethod
    def _cyrillic(value: str, field: str) -> str:
        value = value.strip().upper()
        import re
        if not re.fullmatch(r"[А-Яа-яЍѝ]+(?:[ -][А-Яа-яЍѝ]+)*", value):
            raise serializers.ValidationError(f"errors.{field}.cyrillic")
        return value

    def validate_phone(self, v: str) -> str:
        normalized = normalize_phone(v)
        from .validators import is_valid_phone

        if not is_valid_phone(normalized):
            raise serializers.ValidationError("errors.phone.invalid")
        return normalized

    def validate_egn(self, v: str) -> str:
        # Празно ЕГН е валидно (полето е незадължително). Ако е попълнено,
        # минава checksum.
        if v and not egn_checksum_ok(v):
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
        from pathlib import Path
        from django.conf import settings
        template = Path(settings.AIM_CONTRACT_TEMPLATES) / f"contract_{attrs['season']}_{attrs['program_option']}.docx"
        if not template.exists():
            raise serializers.ValidationError({"program_option": "Договорът за тази опция още не е активиран. Свържи се с нас."})
        from .pricing import quote
        quote(attrs["program_option"], attrs["save_exchange"], attrs.get("discount_code", ""), adjustment=attrs["fee_adjustment_eur"])
        return attrs

    # ------------------------------------------------------------------
    def create(self, validated_data) -> Application:
        """Създава заявката БЕЗ номер на договор — номерът се резервира
        от сервиза, за да е в същата транзакция като брояча."""
        raise NotImplementedError("Използвай services.create_application()")


class ApplicationResultSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(source="public_id", read_only=True)
    contract_number = serializers.SerializerMethodField()
    contract_pdf_url = serializers.SerializerMethodField()
    email_sent_to = serializers.EmailField(source="email", read_only=True)
    email_sent = serializers.SerializerMethodField()
    annex_pdf_url = serializers.SerializerMethodField()

    def get_contract_number(self, obj):
        return obj.contract_date if obj.currency == "EUR" else obj.contract_number

    def get_email_sent(self, obj):
        from .models import ContractDocument
        return ContractDocument.objects.filter(application=obj, email_sent_at__isnull=False).exists()

    def get_annex_pdf_url(self, obj):
        document = getattr(obj, "contract_document", None)
        return document.signed_download_url() + "?document=annex" if document and document.annex_pdf else None

    def get_contract_pdf_url(self, obj: Application) -> str:
        document = getattr(obj, "contract_document", None)
        return document.signed_download_url(ttl_seconds=3600) if document else ""


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
