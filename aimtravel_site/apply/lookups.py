"""Справочници за autocomplete.

Държим ги като данни в кода, а не в базата: списъкът с акредитирани ВУЗ-ове
се мени веднъж-два пъти годишно и не заслужава таблица, миграция и админ.
Ако някога потрябва редакция от офиса, се мигрира към модел без промяна
по API-то.

Търсенето е нарочно наивно (без ILIKE в базата), защото наборът е под
200 реда и всичко се събира в паметта на процеса.
"""
from __future__ import annotations

import unicodedata
from functools import lru_cache

from .data.universities import UNIVERSITIES
from .data.cities import CITIES
from .data.majors import MAJORS


def _fold(text: str) -> str:
    """Сваля регистър и диакритика, за да съвпада „Търново“ и „търново“."""
    return "".join(
        c for c in unicodedata.normalize("NFKD", text.casefold())
        if not unicodedata.combining(c)
    )


@lru_cache(maxsize=1)
def _folded_universities() -> list[tuple[str, str, str]]:
    return [(_fold(name), name, city) for name, city in UNIVERSITIES]


@lru_cache(maxsize=1)
def _folded_cities() -> list[tuple[str, str]]:
    return [(_fold(name), name) for name in CITIES]


@lru_cache(maxsize=1)
def _folded_majors() -> list[tuple[str, str]]:
    return [(_fold(name), name) for name in MAJORS]


def universities(query: str, limit: int = 7) -> list[dict]:
    q = _fold(query)
    hits = [(folded, name, city) for folded, name, city in _folded_universities() if q in folded]
    # Съвпадение в началото се показва преди съвпадение в средата:
    # „Варна“ трябва да върне „Варненски свободен…“ преди „Медицински … — Варна“.
    hits.sort(key=lambda h: (not h[0].startswith(q), h[1]))
    return [{"value": name, "label": name, "hint": city} for _, name, city in hits[:limit]]


def cities(query: str, limit: int = 7) -> list[dict]:
    q = _fold(query)
    hits = [name for folded, name in _folded_cities() if folded.startswith(q)]
    return [{"value": name, "label": name} for name in hits[:limit]]


def majors(query: str, limit: int = 7) -> list[dict]:
    q = _fold(query)
    hits = [(folded, name) for folded, name in _folded_majors() if q in folded]
    hits.sort(key=lambda h: (not h[0].startswith(q), h[1]))
    return [{"value": name, "label": name} for _, name in hits[:limit]]
