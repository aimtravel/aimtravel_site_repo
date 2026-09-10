"""Cloudflare Turnstile — проверка на човек зад публичната форма.

Избран пред reCAPTCHA, защото не изисква съгласие за проследяване по GDPR
и в масовия случай е невидим за студента.
"""
from __future__ import annotations

import logging

import requests
from django.conf import settings

log = logging.getLogger(__name__)

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
TIMEOUT_SECONDS = 5


class TurnstileError(Exception):
    pass


def verify_turnstile(token: str, remote_ip: str | None = None) -> None:
    if not settings.TURNSTILE_SECRET_KEY:
        # В dev и в тестовете проверката се изключва изрично, а не мълчаливо.
        if settings.DEBUG or getattr(settings, "TURNSTILE_DISABLED", False):
            return
        raise TurnstileError("TURNSTILE_SECRET_KEY липсва в продукционна конфигурация")

    try:
        response = requests.post(
            VERIFY_URL,
            data={"secret": settings.TURNSTILE_SECRET_KEY, "response": token,
                  "remoteip": remote_ip},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        # Cloudflare е недостъпен. Пропускаме заявката нататък: по-добре
        # няколко бота, отколкото блокирана кампания. Останалите защити
        # (throttling, идемпотентност) остават активни.
        log.warning("Turnstile недостъпен, пропускам проверката: %s", exc)
        return

    if not payload.get("success"):
        log.info("Turnstile отхвърли заявка: %s", payload.get("error-codes"))
        raise TurnstileError(str(payload.get("error-codes")))
