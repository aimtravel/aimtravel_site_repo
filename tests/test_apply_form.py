"""The application form (/zapisvane-za-brigada/) end to end, without a browser.

A made-up applicant submits through the JSON API; the real season contract
template is filled in, the contract is stored outside the public MEDIA_ROOT,
the email goes to the applicant with a hidden copy to their office, and the
signed download link works while a forged one does not.

LibreOffice is not needed: without it the contract is shipped as .docx.

Run:  python manage.py test tests
"""
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from aimtravel_site.apply.models import Application
from aimtravel_site.apply.validators import upcoming_season


def applicant(**overrides):
    values = {
        "email": "test.applicant@example.com",
        "first_name": "ИВАН",
        "middle_name": "ПЕТРОВ",
        "last_name": "ТЕСТОВ",
        "phone": "+359 888 000 000",
        "egn": "0506140008",
        "save_exchange": False,
        "id_card_number": "000000000",
        "place_of_birth": "Варна",
        "university": "Икономически университет — Варна",
        "major": "Информатика",
        "year_of_study": "2",
        "program_option": "full_arranged",
        "season": upcoming_season(),
        "office": "varna",
        "accepts_terms": True,
        "declares_truth": True,
        "accepts_gdpr": True,
        "turnstile_token": "",
    }
    values.update(overrides)
    return values


class ApplicationFormTest(TestCase):
    def setUp(self):
        self.private_root = tempfile.mkdtemp(prefix="apply-private-")
        self.media_root = tempfile.mkdtemp(prefix="apply-media-")
        self.addCleanup(shutil.rmtree, self.private_root, ignore_errors=True)
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)
        overrides = override_settings(
            APPLY_PRIVATE_ROOT=self.private_root,
            MEDIA_ROOT=self.media_root,
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
            AIM_CONTRACT_EMAIL_BCC=["office-copy@example.com"],
            SITE_URL="https://aimtravel.bg",
        )
        overrides.enable()
        self.addCleanup(overrides.disable)

    def submit(self, **overrides):
        # The email is sent once the database transaction commits.
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(reverse("apply:application-create"), applicant(**overrides),
                                    content_type="application/json")

    def test_page_renders(self):
        response = self.client.get(reverse("apply-zapisvane"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AIM Travel")

    def test_turnstile_is_off_without_keys(self):
        # Production has no keys yet: the form must still work, and must say so.
        self.assertTrue(settings.TURNSTILE_DISABLED)

    def test_submission_issues_contract_and_emails_applicant(self):
        response = self.submit()
        self.assertEqual(response.status_code, 201, response.content)
        application = Application.objects.get()
        document = application.contract_document

        # Stored privately, never under the public MEDIA_ROOT.
        stored = Path(document.pdf.path)
        self.assertTrue(stored.is_file())
        self.assertTrue(str(stored).startswith(self.private_root), stored)
        self.assertEqual(list(Path(self.media_root).rglob("*")), [])

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["test.applicant@example.com"])
        self.assertEqual(email.bcc, ["studentski@aimtravel.bg", "office-copy@example.com"])
        self.assertIn(application.contract_number, email.subject)
        names = [name for name, _content, _mime in email.attachments]
        self.assertEqual(len(names), 2, names)
        self.assertTrue(names[0].startswith(f"Dogovor_{application.contract_number}"), names)
        self.assertEqual(names[1], "AIM_Bank_Details.pdf")
        self.assertIsNotNone(application.contract_document.email_sent_at)

        url = response.json()["contract_pdf_url"]
        self.assertTrue(url.startswith("https://aimtravel.bg/api/v1/contracts/"), url)
        download = self.client.get(url.removeprefix("https://aimtravel.bg"))
        self.assertEqual(download.status_code, 200)
        self.assertEqual(b"".join(download.streaming_content), stored.read_bytes())

        forged = url.rsplit("/", 2)[0] + "/forged-token/"
        self.assertEqual(self.client.get(forged.removeprefix("https://aimtravel.bg")).status_code, 404)

    def test_same_idempotency_key_issues_one_contract(self):
        key = {"HTTP_IDEMPOTENCY_KEY": "double-click-test"}
        first = self.client.post(reverse("apply:application-create"), applicant(),
                                 content_type="application/json", **key)
        second = self.client.post(reverse("apply:application-create"), applicant(),
                                  content_type="application/json", **key)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.json()["contract_number"], first.json()["contract_number"])
        self.assertEqual(Application.objects.count(), 1)

    def test_invalid_submission_is_rejected(self):
        response = self.submit(email="not-an-email", accepts_gdpr=False)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Application.objects.count(), 0)
        self.assertEqual(mail.outbox, [])
