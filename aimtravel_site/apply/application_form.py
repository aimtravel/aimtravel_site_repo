"""Попълнена „Application Form“, върху оригиналния PDF бланкет.

Оригиналът `AIM_Travel_Application_Form.pdf` е статичен PDF без form полета,
но с идентичност (лого, QR код, „Follow us!“, оформление на секциите), която
трябва да се запази. За да излезе с реалните данни на студента, тук
изграждаме overlay PDF с reportlab на същия размер и го сливаме върху
първата страница на оригинала през pypdf. Координатите на етикетите са
извлечени от текстовия слой на PDF-а — ако някога темплейтът се пре-изнесе,
трябва да се пре-мапнат.

Полетата, които формата НЕ събира (адрес, family status, Skype, Facebook/
Instagram, emergency contact, work experience, US visa, езици, hobbies и
т.н.) остават празни — както на оригиналния бланкет.
"""
from __future__ import annotations

import io
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import reportlab
from django.conf import settings
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .models import Application

log = logging.getLogger(__name__)

# Имена на български градове и университети трябва да излизат като букви, а
# не като квадратчета. Vera-та, която идва с reportlab, няма кирилски глифи —
# затова търсим шрифт с кирилица в следния ред:
#   1) settings.AIM_APPFORM_FONT_PATH (ако е зададен)
#   2) стандартни Linux пътища (DejaVu, Liberation) — за прод
#   3) macOS Helvetica.ttc (subfontIndex=0) — за локален dev
#   4) reportlab Vera като последна защита (латиница-only, warning в логовете)
_FONT_REGULAR = "AimFormBody"
_VERA_FALLBACK = os.path.join(os.path.dirname(reportlab.__file__), "fonts", "Vera.ttf")
_LINUX_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
)
_MACOS_HELVETICA_TTC = "/System/Library/Fonts/Helvetica.ttc"
_fonts_registered = False


def _register_first_available() -> None:
    """Регистрира първия намерен шрифт под името ``_FONT_REGULAR``.

    Ако падне до Vera (без кирилица), логваме warning — операторът трябва
    да инсталира ``fonts-dejavu-core`` или да зададе ``AIM_APPFORM_FONT_PATH``.
    """
    override = getattr(settings, "AIM_APPFORM_FONT_PATH", None)
    if override and os.path.exists(override):
        pdfmetrics.registerFont(TTFont(_FONT_REGULAR, override))
        return
    for path in _LINUX_FONT_CANDIDATES:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(_FONT_REGULAR, path))
            return
    if os.path.exists(_MACOS_HELVETICA_TTC):
        pdfmetrics.registerFont(TTFont(_FONT_REGULAR, _MACOS_HELVETICA_TTC, subfontIndex=0))
        return
    log.warning(
        "application_form: няма Cyrillic-capable шрифт на системата; "
        "падам на Vera — кирилицата ще излезе като квадратчета. Инсталирай "
        "fonts-dejavu-core или задай AIM_APPFORM_FONT_PATH в settings."
    )
    pdfmetrics.registerFont(TTFont(_FONT_REGULAR, _VERA_FALLBACK))


def _ensure_fonts() -> None:
    global _fonts_registered
    if _fonts_registered:
        return
    _register_first_available()
    _fonts_registered = True


@dataclass(frozen=True)
class RenderedApplicationForm:
    pdf_path: Path


# Размерът на изходната страница — трябва да съвпадне с оригиналния PDF,
# иначе overlay-ът се разминава. Числата съответстват на MediaBox 597.6×843.6.
_PAGE_WIDTH = 597.6
_PAGE_HEIGHT = 843.6

# Координати (x, y) на baseline-а, на който трябва да седне стойността.
# Извлечени от `visitor_text` върху оригинала — виж docstring-а горе.
_FILL_FONT_SIZE = 10.5

# (x, y, max_width) — max_width е за clip, ако името е по-дълго.
_POSITIONS: dict[str, tuple[float, float, float]] = {
    # Row 668: First / Middle / Family
    "first_name": (88.0, 668.1, 90.0),
    "middle_name": (252.0, 668.1, 105.0),
    "family_name": (432.0, 668.1, 160.0),
    # Row 650: EGN / DoB / City of Birth
    "egn": (57.0, 650.1, 130.0),
    "city_of_birth": (395.0, 650.1, 195.0),
    # Row 614: Mobile (+359 already printed)
    "mobile": (453.0, 614.3, 140.0),
    # Row 596: Email
    "email": (60.0, 596.3, 155.0),
    # Row 470: University / Major
    "university": (90.0, 470.3, 87.0),
    "major": (260.0, 470.3, 115.0),
}

