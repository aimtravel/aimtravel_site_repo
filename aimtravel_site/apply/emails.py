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
        "portal_url": f"{settings.SITE_URL}/profil",
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


def send_contract_issued_email(application: Application, document: ContractDocument) -> None:
    context = build_context(application)
    agent_email = context["agent_email"]
    name_slug = _name_slug(application)

    message = EmailMultiAlternatives(
        subject=f"Договор {application.contract_number} — "
        f"Summer Work & Travel USA {application.season}",
        body=render_to_string("email/contract_issued.txt", context),
        from_email=settings.AIM_FROM_EMAIL,
        to=["stoyan.ch.stoyanov11@gmail.com"],  # application.email
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
