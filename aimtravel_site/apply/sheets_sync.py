"""Idempotent, retryable export of online registrations (no identity numbers)."""
import json
import logging
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone

from .models import Application, ProgramOption

log = logging.getLogger(__name__)


def registration_values(application):
    document = getattr(application, "contract_document", None)
    return [
        timezone.localtime(application.created_at, ZoneInfo("Europe/Sofia")).strftime("%d.%m.%Y %H:%M"),
        application.full_name_latin, application.email, application.phone,
        "Premium Full Arranged" if application.program_option == ProgramOption.FULL_ARRANGED else "Self Arranged",
        application.contract_number, application.season, application.base_price_eur,
        application.discount_eur, application.price_eur,
        "Да" if application.save_exchange else "Не", application.protection_fee_eur,
        232 + application.protection_fee_eur,
        application.price_eur + application.protection_fee_eur,
        f"{settings.SITE_URL.rstrip('/')}/admin/apply/application/{application.pk}/change/",
        "Изпратен" if document and document.email_sent_at else "Неизпратен",
        "Изпратено" if document and document.staff_notified_at else "Неизпратено",
        application.get_status_display(), f"{settings.SITE_URL.rstrip('/')}/zapisvane-za-brigada/",
        str(application.public_id),
    ]


def sync_registration(application):
    if application.currency != "EUR":
        return False
    try:
        # Reuse the existing private Application Form receiver; never commit secrets.
        if hasattr(settings, "ONLINE_REGISTRATION_WEBHOOK_URL"):
            url = settings.ONLINE_REGISTRATION_WEBHOOK_URL
            secret = settings.ONLINE_REGISTRATION_WEBHOOK_SECRET
        else:
            from application_form_secrets import APPLICATION_FORM_WEBHOOK_SECRET, APPLICATION_FORM_WEBHOOK_URL
            url, secret = APPLICATION_FORM_WEBHOOK_URL, APPLICATION_FORM_WEBHOOK_SECRET
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != "script.google.com" or not secret:
            raise ValueError("Invalid receiver configuration")
        payload = {"action": "online_registration", "secret": secret,
                   "registrationId": str(application.public_id), "values": registration_values(application)}
        request = Request(url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                          headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=15) as response:
            result = json.loads(response.read(4096))
        if result.get("ok") is not True or result.get("registrationId") != str(application.public_id):
            raise ValueError("Receiver did not acknowledge registration")
    except Exception:
        # Do not persist remote responses, request bodies, or credentials in logs/admin.
        Application.objects.filter(pk=application.pk).update(
            sheets_sync_error="Записването в Google Sheets не е потвърдено. Очаква повторен опит.")
        log.warning("Google Sheets sync pending for registration %s", application.public_id)
        return False
    Application.objects.filter(pk=application.pk).update(sheets_synced_at=timezone.now(), sheets_sync_error="")
    return True
