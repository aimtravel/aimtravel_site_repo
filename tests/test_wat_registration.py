import io
import json
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from aimtravel_site.web import wat_registration as registration


@override_settings(GOOGLE_SHEETS_WEBHOOK_URL='https://script.google.com/macros/s/test/exec',
                   GOOGLE_SHEETS_WEBHOOK_SECRET='test-only-secret', ALLOWED_HOSTS=['testserver'])
class TabletRegistrationDeliveryTest(SimpleTestCase):
    def payload(self):
        return {'registration_id': '8dbd0402-3e11-4b92-b203-81a802cd1677',
                'full_name': 'TEST ONLY', 'email': 'test@example.com', 'kind': 'wat_registration'}

    @patch.object(registration.time, 'sleep')
    @patch.object(registration, 'urlopen')
    def test_busy_is_retried_with_same_identifier_and_no_payload_mutation(self, opener, sleep):
        # Real urllib responses include a numeric status.
        responses = [io.BytesIO(b'{"ok":false,"error":"busy"}'), io.BytesIO(b'{"ok":true}')]
        for response in responses:
            response.status = 200
        opener.side_effect = responses
        payload = self.payload()
        self.assertTrue(registration._send_to_sheet(payload))
        self.assertNotIn('secret', payload)
        sleep.assert_called_once_with(0.5)
        for call in opener.call_args_list:
            self.assertEqual(call.kwargs['timeout'], 45)
            self.assertEqual(json.loads(call.args[0].data)['registration_id'], payload['registration_id'])

    @patch.object(registration.time, 'sleep')
    @patch.object(registration, 'urlopen')
    def test_persistent_busy_stops_after_three_attempts(self, opener, sleep):
        def busy(*args, **kwargs):
            response = io.BytesIO(b'{"ok":false,"error":"busy"}')
            response.status = 200
            return response
        opener.side_effect = busy
        self.assertFalse(registration._send_to_sheet(self.payload()))
        self.assertEqual(opener.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    @patch.object(registration, 'urlopen', side_effect=TimeoutError('private transport detail'))
    def test_unknown_result_is_not_blindly_retried_or_logged_with_contact_data(self, opener):
        payload = self.payload()
        with self.assertLogs(registration.logger, level='WARNING') as logs:
            self.assertFalse(registration._send_to_sheet(payload))
        self.assertEqual(opener.call_count, 1)
        text = ' '.join(logs.output)
        self.assertIn(payload['registration_id'], text)
        for value in [payload['email'], payload['full_name'], 'test-only-secret', 'private transport detail']:
            self.assertNotIn(value, text)

    @patch.object(registration, '_send_to_sheet', return_value=False)
    @patch.object(registration, 'render', return_value=HttpResponse(status=503))
    def test_failed_delivery_keeps_values_and_identifier_for_retry(self, render, send):
        payload = self.payload()
        request = RequestFactory().post('/wat-2027/registracia/', payload)
        response = registration.wat_2027_registration(request)
        self.assertEqual(response.status_code, 503)
        context = render.call_args.args[2]
        self.assertEqual(context['values']['email'], payload['email'])
        self.assertEqual(context['registration_id'], payload['registration_id'])
        self.assertIn(payload['registration_id'], context['errors']['form'])
