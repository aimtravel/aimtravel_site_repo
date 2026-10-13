"""Ограничения за публичната форма.

Без тях един скрипт изяжда поредицата от номера на договори за минути
и праща стотици имейли с прикачени файлове от нашия домейн — което
освен всичко друго вреди на репутацията на изпращача.
"""
from __future__ import annotations

from rest_framework.throttling import SimpleRateThrottle


class _IpThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}


class ApplyBurstThrottle(_IpThrottle):
    """Пресича автоматизирано подаване. Човек не подава два пъти в минута."""
    scope = "apply_burst"      # settings: "5/min"


class ApplyDraftBurstThrottle(_IpThrottle):
    """Автозаписът на чернова стреля на всяка пауза при писане (виж
    TIMEOUT_SAVE_DRAFT във фронтенда) — отделен, по-щедър scope от
    ApplyBurstThrottle, за да не изяжда бюджета на финалния submit преди
    потребителят изобщо да е стигнал до бутона "Изпрати"."""
    scope = "apply_draft_burst"    # settings: "30/min"


class ApplyDailyThrottle(_IpThrottle):
    """Таван на ден за един IP. Оставен е достатъчно висок за университетски
    NAT, откъдето може да подадат няколко студента от една мрежа."""
    scope = "apply_day"        # settings: "20/day"


class LookupThrottle(_IpThrottle):
    """Autocomplete-ът се вика при писане — лимитът е висок, но не безкраен."""
    scope = "lookup"           # settings: "120/min"


# ---------------------------------------------------------------------------
# Добави в settings.py:
#
# REST_FRAMEWORK = {
#     "DEFAULT_THROTTLE_RATES": {
#         "apply_burst": "5/min",
#         "apply_draft_burst": "30/min",
#         "apply_day": "20/day",
#         "lookup": "120/min",
#     },
# }
#
# ВАЖНО: DRF throttling пази броячите в кеша. С LocMemCache всеки gunicorn
# процес има собствен брояч и лимитът се умножава по броя работници.
# Задължително Redis в продукция.
# ---------------------------------------------------------------------------
