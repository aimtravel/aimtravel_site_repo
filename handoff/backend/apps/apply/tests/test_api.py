"""Интеграционни тестове на API-то. Изискват Django + DRF + pytest-django.

Всеки тест тук пази поведение, което вече е обмислено. Ако някой падне,
първо провери дали промяната е нарочна, преди да „оправиш“ теста.
"""
from __future__ import annotations

from datetime import date
from unittest import mock

import pytest
from django.urls import reverse

from apps.apply.models import Application, ContractCounter
from apps.apply.validators import upcoming_season

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload():
    season = upcoming_season()
    return {
        "email": "ivan.petrov@gmail.com",
        "first_name": "IVAN",
        "middle_name": "PETROV",
        "last_name": "DIMITROV",
        "phone": "+359 888 123 456",
        "date_of_birth": "2005-06-14",
        "egn": "0546140012",
        "id_card_number": "123456789",
        "place_of_birth": "Варна",
        "university": "Икономически университет — Варна",
        "major": "Информатика",
        "year_of_study": "2",
        "program_option": "full_arranged",
        "season": season,
        "office": "varna",
        "accepts_terms": True,
        "declares_truth": True,
        "accepts_gdpr": True,
        "turnstile_token": "test-token",
    }


@pytest.fixture(autouse=True)
def _no_turnstile(settings):
    settings.TURNSTILE_DISABLED = True
    settings.TURNSTILE_SECRET_KEY = ""


@pytest.fixture(autouse=True)
def _fake_contract(tmp_path):
    """Не пускаме LibreOffice в тестовете — бавно е и не е това, което мерим."""
    from apps.apply.contracts import RenderedContract

    def fake(application):
        docx = tmp_path / f"{application.contract_number}.docx"
        pdf = tmp_path / f"{application.contract_number}.pdf"
        docx.write_bytes(b"docx")
        pdf.write_bytes(b"%PDF-1.4 fake")
        return RenderedContract(application.contract_number, docx, pdf)

    with mock.patch("apps.apply.services.render_contract", side_effect=fake):
        yield


def post(client, payload, **headers):
    return client.post(reverse("apply:application-create"), payload,
                       content_type="application/json", **headers)


class TestHappyPath:
    def test_creates_application_and_returns_contract_number(self, client, payload):
        response = post(client, payload)
        assert response.status_code == 201

        body = response.json()
        assert body["contract_number"] == f"AIM-VAR-{payload['season']}-00001"
        assert body["email_sent_to"] == "ivan.petrov@gmail.com"
        assert body["contract_pdf_url"]

    def test_queues_email_once(self, client, payload):
        with mock.patch("apps.apply.services.send_contract_email_task.delay") as delay:
            post(client, payload)
        delay.assert_called_once()

    def test_stores_consent_evidence(self, client, payload):
        post(client, payload, HTTP_USER_AGENT="pytest-agent")
        application = Application.objects.get()
        assert application.accepted_gdpr_at is not None
        assert application.consent_user_agent == "pytest-agent"


class TestContractNumbering:
    def test_sequence_is_per_office(self, client, payload):
        post(client, payload)
        post(client, {**payload, "office": "sofia", "email": "b@x.bg"})
        numbers = set(Application.objects.values_list("contract_number", flat=True))
        assert numbers == {f"AIM-VAR-{payload['season']}-00001",
                           f"AIM-SOF-{payload['season']}-00001"}

    def test_sequence_increments(self, client, payload):
        post(client, payload)
        post(client, {**payload, "email": "b@x.bg"})
        assert ContractCounter.objects.get(office="varna").last_number == 2

    def test_failed_generation_keeps_the_number_burned(self, client, payload):
        """Дупка в поредицата е безобидна; два договора с един номер не са."""
        with mock.patch("apps.apply.services.render_contract", side_effect=RuntimeError):
            assert post(client, payload).status_code == 503
        response = post(client, {**payload, "email": "b@x.bg"})
        assert response.json()["contract_number"].endswith("00002")


class TestIdempotency:
    def test_same_key_returns_same_contract(self, client, payload):
        first = post(client, payload, HTTP_IDEMPOTENCY_KEY="abc-123")
        second = post(client, payload, HTTP_IDEMPOTENCY_KEY="abc-123")
        assert first.json()["contract_number"] == second.json()["contract_number"]
        assert Application.objects.count() == 1


class TestValidation:
    def test_rejects_cyrillic_names(self, client, payload):
        response = post(client, {**payload, "first_name": "Иван"})
        assert response.status_code == 400
        assert "errors.firstName.latin" in str(response.json())

    def test_rejects_egn_that_contradicts_date_of_birth(self, client, payload):
        response = post(client, {**payload, "date_of_birth": "2005-06-15"})
        assert response.status_code == 400
        assert "errors.egn.dobMismatch" in str(response.json())

    def test_rejects_applicant_too_young_at_program_start(self, client, payload):
        season = payload["season"]
        too_young = date(season - 17, 7, 1)      # ще навърши 18 след старта
        response = post(client, {**payload, "date_of_birth": too_young.isoformat(),
                                 "egn": "0000000000"})
        assert response.status_code == 400

    def test_rejects_stale_season(self, client, payload):
        response = post(client, {**payload, "season": payload["season"] + 1})
        assert response.status_code == 400
        assert "errors.season.stale" in str(response.json())

    @pytest.mark.parametrize("field", ["accepts_terms", "declares_truth", "accepts_gdpr"])
    def test_requires_every_consent(self, client, payload, field):
        assert post(client, {**payload, field: False}).status_code == 400

    def test_no_application_is_created_on_validation_error(self, client, payload):
        post(client, {**payload, "egn": "1111111111"})
        assert Application.objects.count() == 0
        assert ContractCounter.objects.count() == 0   # номерът не се хаби


class TestAntiBot:
    def test_rejects_when_turnstile_fails(self, client, payload, settings):
        settings.TURNSTILE_DISABLED = False
        from apps.apply.turnstile import TurnstileError

        with mock.patch("apps.apply.views.verify_turnstile", side_effect=TurnstileError):
            response = post(client, payload)
        assert response.status_code == 400
        assert Application.objects.count() == 0


class TestLookups:
    def test_short_query_returns_empty(self, client):
        response = client.get(reverse("apply:lookup", args=["cities"]), {"q": "В"})
        assert response.json() == []

    def test_prefix_match_ranks_first(self, client):
        response = client.get(reverse("apply:lookup", args=["universities"]), {"q": "варн"})
        labels = [row["label"] for row in response.json()]
        assert labels[0].startswith("Варненски")

    def test_unknown_kind_is_404(self, client):
        assert client.get(reverse("apply:lookup", args=["passwords"])).status_code == 404
