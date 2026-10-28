import json
from io import BytesIO, StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import override_settings

from aimtravel_site.apply.models import Application
from aimtravel_site.apply.sheets_sync import registration_values, sync_registration
from .test_apply_form import ApplicationFormTest


@override_settings(ONLINE_REGISTRATION_WEBHOOK_URL="https://script.google.com/macros/s/test/exec",
                   ONLINE_REGISTRATION_WEBHOOK_SECRET="test-only-secret")
class RegistrationSheetsTest(ApplicationFormTest):
    def setUp(self):
        super().setUp()
        self.auto_sync = patch("aimtravel_site.apply.sheets_sync.sync_registration", return_value=False)
        self.auto_sync.start()
        self.addCleanup(self.auto_sync.stop)
        self.submit(save_exchange=True, fee_adjustment_eur=80)
        self.application = Application.objects.get()
        self.auto_sync.stop()

    def test_export_uses_agreed_price_and_excludes_identity_numbers(self):
        values = registration_values(self.application)
        self.assertEqual(len(values), 20)
        self.assertEqual(values[7:14], [1699, 80, 1619, "Да", 249, 481, 1868])
        self.assertNotIn(self.application.egn, values)
        self.assertNotIn(self.application.id_card_number, values)
        self.assertNotIn("token=", values[14])
        self.assertEqual(values[15:17], ["Изпратен", "Изпратено"])

    @patch("aimtravel_site.apply.sheets_sync.urlopen")
    def test_acknowledged_export_and_repeat_keep_same_identifier(self, opener):
        identifier = str(self.application.public_id)
        opener.return_value.__enter__.side_effect = lambda: BytesIO(json.dumps({"ok": True, "registrationId": identifier}).encode())
        self.assertTrue(sync_registration(self.application))
        self.assertTrue(sync_registration(self.application))
        self.application.refresh_from_db()
        self.assertIsNotNone(self.application.sheets_synced_at)
        self.assertEqual(self.application.sheets_sync_error, "")
        for call in opener.call_args_list:
            payload = json.loads(call.args[0].data)
            self.assertEqual(payload["registrationId"], identifier)
            self.assertEqual(payload["action"], "online_registration")

    @patch("aimtravel_site.apply.sheets_sync.urlopen", side_effect=TimeoutError)
    def test_failure_is_retained_for_retry_without_losing_registration(self, opener):
        self.assertFalse(sync_registration(self.application))
        self.application.refresh_from_db()
        self.assertIsNone(self.application.sheets_synced_at)
        self.assertTrue(self.application.sheets_sync_error)
        with patch("aimtravel_site.apply.management.commands.sync_online_registrations.sync_registration", return_value=True) as retry:
            call_command("sync_online_registrations", stdout=StringIO())
            self.assertEqual(retry.call_count, 1)

    @patch("aimtravel_site.apply.sheets_sync.urlopen")
    def test_wrong_acknowledgement_does_not_mark_as_synchronized(self, opener):
        opener.return_value.__enter__.return_value = BytesIO(b'{"ok":true}')
        self.assertFalse(sync_registration(self.application))
        self.application.refresh_from_db()
        self.assertIsNone(self.application.sheets_synced_at)
