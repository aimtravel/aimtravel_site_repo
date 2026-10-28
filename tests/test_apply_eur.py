from datetime import timedelta
from io import BytesIO
from unittest.mock import patch

from django.core import mail
from django.utils import timezone
from pypdf import PdfReader
from rest_framework.exceptions import ValidationError

from aimtravel_site.apply.models import Application, DiscountCode
from aimtravel_site.apply.pricing import quote
from aimtravel_site.apply.contracts import amount_words
from .test_apply_form import ApplicationFormTest


class EuroRegistrationTest(ApplicationFormTest):
    def test_numeric_adjustment_updates_contract_and_annex(self):
        response = self.submit(fee_adjustment_eur=80, save_exchange=True)
        self.assertEqual(response.status_code, 201, response.content)
        app = Application.objects.get()
        self.assertEqual((app.price_eur, app.discount_eur, app.discount_code), (1619, 80, ''))
        for name, content, mime in mail.outbox[0].attachments[:2]:
            text = ''.join(page.extract_text() for page in PdfReader(BytesIO(content)).pages)
            self.assertIn('1619', text)
        self.assertIn('481 евро', mail.outbox[0].body)

    def test_numeric_adjustment_rejects_invalid_values(self):
        for amount in [-10, 15, 700, 'AIM80']:
            with self.subTest(amount=amount):
                self.assertEqual(self.submit(fee_adjustment_eur=amount).status_code, 400)
        self.assertFalse(Application.objects.exists())

    def test_full_discount_and_annex_have_same_amount(self):
        DiscountCode.objects.create(code='AIM80', amount_eur=80, max_uses=1)
        response = self.submit(discount_code='aim80', save_exchange=True)
        self.assertEqual(response.status_code, 201, response.content)
        app = Application.objects.get()
        self.assertEqual((app.base_price_eur, app.price_eur, app.discount_eur), (1699,1619,80))
        self.assertEqual(DiscountCode.objects.get().used_count, 1)
        self.assertEqual(len(mail.outbox[0].attachments), 3)
        for name, content, mime in mail.outbox[0].attachments[:2]:
            self.assertEqual(mime, 'application/pdf')
            text = ''.join(page.extract_text() for page in PdfReader(BytesIO(content)).pages)
            self.assertIn('1619', text)
            self.assertIn('хиляда шестстотин и деветнадесет', text)
            self.assertNotIn('{{', text)
        self.assertIn('481 евро', mail.outbox[0].body)
        self.assertIn('7 календарни дни', mail.outbox[0].body)
        self.assertTrue(response.json()['annex_pdf_url'])

    def test_self_has_own_clauses_and_annex_reference(self):
        response=self.submit(program_option='self_arranged', save_exchange=True)
        self.assertEqual(response.status_code,201,response.content)
        app=Application.objects.get()
        self.assertEqual(app.price_eur,1499)
        text=''.join(p.extract_text() for p in PdfReader(app.contract_document.annex_pdf.path).pages)
        self.assertIn('чл. 18',text)
        self.assertIn('1499',text)
        self.assertIn('SELF ARRANGED',''.join(p.extract_text() for p in PdfReader(app.contract_document.pdf.path).pages))

    def test_latin_names_rejected(self):
        response=self.submit(first_name='IVAN')
        self.assertEqual(response.status_code,400)
        self.assertFalse(Application.objects.exists())

    def test_invalid_discount_is_not_ignored(self):
        response=self.submit(discount_code='AIM9999')
        self.assertEqual(response.status_code,400)
        self.assertFalse(Application.objects.exists())

    def test_price_tampering_ignored(self):
        response=self.submit(price_eur=1,discount_eur=1698)
        self.assertEqual(response.status_code,201,response.content)
        self.assertEqual(Application.objects.get().price_eur,1699)
        self.assertIn('232 евро',mail.outbox[0].body)
        self.assertEqual(len(mail.outbox[0].attachments),2)
        self.assertIsNone(response.json()['annex_pdf_url'])

    def test_expired_and_exhausted_codes(self):
        code=DiscountCode.objects.create(code='AIM20',amount_eur=20,max_uses=1,
                                          expires_at=timezone.now()-timedelta(seconds=1))
        with self.assertRaises(ValidationError):quote('full_arranged',False,'AIM20')
        code.expires_at=None;code.used_count=1;code.save()
        with self.assertRaises(ValidationError):quote('self_arranged',True,'AIM20')

    def test_email_failure_is_reported_honestly(self):
        with patch('aimtravel_site.apply.emails.EmailMultiAlternatives.send',side_effect=OSError):
            response=self.submit()
        self.assertEqual(response.status_code,201,response.content)
        self.assertFalse(response.json()['email_sent'])
        self.assertIsNone(Application.objects.get().contract_document.email_sent_at)

    def test_amount_words(self):
        self.assertEqual(amount_words(1699),'хиляда шестстотин деветдесет и девет')
        self.assertEqual(amount_words(1499),'хиляда четиристотин деветдесет и девет')
        self.assertEqual(amount_words(819),'осемстотин и деветнадесет')
