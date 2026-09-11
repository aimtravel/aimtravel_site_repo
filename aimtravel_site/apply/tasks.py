"""Local dev stubs for the Celery tasks.

The production version uses Celery + Redis to send the contract email and to
purge stale drafts on a schedule. Locally we neither install Celery nor run a
worker; these stand-ins keep imports working and simply log what would have
happened, so the API and admin actions run without a broker.
"""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)


class _Task:
    def __init__(self, func):
        self._func = func

    def delay(self, *args, **kwargs) -> None:
        log.info("apply.tasks stub: would enqueue %s(%s, %s)",
                 self._func.__name__, args, kwargs)

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)


@_Task
def send_contract_email_task(application_id: int, document_id: int) -> None:
    log.info("apply.tasks stub: send_contract_email_task(%s, %s)",
             application_id, document_id)


@_Task
def purge_stale_drafts(days: int = 30) -> int:
    from datetime import timedelta

    from django.utils import timezone

    from .models import ApplicationDraft

    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = ApplicationDraft.objects.filter(updated_at__lt=cutoff).delete()
    log.info("apply.tasks stub: purged %s stale drafts", deleted)
    return deleted
