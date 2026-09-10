"""Тестове на чистата валидация — не изискват Django и вървят за милисекунди.

Тези тестове са спецификацията на бизнес правилата. Ако Devin промени
поведение тук, значи променя договорно задължение — да пита преди това.
"""
from datetime import date

import pytest

from apps.apply.validators import (
    age_is_eligible,
    dob_from_egn,
    egn_checksum_ok,
    is_valid_latin_name,
    is_valid_phone,
    normalize_phone,
    upcoming_season,
)


class TestEgn:
    @pytest.mark.parametrize("egn", ["0546140012", "7503160127", "7523160121"])
    def test_valid_checksum(self, egn):
        assert egn_checksum_ok(egn)

    @pytest.mark.parametrize("egn", ["0546140011", "123", "", "абвгдеьжзи", "05461400121"])
    def test_invalid(self, egn):
        assert not egn_checksum_ok(egn)

    def test_dob_2000s_month_offset_40(self):
        assert dob_from_egn("0546140012") == date(2005, 6, 14)

    def test_dob_1900s_no_offset(self):
        assert dob_from_egn("7503160127") == date(1975, 3, 16)

    def test_dob_1800s_month_offset_20(self):
        # Отместване +20 значи XIX век. Няма да го срещнем при студенти,
        # но правилото трябва да е вярно, иначе кръстосаната проверка лъже.
        assert dob_from_egn("7523160121") == date(1875, 3, 16)

    def test_impossible_date_returns_none(self):
        assert dob_from_egn("0599990000") is None


class TestPhone:
    @pytest.mark.parametrize("raw,expected", [
        ("+359 888 123 456", "+359888123456"),
        ("0888123456", "+359888123456"),
        ("359888123456", "+359888123456"),
        ("00359888123456", "+359888123456"),
        ("+359-88-812-34-56", "+359888123456"),
    ])
    def test_normalization(self, raw, expected):
        assert normalize_phone(raw) == expected

    @pytest.mark.parametrize("raw", ["+359888123456", "0877123456", "0899999999"])
    def test_accepts_bg_mobile(self, raw):
        assert is_valid_phone(raw)

    @pytest.mark.parametrize("raw", ["+3592123456", "0123456789", "+1 555 0100", ""])
    def test_rejects_non_mobile(self, raw):
        assert not is_valid_phone(raw)


class TestLatinNames:
    @pytest.mark.parametrize("name", ["IVAN", "O'CONNOR", "SMITH-JONES", "Petrov"])
    def test_accepts(self, name):
        assert is_valid_latin_name(name)

    @pytest.mark.parametrize("name", ["Иван", "I", "IVAN2", "", "IVAN PETROV"])
    def test_rejects(self, name):
        assert not is_valid_latin_name(name)


class TestSeason:
    @pytest.mark.parametrize("today,expected", [
        (date(2026, 9, 8), 2027),     # есента записваме за следващото лято
        (date(2026, 12, 31), 2027),
        (date(2027, 1, 2), 2027),
        (date(2027, 5, 31), 2027),    # последният ден от старата кампания
        (date(2027, 6, 1), 2028),     # програмата стартира → следващата кампания
        (date(2027, 10, 2), 2028),
    ])
    def test_upcoming_season(self, today, expected):
        assert upcoming_season(today) == expected


class TestAgeEligibility:
    """Възрастта се мери спрямо 1 юни на сезона, не спрямо днес (чл. 8.1.3)."""

    def test_turns_18_just_before_start(self):
        assert age_is_eligible(date(2009, 5, 31), 2027)

    def test_turns_18_just_after_start(self):
        assert not age_is_eligible(date(2009, 6, 2), 2027)

    def test_exactly_28_at_start(self):
        assert age_is_eligible(date(1999, 6, 1), 2027)

    def test_29_at_start(self):
        assert not age_is_eligible(date(1998, 5, 31), 2027)