# „dd / mm / yyyy“ на реда за Date of Birth — маскираме, за да не се
# препокрива с истинската дата.
_DOB_MASK = (254.0, 643.0, 328.0, 658.0)  # x1, y1, x2, y2
_DOB_TEXT = (257.0, 650.1)

# Центрове на кръговете за „Year of studies: 1 2 3 4 master“.
_YEAR_CIRCLES: dict[str, tuple[float, float, float]] = {
    "1": (456.0, 470.3, 7.0),
    "2": (466.5, 470.3, 7.0),
    "3": (477.0, 470.3, 7.0),
    "4": (487.5, 470.3, 7.0),
    "master": (510.0, 470.3, 17.0),  # по-широк овал за думата
}


def _phone_digits(phone: str) -> str:
    """Оригиналната форма вече е принтирала „+359“ — рисуваме само остатъка."""
    p = (phone or "").strip()
    if p.startswith("+359"):
        return p[4:].lstrip(" -")
    return p


def _clip(canvas_obj, text: str, x: float, y: float, max_width: float) -> None:
    """Изрязва текста, ако е по-широк от полето — по-добре „…" отколкото
    да излезе върху следващия етикет."""
    if not text:
        return
    font_size = _FILL_FONT_SIZE
    width = pdfmetrics.stringWidth(text, _FONT_REGULAR, font_size)
    if width <= max_width:
        canvas_obj.drawString(x, y, text)
        return
    # Свиваме до „…" — итеративно, защото за кирилица чарстрингширинити
    # варират много.
    ellipsis = "…"
    ell_w = pdfmetrics.stringWidth(ellipsis, _FONT_REGULAR, font_size)
    trimmed = text
    while trimmed and pdfmetrics.stringWidth(trimmed, _FONT_REGULAR, font_size) + ell_w > max_width:
        trimmed = trimmed[:-1]
    canvas_obj.drawString(x, y, trimmed + ellipsis)


def _build_overlay(application: Application) -> bytes:
    _ensure_fonts()
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(_PAGE_WIDTH, _PAGE_HEIGHT))
    c.setFont(_FONT_REGULAR, _FILL_FONT_SIZE)
    c.setFillColor(black)

    values: dict[str, str] = {
        "first_name": application.first_name,
        "middle_name": application.middle_name,
        "family_name": application.last_name,
        "egn": application.egn,
        "city_of_birth": application.place_of_birth,
        "mobile": _phone_digits(application.phone),
        "email": application.email,
        "university": application.university,
        "major": application.major,
    }
    for key, (x, y, max_w) in _POSITIONS.items():
        _clip(c, values.get(key, ""), x, y, max_w)

    # Date of Birth — маскираме „dd / mm / yyyy" placeholder-а, после датата.
    c.setFillColor(white)
    c.rect(_DOB_MASK[0], _DOB_MASK[1],
           _DOB_MASK[2] - _DOB_MASK[0],
           _DOB_MASK[3] - _DOB_MASK[1], stroke=0, fill=1)
    c.setFillColor(black)
    dob = application.date_of_birth.strftime("%d / %m / %Y")
    c.drawString(_DOB_TEXT[0], _DOB_TEXT[1], dob)

    # Year of studies — заграждаме избраното число/„master".
    circle = _YEAR_CIRCLES.get(application.year_of_study)
    if circle:
        cx, cy, r = circle
        c.setStrokeColor(black)
        c.setLineWidth(0.9)
        if application.year_of_study == "master":
            c.ellipse(cx - r, cy - 5, cx + r, cy + 10, stroke=1, fill=0)
        else:
            c.circle(cx, cy + 3, r, stroke=1, fill=0)

    c.showPage()
    c.save()
    return buffer.getvalue()


def render_application_form(application: Application) -> RenderedApplicationForm:
    template_path = Path(settings.AIM_STATIC_DOCS) / "AIM_Travel_Application_Form.pdf"
    if not template_path.exists():
        raise FileNotFoundError(f"Липсва бланкет: {template_path}")

    overlay_bytes = _build_overlay(application)
    overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
    base_reader = PdfReader(str(template_path))

    writer = PdfWriter()
    first_page = base_reader.pages[0]
    first_page.merge_page(overlay_reader.pages[0])
    writer.add_page(first_page)
    for page in base_reader.pages[1:]:
        writer.add_page(page)

    out_dir = Path(tempfile.mkdtemp(prefix="aim-appform-"))
    pdf_path = out_dir / f"AIM_Travel_Application_Form_{application.contract_number}.pdf"
    with open(pdf_path, "wb") as fh:
        writer.write(fh)
    return RenderedApplicationForm(pdf_path=pdf_path)
