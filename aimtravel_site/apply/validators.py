"""Чисти функции за валидация — без Django и без DRF.

Държим ги отделно, защото се използват на три места: сериализаторите,
админ импорта и тестовете. Огледални на frontend/src/apply/validation.ts —
при промяна тук се пипа и там.
"""
from __future__ import annotations

import re
from datetime import date

LATIN_NAME = re.compile(r"^[A-Za-z][A-Za-z'\-]{1,29}$")
BG_MOBILE = re.compile(r"^\+359[789]\d{8}$")
EGN_WEIGHTS = (2, 4, 8, 5, 10, 9, 7, 3, 6)

MIN_AGE = 18
MAX_AGE = 28


def normalize_phone(value: str) -> str:
    """+359 88 812 34 56 → +359888123456. Приема и 0888…, и 359…"""
    digits = re.sub(r"[^\d+]", "", value or "")
    if digits.startswith("00359"):
        digits = "+" + digits[2:]
    elif digits.startswith("0"):
        digits = "+359" + digits[1:]
    elif digits.startswith("359"):
        digits = "+" + digits
    return digits


def is_valid_phone(value: str) -> bool:
    return bool(BG_MOBILE.match(normalize_phone(value)))


def is_valid_latin_name(value: str) -> bool:
    return bool(LATIN_NAME.match(value or ""))


def egn_checksum_ok(egn: str) -> bool:
    if not re.fullmatch(r"\d{10}", egn or ""):
        return False
    total = sum(w * int(d) for w, d in zip(EGN_WEIGHTS, egn))
    return (total % 11) % 10 == int(egn[9])


def dob_from_egn(egn: str) -> date | None:
    """ЕГН носи датата на раждане. Месецът е отместен: +40 за 2000-те, +20 за 1800-те."""
    if not re.fullmatch(r"\d{10}", egn or ""):
        return None
    year, month, day = int(egn[0:2]), int(egn[2:4]), int(egn[4:6])
    if month > 40:
        month, year = month - 40, year + 2000
    elif month > 20:
        month, year = month - 20, year + 1800
    else:
        year += 1900
    try:
        return date(year, month, day)
    except ValueError:
        return None


def season_start(season: int) -> date:
    """Програмата стартира условно на 1 юни. Спрямо тази дата се мери възрастта."""
    return date(season, 6, 1)


def age_at(dob: date, at: date) -> int:
    return at.year - dob.year - ((at.month, at.day) < (dob.month, dob.day))


def upcoming_season(today: date | None = None) -> int:
    """Записваме винаги за предстоящото лято — никога за години напред.

    От 1 юни нататък текущата кампания е приключила, значи следващата е догодина.
    Есен 2026 → 2027. Март 2027 → пак 2027. Юни 2027 → 2028.
    """
    today = today or date.today()
    return today.year + 1 if today.month >= 6 else today.year


def age_is_eligible(dob: date, season: int) -> bool:
    return MIN_AGE <= age_at(dob, season_start(season)) <= MAX_AGE
