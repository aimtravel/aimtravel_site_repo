import csv
import io
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from .models import City, JobOffer, OfferLead


class FavoriteOffersTests(TestCase):
    def setUp(self):
        self.city = City.objects.create(name='Ocean City', state='MD')
        self.offer = JobOffer.objects.create(
            employer_name='Safe Employer', city=self.city,
            job_position='Server', wage=15.5, housing='100', tips='Да',
        )
        self.other_offer = JobOffer.objects.create(
            employer_name='Other Employer', city=self.city,
            job_position='Cashier', wage=12, housing='Не', tips='Не',
        )
        self.lead = OfferLead.objects.create(
            first_name='Test', last_name='Student', email='test@example.com',
            phone='0888000000', university='Test University', course='2',
            specialty='Tourism', privacy_consent=True,
        )
        self.other_lead = OfferLead.objects.create(
            first_name='Other', last_name='Student', email='other@example.com',
            phone='0888111111', privacy_consent=True,
        )
        self.lead.favorite_offers.add(self.offer)
        self.other_lead.favorite_offers.add(self.other_offer)

    def _post(self, name, lead=None, **data):
        if lead is not None:
            data['lead_token'] = str(lead.public_id)
        return self.client.post(reverse(name), data)

    def test_list_uses_bearer_token_without_exposing_student_data(self):
        response = self._post('favorite offers', self.lead)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual([item['id'] for item in body['offers']], [str(self.offer.pk)])
        serialized = response.content.decode()
        self.assertNotIn(self.lead.email, serialized)
        self.assertNotIn(self.lead.phone, serialized)

    def test_invalid_token_is_a_generic_not_found(self):
        response = self._post('favorite offers', lead_token='not-a-uuid')
        self.assertEqual(response.status_code, 404)
        self.assertNotIn('UUID', response.content.decode())

    def test_offer_interest_rejects_malformed_profile_token(self):
        response = self.client.post(reverse('offer lead'), {
            'offer_id': self.offer.pk, 'lead_token': 'not-a-uuid',
        })
        self.assertEqual(response.status_code, 404)

    def test_known_email_cannot_reveal_an_existing_profile_token(self):
        response = self.client.post(reverse('offer lead'), {
            'offer_id': self.offer.pk,
            'first_name': 'Attacker',
            'last_name': 'Attempt',
            'email': self.lead.email,
            'phone': '0999999999',
            'privacy_consent': '1',
        })
        self.assertEqual(response.status_code, 409)
        self.assertNotIn('lead_token', response.json())
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.phone, '0888000000')
        self.assertEqual(self.lead.first_name, 'Test')

    def test_remove_changes_only_the_authorized_list(self):
        self.other_lead.favorite_offers.add(self.offer)
        response = self._post('remove favorite', self.lead, offer_id=str(self.offer.pk))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.lead.favorite_offers.filter(pk=self.offer.pk).exists())
        self.assertTrue(self.other_lead.favorite_offers.filter(pk=self.offer.pk).exists())

    def test_remove_rejects_oversized_identifier(self):
        response = self._post('remove favorite', self.lead, offer_id='9' * 80)
        self.assertEqual(response.status_code, 400)

    @patch('aimtravel_site.web.favorites.sync_offer_lead_to_sheet')
    @patch('aimtravel_site.web.favorites.send_mail')
    def test_inquiry_saves_message_and_notifies_staff(self, send_mail_mock, sync_mock):
        response = self._post(
            'favorite inquiry', self.lead,
            message='Коя от избраните оферти е най-подходяща за мен?',
        )
        self.assertEqual(response.status_code, 200)
        self.lead.refresh_from_db()
        self.assertIn('Коя от избраните оферти', self.lead.inquiry_message)
        send_mail_mock.assert_called_once()
        sync_mock.assert_called_once()

    def test_inquiry_requires_a_message_and_favorite_offer(self):
        response = self._post('favorite inquiry', self.lead, message=' ')
        self.assertEqual(response.status_code, 400)
        self.lead.favorite_offers.clear()
        response = self._post('favorite inquiry', self.lead, message='Имам въпрос')
        self.assertEqual(response.status_code, 400)

    def test_inquiry_rejects_an_oversized_message(self):
        response = self._post('favorite inquiry', self.lead, message='а' * 1001)
        self.assertEqual(response.status_code, 400)

    def test_logged_in_account_ignores_token_from_shared_browser(self):
        user = get_user_model().objects.create_user(
            email=self.other_lead.email, password='secret-pass',
        )
        self.client.force_login(user)
        response = self._post('favorite offers', self.lead)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item['id'] for item in response.json()['offers']],
            [str(self.other_offer.pk)],
        )

    def test_export_requires_staff_permission_and_escapes_formulas(self):
        self.lead.first_name = '=HYPERLINK("https://invalid.example")'
        self.lead.save(update_fields=['first_name'])
        user = get_user_model().objects.create_user(
            email='employee@example.com', password='secret-pass',
            is_staff=True,
        )
        user.user_permissions.add(Permission.objects.get(codename='view_offerlead'))
        self.client.force_login(user)
        response = self.client.get(reverse('export favorites'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment; filename="aim-favorites.csv"', response['Content-Disposition'])
        rows = list(csv.reader(io.StringIO(response.content.decode('utf-8-sig'))))
        self.assertEqual(rows[0][0], 'ID студент')
        exported_name = next(row[1] for row in rows if row[0] == str(self.lead.pk))
        self.assertTrue(exported_name.startswith("'="))
