"""Local dev implementation for email sending.

The production version uses Celery + Redis to send the contract email and to
purge stale drafts on a schedule. Locally we send emails synchronously for testing.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


class _Task:
    def __init__(self, func):
        self._func = func

    def delay(self, *args, **kwargs) -> None:
        """Execute synchronously for local development/testing."""
        log.info(
            "apply.tasks: executing %s(%s, %s) synchronously", self._func.__name__, args, kwargs
        )
        return self._func(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)


@_Task
def send_contract_email_task(application_id: int, document_id: int) -> bool:
    """Send contract email with attachments synchronously for testing.

    Never raises: the contract is already issued, so a mail failure must not
    turn the submission into an error. Returns whether the email went out;
    `email_sent_at` stays empty on failure so the agent can resend from admin.
    """
    from .emails import EmailNotConfiguredError, send_contract_issued_email
    from .models import Application, ContractDocument

    try:
        application = Application.objects.get(pk=application_id)
        document = ContractDocument.objects.get(pk=document_id)
        send_contract_issued_email(application, document)
        log.info("apply.tasks: Contract email for %s sent", application.contract_number)
        return True
    except Application.DoesNotExist:
        log.error("apply.tasks: Application %s not found", application_id)
    except ContractDocument.DoesNotExist:
        log.error("apply.tasks: ContractDocument %s not found", document_id)
    except EmailNotConfiguredError as e:
        log.error("apply.tasks: Contract email NOT sent: %s", e)
    except Exception:
        log.exception("apply.tasks: Failed to send contract email")
    return False


@_Task
def purge_stale_drafts(days: int = 30) -> int:
    from datetime import timedelta

    from django.utils import timezone

    from .models import ApplicationDraft

    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = ApplicationDraft.objects.filter(updated_at__lt=cutoff).delete()
    log.info("apply.tasks: purged %s stale drafts", deleted)
    return deleted
