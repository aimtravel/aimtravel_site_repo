from __future__ import annotations

import logging

from celery import shared_task

from .emails import send_contract_issued_email
from .models import Application, ApplicationStatus, ContractDocument

log = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=60,        # 1 мин, 2, 4, 8 …
    retry_backoff_max=3600,
    retry_jitter=True,
    max_retries=6,
    acks_late=True,
)
def send_contract_email_task(self, application_id: int, document_id: int) -> None:
    application = Application.objects.get(pk=application_id)
    document = ContractDocument.objects.get(pk=document_id)

    if document.email_sent_at:
        return                # retry след частичен успех не праща втори имейл

    try:
        send_contract_issued_email(application, document)
    except Exception:
        if self.request.retries >= self.max_retries:
            # Изчерпани опити: маркираме заявката, за да я види агентът в админа.
            # Договорът е валиден и е записан — липсва само имейлът.
            log.exception("Имейлът за %s се провали окончателно", application.contract_number)
            application.mark(ApplicationStatus.EMAIL_FAILED)
        raise


@shared_task
def purge_stale_drafts(days: int = 30) -> int:
    """Черновите съдържат ЕГН. Нямаме основание да ги пазим за незавършена
    заявка — чистят се по график (Celery beat, веднъж дневно)."""
    from datetime import timedelta

    from django.utils import timezone

    from .models import ApplicationDraft

    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = ApplicationDraft.objects.filter(updated_at__lt=cutoff).delete()
    log.info("Изтрити %s стари чернови", deleted)
    return deleted
