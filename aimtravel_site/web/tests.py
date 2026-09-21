from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import City, JobOffer, OfferLead


class JobOfferFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.california_city = City.objects.create(name='San Diego', state='CA')
        cls.new_york_city = City.objects.create(name='New York', state='NY')
        JobOffer.objects.create(
            city=cls.california_city,
            employer_name='California Employer',
            job_position='Server',
            wage=16,
        )
        JobOffer.objects.create(
            city=cls.new_york_city,
            employer_name='New York Employer',
            job_position='Busser',
            wage=15,
        )

    def test_city_options_are_limited_to_selected_state(self):
        response = self.client.get(reverse('offers'), {'state': 'CA'})

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['cities'],
            [self.california_city],
        )
        self.assertContains(response, 'Всички градове в CA')
        self.assertNotContains(response, 'value="New York"')

    def test_city_options_wait_for_state_without_changing_catalogue_count(self):
        response = self.client.get(reverse('offers'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['cities']), [])
        self.assertEqual(response.context['city_count'], 2)
        self.assertContains(response, 'Първо избери щат')
        self.assertContains(response, 'name="city" data-auto-filter disabled')

    def test_city_is_cleared_when_it_does_not_match_state(self):
        response = self.client.get(
            reverse('offers'),
            {'state': 'CA', 'city': 'New York'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_city'], '')
        self.assertEqual(response.context['result_count'], 1)

    def test_employer_dropdown_is_not_rendered_or_applied(self):
        response = self.client.get(
            reverse('offers'),
            {'employer': 'California Employer'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result_count'], 2)
        self.assertNotContains(response, 'name="employer"')

    def test_free_text_search_does_not_filter_by_employer(self):
        response = self.client.get(reverse('offers'), {'q': 'California Employer'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result_count'], 0)
        self.assertContains(response, 'placeholder="Позиция или град"')

    def test_mobile_offer_controls_are_rendered(self):
        response = self.client.get(reverse('offers'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-mobile-filter-open')
        self.assertContains(response, 'data-mobile-sort')
        self.assertContains(response, 'mobile-filter-footer')
        self.assertContains(response, 'Промените се прилагат автоматично')


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class JobOfferDetailFunnelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(name='Greenville Test', state='ME')
        cls.offer = JobOffer.objects.create(
            city=cls.city,
            employer_name='Dockside Test',
            job_position='Server',
            wage=13.80,
            sponsor='CHI',
            assignment=True,
            availability_status='available',
        )

    def test_public_detail_hides_operational_availability(self):
        response = self.client.get(reverse('details offer', kwargs={'pk': self.offer.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Реална наличност')
        self.assertNotContains(response, 'Assignment')
        self.assertContains(response, 'Безплатна консултация')

    def test_staff_detail_shows_operational_availability(self):
        user = get_user_model().objects.create_user(
            email='consultant@aimtravel.bg', password='test-pass', is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse('details offer', kwargs={'pk': self.offer.pk}))

        self.assertContains(response, 'Реална наличност')
        self.assertContains(response, 'Свободна')
        self.assertContains(response, 'Assignment')

    def test_consultation_creates_lead_and_tracks_offer(self):
        response = self.client.post(reverse('offer lead'), {
            'offer_id': self.offer.pk,
            'intent': 'consultation',
            'first_name': 'Test',
            'last_name': 'Student',
            'email': 'student@aimtravel.bg',
            'phone': '0888123456',
            'university': 'СУ',
            'course': '2 курс',
            'specialty': 'Икономика',
            'privacy_consent': '1',
        })

        self.assertEqual(response.status_code, 200)
        lead = OfferLead.objects.get(email='student@aimtravel.bg')
        self.assertTrue(lead.favorite_offers.filter(pk=self.offer.pk).exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Заявка за безплатна консултация', mail.outbox[0].subject)

# Create your tests here.
