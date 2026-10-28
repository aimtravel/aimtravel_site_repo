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
    annex_path: Path | None = None


def _legacy_context(application: Application, today: date | None = None) -> dict:
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


def _render_legacy_contract(application: Application) -> RenderedContract:
    template = Path(settings.AIM_CONTRACT_TEMPLATES) / f"contract_{application.season}.docx"
    if not template.exists():
        raise FileNotFoundError(
            f"Липсва темплейт за сезон {application.season}: {template}. "
            "Всеки сезон има собствен темплейт, защото цените и сроковете се менят."
        )

    out_dir = Path(tempfile.mkdtemp(prefix="aim-contract-"))
    docx_path = out_dir / f"Dogovor_{application.contract_number}.docx"

    document = DocxTemplate(template)
    document.render(_legacy_context(application), autoescape=True)
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


_ONES = ["нула", "едно", "две", "три", "четири", "пет", "шест", "седем", "осем", "девет"]
_TEENS = ["десет", "единадесет", "дванадесет", "тринадесет", "четиринадесет", "петнадесет", "шестнадесет", "седемнадесет", "осемнадесет", "деветнадесет"]
_TENS = ["", "", "двадесет", "тридесет", "четиридесет", "петдесет", "шестдесет", "седемдесет", "осемдесет", "деветдесет"]
_HUNDREDS = ["", "сто", "двеста", "триста", "четиристотин", "петстотин", "шестстотин", "седемстотин", "осемстотин", "деветстотин"]


def amount_words(value):
    value = int(value)
    if not 0 <= value < 2000:
        raise ValueError("Unsupported contract amount")
    if value < 10:
        return _ONES[value]
    if value < 20:
        return _TEENS[value - 10]
    if value < 100:
        tens, units = divmod(value, 10)
        return _TENS[tens] + (" и " + _ONES[units] if units else "")
    if value < 1000:
        hundreds, rest = divmod(value, 100)
        return _HUNDREDS[hundreds] + ((" и " if rest < 20 or rest % 10 == 0 else " ") + amount_words(rest) if rest else "")
    rest = value - 1000
    return "хиляда" + ((" и " if rest < 100 or rest % 100 == 0 else " ") + amount_words(rest) if rest else "")


def build_context(application, today=None):
    if application.currency != "EUR":
        return _legacy_context(application, today)
    from zoneinfo import ZoneInfo
    today = today or application.created_at.astimezone(ZoneInfo("Europe/Sofia")).date()
    price = application.price_eur
    return {
        "contract_number": application.contract_number,
        "today": today.strftime("%d.%m.%Y"),
        "full_name": application.full_name_latin,
        "egn": application.egn, "id_card_number": application.id_card_number,
        "phone": application.phone, "email": application.email,
        "program_option": OPTION_LABEL[ProgramOption(application.program_option)],
        "season": application.season,
        "documents_clause": 18 if application.program_option == "self_arranged" else 19,
        "price_eur": price, "price_words": amount_words(price),
        "balance_eur": price - 200, "balance_words": amount_words(price - 200),
        "final_payment_eur": price - 800,
        "final_payment_words": amount_words(price - 800),
    }


def _pdf(docx_path, directory):
    from .document_pdf import render_pdf
    return render_pdf(docx_path, docx_path.with_suffix(".pdf"))


def render_contract(application):
    if application.currency != "EUR":
        return _render_legacy_contract(application)
    folder = Path(settings.AIM_CONTRACT_TEMPLATES)
    template = folder / f"contract_{application.season}_{application.program_option}.docx"
    directory = Path(tempfile.mkdtemp(prefix="aim-contract-")).resolve()
    context = build_context(application)
    docx = directory / f"Dogovor_{application.contract_number}.docx"
    document = DocxTemplate(template)
    document.render(context, autoescape=True)
    document.save(docx)
    pdf = _pdf(docx, directory)
    annex = None
    if application.save_exchange:
        annex_docx = directory / f"Annex_{application.contract_number}.docx"
        document = DocxTemplate(folder / f"annex_{application.season}.docx")
        document.render(context, autoescape=True)
        document.save(annex_docx)
        annex = _pdf(annex_docx, directory)
    return RenderedContract(application.contract_number, docx, pdf, annex)
