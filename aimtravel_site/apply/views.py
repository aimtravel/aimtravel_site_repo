from __future__ import annotations

import logging
from pathlib import PurePosixPath

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import lookups
from .models import Application, ApplicationDraft
from .serializers import (
    ApplicationCreateSerializer,
    ApplicationResultSerializer,
    DraftSerializer,
    consent_metadata,
)
from .services import ContractGenerationError, create_application
from .throttles import ApplyBurstThrottle, ApplyDailyThrottle, LookupThrottle
from .turnstile import TurnstileError, verify_turnstile

log = logging.getLogger(__name__)


class ApplicationCreateView(APIView):
    """POST /api/v1/applications — единствената точка, която издава договор."""

    permission_classes = [AllowAny]
    throttle_classes = [ApplyBurstThrottle, ApplyDailyThrottle]

    def post(self, request):
        serializer = ApplicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Skip Turnstile verification for local development
        if not getattr(settings, "TURNSTILE_DISABLED", False):
            try:
                verify_turnstile(
                    serializer.validated_data["turnstile_token"],
                    remote_ip=request.META.get("REMOTE_ADDR"),
                )
            except TurnstileError:
                return Response(
                    {"detail": "errors.antibot.failed"}, status=status.HTTP_400_BAD_REQUEST
                )

        try:
            application = create_application(
                validated=serializer.validated_data,
                consent=consent_metadata(request),
                idempotency_key=request.headers.get("Idempotency-Key", "")[:64],
            )
        except ContractGenerationError:
            return Response(
                {"detail": "errors.submitFailed"}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response(
            ApplicationResultSerializer(application).data, status=status.HTTP_201_CREATED
        )


class DraftView(APIView):
    """PUT /api/v1/applications/draft — автозапис на чернова.

    Анонимна: ключът се пази в localStorage на браузъра. Не връща данни при
    GET по чужд ключ, защото черновата съдържа ЕГН — ако ключът изтече,
    най-лошото е загубена чернова, а не изтекли данни.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ApplyBurstThrottle]

    def put(self, request):
        serializer = DraftSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        draft_id = serializer.validated_data.get("draft_id")

        draft, _ = ApplicationDraft.objects.update_or_create(
            draft_id=draft_id or None,
            defaults={"payload": serializer.validated_data["values"]},
        )
        return Response({"draft_id": str(draft.draft_id)})


class LookupView(APIView):
    """GET /api/v1/lookup/{kind}?q=… — източникът за autocomplete."""

    permission_classes = [AllowAny]
    throttle_classes = [LookupThrottle]

    KINDS = {
        "universities": lookups.universities,
        "cities": lookups.cities,
        "majors": lookups.majors,
    }

    def get(self, request, kind: str):
        finder = self.KINDS.get(kind)
        if finder is None:
            raise Http404
        query = (request.query_params.get("q") or "").strip()
        if len(query) < 2:
            return Response([])
        return Response(finder(query, limit=7))


class ContractDownloadView(APIView):
    """GET /api/v1/contracts/<public_id>/<token>/ — сваляне на договора.

    Договорът съдържа ЕГН и адрес, затова линкът е подписан и с давност.
    Виж docs/05-security-and-legal.md.
    """

    permission_classes = [AllowAny]

    def get(self, request, public_id, token):
        from .storage import verify_token

        application = Application.objects.filter(public_id=public_id).first()
        if application is None or not verify_token(application, token):
            raise Http404
        document = application.contract_document
        # Use the stored file's extension, not a hard-coded .pdf: on machines
        # without LibreOffice the "pdf" field actually holds a .docx (see the
        # fallback in contracts.render_contract). Serving docx bytes as a
        # .pdf leaves the user with an unopenable file.
        extension = PurePosixPath(document.pdf.name).suffix or ".pdf"
        return FileResponse(
            document.pdf.open("rb"),
            as_attachment=True,
            filename=f"Dogovor_{application.contract_number}{extension}",
        )


class ConfigView(APIView):
    """GET /api/v1/apply/config — какво фронтендът не бива да знае предварително.

    Държим сезона и публичния Turnstile ключ тук, а не в bundle-а, за да не
    се налага rebuild на 1 юни и при ротация на ключа.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        from .validators import upcoming_season

        return Response(
            {
                "season": upcoming_season(),
                "turnstile_site_key": settings.TURNSTILE_SITE_KEY,
                "offices": [
                    {
                        "value": "varna",
                        "label": "Офис Варна",
                        "address": "бул. „Владислав Варненчик“ 186",
                    },
                    {"value": "sofia", "label": "Офис София", "address": "бул. „Витоша“ 19"},
                ],
            }
        )
