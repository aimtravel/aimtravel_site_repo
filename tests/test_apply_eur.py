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
    def test_contract_keeps_original_typography_and_compact_page_count(self):
        for option, expected_pages in [('full_arranged', 8), ('self_arranged', 8)]:
            self.submit(program_option=option, save_exchange=True)
            message = mail.outbox[-2]
            contract = PdfReader(BytesIO(message.attachments[0][1]))
            annex = PdfReader(BytesIO(message.attachments[1][1]))
            self.assertEqual(len(contract.pages), expected_pages)
            self.assertEqual(len(annex.pages), 2)
            self.assertAlmostEqual(float(contract.pages[0].mediabox.width), 595.3, places=1)
            font_names = [str(font.get_object().get('/BaseFont', '')) for page in contract.pages
                          for font in page['/Resources']['/Font'].get_object().values()]
            self.assertTrue(any('Arial' in name or 'LiberationSans' in name for name in font_names), font_names)
            self.assertFalse(any('SofiaSans' in name for name in font_names))
            for document in (contract, annex):
                for number, page in enumerate(document.pages, 1):
                    text = page.extract_text()
                    self.assertEqual(text.splitlines()[4:6], ['Подпис ………………', str(number)])
            text = ' '.join(''.join(page.extract_text() for page in contract.pages).split())
            self.assertIn('в работни дни от 09:30 до 17:30 ч.', text)
            self.assertNotIn('24 часа в денонощието', text)
            self.assertRegex(text, r'24[- ]часова телефонна линия за спешни случаи')

    def test_pdf_content_verification_rejects_missing_contract_text(self):
        from pypdf import PdfWriter
        from aimtravel_site.apply.document_pdf import validate_pdf_text
        document = BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=595, height=842)
        writer.write(document)
        document.seek(0)
        with self.assertRaisesRegex(ValueError, 'paragraph 1'):
            validate_pdf_text(['Required contractual clause'], document)

    def test_program_price_is_red_and_email_has_no_combined_total(self):
        from io import BytesIO
        from zipfile import ZipFile
        from lxml import etree
        self.submit(save_exchange=True, fee_adjustment_eur=80)
        application = Application.objects.get()
        with application.contract_document.docx.open('rb') as source:
            with ZipFile(BytesIO(source.read())) as package:
                xml = etree.fromstring(package.read('word/document.xml'))
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        red = xml.xpath('//w:r[w:rPr/w:color[@w:val="C00000"]]/w:t/text()', namespaces=ns)
        self.assertIn('1619', red)
        for name, content, mime in mail.outbox[0].attachments[:2]:
            reader = PdfReader(BytesIO(content))
            colored = []
            def visit(text, cm, tm, font, size):
                if '1619' in text:
                    colored.append(text)
            for page in reader.pages:
                page.extract_text(visitor_text=visit)
            self.assertTrue(colored, name)
            # ReportLab emits the same explicit red RGB operator in both PDFs.
            streams = b''.join(page.get_contents().get_data() for page in reader.pages)
            self.assertIn(b'.752941 0 0 rg', streams)
        for body in [mail.outbox[0].body, mail.outbox[0].alternatives[0][0]]:
            self.assertNotIn('Общо:', body)
            self.assertNotIn('1868', body)
            self.assertIn('Цена на програмата: 1619', body)
            self.assertIn('Застраховка Save Exchange: 249', body)

    def test_identity_card_accepts_latin_and_cyrillic_letters(self):
        from aimtravel_site.apply.serializers import ApplicationCreateSerializer
        from .test_apply_form import applicant
        for number in ["AB1234567", "АБ1234567", "123456789"]:
            serializer = ApplicationCreateSerializer(data=applicant(id_card_number=number))
            self.assertTrue(serializer.is_valid(), serializer.errors)
            self.assertEqual(serializer.validated_data["id_card_number"], number)
        for number in ["AB123456", "AB12345678", "AB12345!7"]:
            serializer = ApplicationCreateSerializer(data=applicant(id_card_number=number))
            self.assertFalse(serializer.is_valid())
            self.assertIn("id_card_number", serializer.errors)

    def test_passport_deadline_follows_program_season(self):
        self.assertEqual(Application(season=2027).passport_valid_until, "30.04.2028")
        self.assertEqual(Application(season=2028).passport_valid_until, "30.04.2029")

    def test_dated_contract_and_annex_use_same_sofia_date(self):
        from datetime import datetime, timezone as dt_timezone
        app = Application(currency="EUR", created_at=datetime(2026, 10, 28, 22, 30, tzinfo=dt_timezone.utc))
        self.assertEqual(app.contract_date, "29.10.2026")
        self.submit(save_exchange=True, id_card_number="АБ1234567")
        app = Application.objects.get()
        self.assertIn(app.contract_reference, mail.outbox[0].subject)
        self.assertIn("30.04.2028", mail.outbox[0].body)
        for name, content, mime in mail.outbox[0].attachments[:2]:
            text = ''.join(page.extract_text() for page in PdfReader(BytesIO(content)).pages)
            self.assertIn(f"Договор от {app.contract_date} г.", text)
            self.assertNotIn(app.contract_number, text)
            self.assertIn("АБ1234567", text)
            self.assertIn(app.contract_date, name)

    def test_staff_notification_and_retry_are_independent(self):
        from aimtravel_site.apply.tasks import send_contract_email_task
        self.submit(save_exchange=True)
        app = Application.objects.get()
        student_email = mail.outbox[0]
        self.assertEqual(student_email.recipients(), [app.email])
        self.assertEqual(student_email.cc, [])
        self.assertEqual(student_email.bcc, [])
        self.assertEqual(student_email.reply_to, ['studentski@aimtravel.bg'])
        notification = mail.outbox[1]
        self.assertEqual(notification.recipients(), ['studentski@aimtravel.bg'])
        self.assertEqual(notification.attachments, [])
        self.assertTrue(notification.subject.startswith('Нов записан участник онлайн'))
        self.assertIn(app.full_name_latin, notification.body)
        self.assertIn('481 евро', notification.body)
        self.assertEqual(notification.reply_to, [app.email])
        send_contract_email_task(app.pk, app.contract_document.pk)
        self.assertEqual(len(mail.outbox), 2)

    def test_staff_is_notified_if_applicant_delivery_fails(self):
        from aimtravel_site.apply.emails import _deliver_email
        def deliver(message):
            if message.to == ['test.applicant@example.com']:
                raise OSError('simulated applicant delivery failure')
            return _deliver_email(message)
        with patch('aimtravel_site.apply.emails._deliver_email', side_effect=deliver):
            response = self.submit()
        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.json()['email_sent'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['studentski@aimtravel.bg'])
        self.assertIn('ВНИМАНИЕ', mail.outbox[0].body)

    def test_staff_delivery_failure_does_not_resend_applicant(self):
        from aimtravel_site.apply.tasks import send_contract_email_task
        with patch('aimtravel_site.apply.emails.send_staff_registration_notification', side_effect=OSError):
            response = self.submit()
        app = Application.objects.get()
        self.assertIsNotNone(app.contract_document.email_sent_at)
        self.assertIsNone(app.contract_document.staff_notified_at)
        send_contract_email_task(app.pk, app.contract_document.pk)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIsNotNone(app.contract_document.__class__.objects.get(pk=app.contract_document.pk).staff_notified_at)

    def test_numeric_adjustment_updates_contract_and_annex(self):
        response = self.submit(fee_adjustment_eur=80, save_exchange=True)
        self.assertEqual(response.status_code, 201, response.content)
        app = Application.objects.get()
        self.assertEqual((app.price_eur, app.discount_eur, app.discount_code), (1619, 80, ''))
        for name, content, mime in mail.outbox[0].attachments[:2]:
            text = ''.join(page.extract_text() for page in PdfReader(BytesIO(content)).pages)
            self.assertIn('1619', text)
        self.assertIn('481 евро', mail.outbox[0].body)
        html = mail.outbox[0].alternatives[0][0]
        for value in ['BG60UNCR70001523205219', 'до 7 дни',
                      'href="https://aimtravel.bg/application-form/"',
                      'viber://chat?number=%2B359889966583',
                      'https://www.instagram.com/aimtravel_usa/',
                      'https://www.facebook.com/profile.php?id=100072235954652',
                      'Цена на програмата: 1619 евро', 'Застраховка Save Exchange: 249 евро']:
            self.assertIn(value, html)

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
            self.assertIn('хиляда шестстотин и деветнадесет', ' '.join(text.split()))
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
