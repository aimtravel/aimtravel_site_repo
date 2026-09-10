"""Автоматичният имейл при сключен договор.

Тялото е в templates/email/contract_issued.{html,txt}. Когато Стоян предостави
официалния темплейт, се сменят САМО тези два шаблона — логиката тук и
списъкът с прикачени файлове остават.
"""
from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from .contracts import OPTION_LABEL
from .models import Application, ContractDocument, ProgramOption

# Бланките са статични — не се генерират, само се прикачат.
STATIC_ATTACHMENTS = ("Resume_blank_AIM.docx", "AIM_Travel_Application_Form.pdf")

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


def send_contract_issued_email(application: Application, document: ContractDocument) -> None:
    context = build_context(application)
    agent_email = context["agent_email"]

    message = EmailMultiAlternatives(
        subject=f"Договор {application.contract_number} — "
                f"Summer Work & Travel USA {application.season}",
        body=render_to_string("email/contract_issued.txt", context),
        from_email=settings.AIM_FROM_EMAIL,
        to=[application.email],
        # Студентът отговаря на имейла със снимката в паспортен формат —
        # този отговор трябва да падне при агента, а не в no-reply кутия.
        reply_to=[agent_email],
        headers={"X-AIM-Contract": application.contract_number},
    )
    message.attach_alternative(render_to_string("email/contract_issued.html", context), "text/html")

    document.pdf.open("rb")
    try:
        message.attach(f"Dogovor_{application.contract_number}.pdf",
                       document.pdf.read(), "application/pdf")
    finally:
        document.pdf.close()

    for name in STATIC_ATTACHMENTS:
        message.attach_file(str(Path(settings.AIM_STATIC_DOCS) / name))

    message.send(fail_silently=False)

    document.email_sent_at = timezone.now()
    document.save(update_fields=["email_sent_at"])
