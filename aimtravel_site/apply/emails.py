"""Автоматичният имейл при сключен договор.

Тялото е в templates/email/contract_issued.{html,txt}. Когато Стоян предостави
официалния темплейт, се сменят САМО тези два шаблона — логиката тук и
списъкът с прикачени файлове остават.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from .application_form import render_application_form
from .contracts import OPTION_LABEL
from .models import Application, ContractDocument, ProgramOption

DEPOSIT_USD = 200
SEVIS_USD = 35

SMTP_BACKEND = "django.core.mail.backends.smtp.EmailBackend"


class EmailNotConfiguredError(RuntimeError):
    """SMTP е избран, но липсва парола — Gmail ще върне 530 при изпращане."""


def _ensure_smtp_configured() -> None:
    # Без парола Django пропуска login-а, връзката "успява", а Gmail отказва
    # чак при MAIL FROM с 530 Authentication Required. Спираме по-рано с ясна
    # причина, вместо с неясна SMTP грешка.
    if settings.EMAIL_BACKEND == SMTP_BACKEND and not settings.EMAIL_HOST_PASSWORD:
        raise EmailNotConfiguredError(
            f"EMAIL_HOST_PASSWORD is empty — set EMAILPASSWORD in credentials.py "
            f"(Gmail app password for {settings.EMAIL_HOST_USER})."
        )


def build_context(application: Application) -> dict:
    agent = settings.AIM_OFFICE_AGENTS[application.office]
    return {
        "first_name": application.first_name.capitalize(),
        "full_name": application.full_name_latin,
        "contract_number": application.contract_number,
        "program_option": OPTION_LABEL[ProgramOption(application.program_option)],
        "season": application.season,
        "office_city": application.office_city,
        "agent_name": agent["name"],
        "agent_email": agent["email"],
        "agent_phone": agent["phone"],
        "deposit_usd": DEPOSIT_USD,
        "sevis_usd": SEVIS_USD,
        "price_usd": application.price_usd,
    }


def _name_slug(application: Application) -> str:
    """Filesystem-safe UPPER_SNAKE slug of the student's three names.

    Кирилицата се транслитерира през NFKD → ASCII, за да не тръгне договор с
    име, което Gmail показва като "?????".
    """
    parts = [application.first_name, application.middle_name, application.last_name]
    joined = "_".join(p.strip() for p in parts if p and p.strip())
    ascii_form = unicodedata.normalize("NFKD", joined).encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", ascii_form).strip("_")
    return cleaned.upper() or "STUDENT"


def _send_legacy_email(application: Application, document: ContractDocument) -> None:
    _ensure_smtp_configured()
    context = build_context(application)
    agent_email = context["agent_email"]
    name_slug = _name_slug(application)

    message = EmailMultiAlternatives(
        subject=f"Договор {application.contract_number} — "
        f"Summer Work & Travel USA {application.season}",
        body=render_to_string("email/contract_issued.txt", context),
        from_email=settings.AIM_FROM_EMAIL,
        to=[application.email],
        # Скрито копие до офиса, който студентът е избрал (+ CONTRACT_EMAIL_BCC).
        bcc=[agent_email, *settings.AIM_CONTRACT_EMAIL_BCC],
        # Студентът отговаря на имейла със снимката в паспортен формат —
        # този отговор трябва да падне при агента, а не в no-reply кутия.
        reply_to=[agent_email],
        headers={"X-AIM-Contract": application.contract_number},
    )
    message.attach_alternative(render_to_string("email/contract_issued.html", context), "text/html")

    # In dev without LibreOffice, `document.pdf` may actually be a .docx file
    # (see contracts.render_contract's fallback). Ship it under its real name
    # and MIME type so Gmail doesn't preview a corrupt PDF.
    contract_file = document.pdf
    contract_ext = Path(contract_file.name).suffix.lower()
    contract_mime = (
        "application/pdf"
        if contract_ext == ".pdf"
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    contract_file.open("rb")
    try:
        message.attach(
            f"Dogovor_{application.contract_number}_{name_slug}{contract_ext}",
            contract_file.read(),
            contract_mime,
        )
    finally:
        contract_file.close()

    # Application form — оригиналният бланкет с overlay-нати стойности върху
    # него, не преоформен документ.
    application_form = render_application_form(application)
    message.attach(
        f"AIM_Travel_Application_Form_{name_slug}.pdf",
        application_form.pdf_path.read_bytes(),
        "application/pdf",
    )

    message.send(fail_silently=False)

    document.email_sent_at = timezone.now()
    document.save(update_fields=["email_sent_at"])


def send_contract_issued_email(application, document):
    if application.currency != "EUR":
        return _send_legacy_email(application, document)
    from .pricing import DEPOSIT, SEVIS
    from .bank_details import bank_pdf
    context = {
        "first_name": application.first_name.capitalize(),
        "contract_number": application.contract_number,
        "season": application.season,
        "program_option": OPTION_LABEL[ProgramOption(application.program_option)],
        "price_eur": application.price_eur,
        "save_exchange": application.save_exchange,
        "protection_fee_eur": application.protection_fee_eur,
        "first_payment_eur": DEPOSIT + SEVIS + application.protection_fee_eur,
    }
    destination = "studentski@aimtravel.bg"
    message = EmailMultiAlternatives(
        subject=f"Договор {application.contract_number} | Work and Travel {application.season}",
        body=render_to_string("email/contract_issued_eur.txt", context),
        from_email=destination, to=[application.email],
        bcc=list(dict.fromkeys([destination, *settings.AIM_CONTRACT_EMAIL_BCC])),
        reply_to=[destination], headers={"X-AIM-Contract": application.contract_number},
    )
    message.attach_alternative(render_to_string("email/contract_issued_eur.html", context), "text/html")
    files = [(document.pdf, f"Dogovor_{application.contract_number}.pdf")]
    if application.save_exchange:
        if not document.annex_pdf:
            raise RuntimeError("Selected protection requires annex PDF")
        files.append((document.annex_pdf, f"Annex_{application.contract_number}.pdf"))
    for field, name in files:
        with field.open("rb") as source:
            data = source.read()
        if data[:5] != b"%PDF-":
            raise RuntimeError("Attachment is not a PDF")
        message.attach(name, data, "application/pdf")
    message.attach("AIM_Bank_Details.pdf", bank_pdf(application), "application/pdf")
    if settings.EMAIL_BACKEND == SMTP_BACKEND and not settings.EMAIL_HOST_PASSWORD:
        import subprocess
        result = subprocess.run(
            ["/usr/sbin/sendmail", "-oi", "-f", destination, "--", *message.recipients()],
            input=message.message().as_bytes(), capture_output=True, timeout=30, check=False,
        )
        if result.returncode:
            raise RuntimeError("Mail transport rejected message")
    elif message.send(fail_silently=False) != 1:
        raise RuntimeError("Mail transport did not accept message")
    document.email_sent_at = timezone.now()
    document.save(update_fields=["email_sent_at"])
