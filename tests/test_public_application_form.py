"""Production application form: render, CV generation and webhook delivery.

Uses fictional applicants and mocks delivery; never writes to the live Sheet.
"""
import base64
import io
import json
from unittest.mock import patch

from django.core.cache import cache
from django.test import Client, SimpleTestCase, override_settings
from docx import Document

from aimtravel_site.web import application_form_view as form


@override_settings(ALLOWED_HOSTS=["testserver"])
class PublicApplicationFormTest(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def payload(self):
        values = [""] * 31
        values[0] = "TEST APPLICATION"
        values[1] = "2005-06-14"
        values[5] = "+359888000000"
        values[6] = "test.applicant@example.com"
        values[13] = "Test University"
        values[21] = "2027-05-15"
        return {"values": values, "consent": True,
                "submissionId": "test-submission-1234567890",
                "gender": "Female", "nationality": "Bulgaria", "experiences": []}

    def submit(self, body):
        return self.client.post("/application-form/submit/", body,
                                content_type="application/json")

    def test_page_and_csrf(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get("/application-form/")
        self.assertContains(response, "Application Form")
        self.assertContains(response, "/application-form/submit/")
        self.assertIn("csrftoken", response.cookies)
        self.assertEqual(client.post("/application-form/submit/", self.payload(),
                                    content_type="application/json").status_code, 403)

    def test_cv_is_generated_from_the_shipped_template(self):
        payload = self.payload()
        document = Document(io.BytesIO(form._build_resume(
            payload["values"], [], "", "Female", "Bulgaria")))
        text = "\n".join(p.text for p in document.paragraphs)
        text += "\n" + "\n".join(c.text for c in form._iter_cells(document.tables))
        self.assertIn("TEST APPLICATION", text)
        self.assertIn("test.applicant@example.com", text)
        self.assertIn("14/06/2005", text)
        self.assertIn("15/05/2027", text)
        self.assertNotIn("[FULL NAME IN LATIN LETTERS]", text)

    @patch.object(form, "APPLICATION_FORM_WEBHOOK_URL", "https://script.google.com/macros/s/test/exec")
    @patch.object(form, "APPLICATION_FORM_WEBHOOK_SECRET", "test-only-secret")
    @patch.object(form.urllib.request, "urlopen")
    def test_submission_preserves_sheet_payload_and_cv_and_does_not_duplicate(self, outbound):
        outbound.return_value.__enter__.return_value.read.return_value = b'{"ok":true}'
        payload = self.payload()
        self.assertEqual(self.submit(payload).json(), {"ok": True})
        request = outbound.call_args.args[0]
        sent = json.loads(request.data)
        self.assertEqual(sent["values"], payload["values"])
        self.assertEqual(sent["submissionId"], payload["submissionId"])
        self.assertEqual(sent["secret"], "test-only-secret")
        self.assertEqual(sent["resumeFileName"], "TEST_APPLICATION_AIM_CV.docx")
        self.assertTrue(base64.b64decode(sent["resumeBase64"]).startswith(b"PK"))
        self.assertEqual(self.submit(payload).json(), {"ok": True})
        self.assertEqual(outbound.call_count, 1)

    @patch.object(form.urllib.request, "urlopen")
    def test_invalid_input_never_reaches_google(self, outbound):
        payload = self.payload()
        payload["consent"] = False
        self.assertEqual(self.submit(payload).status_code, 400)
        payload["consent"] = True
        payload["values"][0] = "Тест"
        self.assertEqual(self.submit(payload).status_code, 400)
        outbound.assert_not_called()

    @patch.object(form, "APPLICATION_FORM_WEBHOOK_URL", "")
    def test_unconfigured_form_reports_unavailable(self):
        self.assertEqual(self.submit(self.payload()).status_code, 503)
