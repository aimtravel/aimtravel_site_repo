"""Django view-то, което рендерира страницата (не API-то).

Държим го отделно от views.py, защото това е HTML, а не JSON —
две различни отговорности, две различни причини за промяна.
"""
from __future__ import annotations

import json

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from .validators import upcoming_season


@never_cache
def zapisvane(request):
    """GET /zapisvane-za-brigada/

    never_cache, защото страницата носи CSRF токен и сезон, който се сменя
    на 1 юни. Кеширано копие би подало на студента изтекъл токен.
    """
    season = upcoming_season()
    bootstrap = {
        "season": str(season),
        "turnstileSiteKey": settings.TURNSTILE_SITE_KEY,
        "offices": [
            {"value": "varna", "label": "Офис Варна",
             "address": "бул. „Владислав Варненчик“ 186"},
            {"value": "sofia", "label": "Офис София",
             "address": "бул. „Витоша“ 19"},
        ],
    }
    return render(request, "apply/zapisvane.html", {
        "season": season,
        # Django escape-ва стойността в атрибута; React я чете с JSON.parse.
        "bootstrap_json": json.dumps(bootstrap, ensure_ascii=False),
    })
