"""Isolated verification. Uses in-memory email; never contacts SMTP."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / '.form-testdeps'))
from django.conf import settings
TEMP = tempfile.TemporaryDirectory(dir=ROOT, ignore_cleanup_errors=True)
settings.configure(SECRET_KEY='isolated-contact-tests', BASE_DIR=TEMP.name,
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='website@example.com', ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['testserver'], MIDDLEWARE=['django.middleware.csrf.CsrfViewMiddleware'])
import django
django.setup()
spec = importlib.util.spec_from_file_location('contact_inquiry', ROOT.parent / 'aimtravel_site/web/contact_inquiry.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
from django.urls import path
urlpatterns = [path('captcha/', module.contact_captcha), path('submit/', module.contact_inquiry)]
from django.test import Client
from django.core import mail, signing


class ContactTests(unittest.TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        mail.outbox = []

    def challenge(self, client=None):
        client = client or self.client
        # Predetermined test fixture; no live CAPTCHA is read or solved.
        with patch.object(module, '_new_answer', return_value='AAAAAA'):
            response = client.get('/captcha/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['image'].startswith('data:image/png;base64,'))
        self.assertIn('no-store', response['Cache-Control'])
        return response.json()['token']

    def post(self, token='', answer='AAAAAA', client=None, **changes):
        client = client or self.client
        payload = {'captcha_token':token, 'captcha_answer':answer, 'name':'Test Fixture',
            'phone-field':'0881234567', 'email-field':'test@example.com', 'message':'Test message'}
        payload.update(changes)
        return client.post('/submit/', payload,
            HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)

    def test_missing_wrong_and_replayed(self):
        token = self.challenge()
        self.assertEqual(self.post().status_code,400)
        self.assertEqual(self.post(token,'BBBBBB').status_code,400)
        self.assertEqual(self.post(token).status_code,400)
        self.assertEqual(len(mail.outbox),0)

    def test_valid_then_replayed(self):
        token = self.challenge()
        self.assertEqual(self.post(token).status_code,200)
        self.assertEqual(len(mail.outbox),1)
        self.assertEqual(mail.outbox[0].to,['studentski@aimtravel.bg'])
        self.assertEqual(mail.outbox[0].reply_to,['test@example.com'])
        self.assertEqual(self.post(token).status_code,400)
        self.assertEqual(len(mail.outbox),1)

    def test_tampering_expiry_cross_cookie(self):
        token = self.challenge()
        self.assertEqual(self.post(token+'x').status_code,400)
        with patch('django.core.signing.time.time',return_value=2000000000):
            self.assertEqual(self.post(token).status_code,400)
        other=Client(enforce_csrf_checks=True)
        self.challenge(other)
        self.assertEqual(self.post(token,client=other).status_code,400)
        self.assertEqual(len(mail.outbox),0)

    def test_csrf_and_honeypot(self):
        token=self.challenge()
        self.assertEqual(self.client.post('/submit/',{}).status_code,403)
        self.assertEqual(self.post(token,website='bot.example').status_code,400)
        self.assertEqual(len(mail.outbox),0)

    def test_invalid_email_and_mail_failure(self):
        self.assertEqual(self.post(self.challenge(),**{'email-field':'invalid'}).status_code,400)
        with patch.object(module.EmailMessage,'send',side_effect=OSError):
            self.assertEqual(self.post(self.challenge()).status_code,503)
        self.assertEqual(len(mail.outbox),0)

    def test_separate_users(self):
        other=Client(enforce_csrf_checks=True)
        first=self.challenge(); second=self.challenge(other)
        self.assertEqual(self.post(first).status_code,200)
        self.assertEqual(self.post(second,client=other).status_code,200)
        self.assertEqual(len(mail.outbox),2)


if __name__=='__main__':
    unittest.main()

