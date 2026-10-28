"""Оркестрация на подаването. View-то остава тънко, логиката е тук.

Редът е важен и е избран нарочно:
  1. резервираме номер + записваме заявката   (една транзакция)
  2. генерираме PDF-а                          (извън транзакцията — бавно е)
  3. пускаме имейла в опашка                   (най-крехката стъпка е последна)
"""
from __future__ import annotations

import logging

from django.core.files import File
from django.db import transaction, IntegrityError
from rest_framework.exceptions import ValidationError

from .contracts import render_contract
from .models import Application, ApplicationStatus, ContractCounter, ContractDocument
from .tasks import send_contract_email_task

log = logging.getLogger(__name__)


class ContractGenerationError(Exception):
    """PDF-ът не се получи. Номерът остава зает — виж коментара долу."""


@transaction.atomic
def _persist(validated: dict, consent: dict, idempotency_key: str | None) -> Application:
    from .pricing import quote
    from .models import Office
    office, season = Office.SOFIA, validated["season"]
    prices, discount = quote(validated["program_option"], validated["save_exchange"], validated.get("discount_code", ""), lock=True)
    prices.pop("first_payment_eur")
    if discount:
        discount.used_count += 1
        discount.save(update_fields=["used_count"])
    validated = {**validated, **prices, "office": office, "currency": "EUR"}
    contract_number = ContractCounter.reserve(office, season)
    return Application.objects.create(
        idempotency_key=idempotency_key or None,
        contract_number=contract_number,
        **{k: v for k, v in validated.items()
           if k not in {"turnstile_token", "accepts_terms", "declares_truth", "accepts_gdpr"}},
        **consent,
    )


def create_application(validated: dict, consent: dict,
                       idempotency_key: str | None = None) -> Application:
    if idempotency_key:
        existing = Application.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            if existing.status == ApplicationStatus.CONTRACT_FAILED or not hasattr(existing, 'contract_document'):
                raise ContractGenerationError(existing.contract_number)
            return existing          # двойно кликване не издава втори договор

    try:
        application = _persist(validated, consent, idempotency_key)
    except IntegrityError:
        application = Application.objects.filter(idempotency_key=idempotency_key).first() if idempotency_key else None
        if application is None:
            raise
        if not hasattr(application, 'contract_document'):
            raise ContractGenerationError(application.contract_number)
        return application

    try:
        rendered = render_contract(application)
    except Exception as exc:
        log.exception("Договор %s не се генерира", application.contract_number)
        # Номерът остава зает НАРОЧНО. Дупка в поредицата е безобидна;
        # два договора с един номер не са. Агентът вижда заявката като
        # `contract_failed` в админа и я пуска отново оттам.
        application.mark(ApplicationStatus.CONTRACT_FAILED)
        raise ContractGenerationError(application.contract_number) from exc

    with open(rendered.pdf_path, "rb") as pdf, open(rendered.docx_path, "rb") as docx:
        document = ContractDocument.objects.create(
            application=application,
            pdf=File(pdf, name=rendered.pdf_path.name),
            docx=File(docx, name=rendered.docx_path.name),
        )

    if rendered.annex_path:
        with open(rendered.annex_path, "rb") as annex:
            document.annex_pdf.save(rendered.annex_path.name, File(annex), save=True)

    # Имейлът тръгва през опашка, не в HTTP заявката: SMTP-то може да е бавно
    # или временно недостъпно, а договорът вече е издаден и номерът е зает.
    # transaction.on_commit гарантира, че Celery няма да види ред, който още
    # не е комитнат.
    transaction.on_commit(lambda: send_contract_email_task.delay(application.pk, document.pk))
    return application
