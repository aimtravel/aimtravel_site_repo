"""Подписани линкове към договора.

Договорът съдържа три имена, ЕГН, номер на лична карта и адрес. Линкът към
него не бива да е познаваем, вечен или индексируем.

Две реализации според storage backend-а:
  * S3/MinIO → presigned URL, изтича сам;
  * локален диск → подписан токен + view, което го проверява.
"""
from __future__ import annotations

from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.urls import reverse

SALT = "apply.contract"


def _signer() -> TimestampSigner:
    return TimestampSigner(salt=SALT)


def make_token(application) -> str:
    return _signer().sign(str(application.public_id))


def verify_token(application, token: str, max_age: int = 3600) -> bool:
    try:
        value = _signer().unsign(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return False
    return value == str(application.public_id)


def signed_url(file_field, ttl_seconds: int = 3600) -> str:
    storage = file_field.storage

    # boto3-базираните storage-и сами правят presigned URL.
    if hasattr(storage, "url") and getattr(storage, "querystring_auth", False):
        return storage.url(file_field.name, expire=ttl_seconds)

    application = file_field.instance.application
    path = reverse("apply:contract-download", kwargs={
        "public_id": application.public_id,
        "token": make_token(application),
    })
    return f"{settings.SITE_URL}{path}"
