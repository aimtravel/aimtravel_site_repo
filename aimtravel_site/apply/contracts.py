"""Генериране на договора: .docx темплейт → попълнен .docx → PDF.

ПРЕДПОСТАВКА, която Devin трябва да изпълни преди този модул да работи:
`AIM_Travel_WAT_Contract_template_2026.docx` е с твърдо въведени данни на
конкретен участник. Трябва еднократно да се превърне в темплейт — виж
docs/07-contract-template.md за пълния списък от замени.
"""
from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from django.conf import settings
from docxtpl import DocxTemplate

from .models import Application, ProgramOption

log = logging.getLogger(__name__)

OPTION_LABEL = {
    ProgramOption.FULL_ARRANGED: "FULL ARRANGED",
    ProgramOption.SELF_ARRANGED: "SELF ARRANGED",
}

LIBREOFFICE_TIMEOUT_SECONDS = 120


@dataclass(frozen=True)
class RenderedContract:
    number: str
    docx_path: Path
    pdf_path: Path


def build_context(application: Application, today: date | None = None) -> dict:
    """Стойностите за merge полетата в темплейта."""
    today = today or date.today()
    return {
        "contract_number": application.contract_number,
        "today": today.strftime("%d.%m.%Y"),
        "city": application.office_city,
        "full_name": application.full_name_latin,
        "egn": application.egn,
        "id_card_number": application.id_card_number,
        "citizenship": "България",
        "phone": application.phone,
        "email": application.email,
        "date_of_birth": application.date_of_birth.strftime("%d.%m.%Y"),
        "place_of_birth": application.place_of_birth,
        "university": application.university,
        "program_option": OPTION_LABEL[ProgramOption(application.program_option)],
        "season": application.season,
        "price_usd": application.price_usd,
        "manager_name": settings.AIM_MANAGER_NAME,
        "company_uic": settings.AIM_COMPANY_UIC,
    }


def render_contract(application: Application) -> RenderedContract:
    template = Path(settings.AIM_CONTRACT_TEMPLATES) / f"contract_{application.season}.docx"
    if not template.exists():
        raise FileNotFoundError(
            f"Липсва темплейт за сезон {application.season}: {template}. "
            "Всеки сезон има собствен темплейт, защото цените и сроковете се менят."
        )

    out_dir = Path(tempfile.mkdtemp(prefix="aim-contract-"))
    docx_path = out_dir / f"Dogovor_{application.contract_number}.docx"

    document = DocxTemplate(template)
    document.render(build_context(application))
    document.save(docx_path)

    # LibreOffice headless. Договорът тръгва като PDF, за да не може да бъде
    # редактиран случайно от студента преди подписване.
    #
    # Local dev fallback: if `soffice` is not installed on this machine we
    # skip the PDF conversion and treat the .docx as the "contract" file.
    # Emails will then attach the .docx directly. Production must have
    # LibreOffice installed — this branch only kicks in when the binary is
    # missing, never as a silent quality regression.
    pdf_path = docx_path.with_suffix(".pdf")
    if shutil.which("soffice") is None:
        log.warning(
            "soffice binary not found; skipping PDF conversion and shipping .docx as the contract"
        )
        return RenderedContract(application.contract_number, docx_path, docx_path)

    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(docx_path)],
        check=True, timeout=LIBREOFFICE_TIMEOUT_SECONDS, capture_output=True,
    )

    if not pdf_path.exists():
        raise RuntimeError(f"LibreOffice не произведе PDF за {application.contract_number}")
    return RenderedContract(application.contract_number, docx_path, pdf_path)
