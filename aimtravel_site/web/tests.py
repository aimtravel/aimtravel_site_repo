from django.test import TestCase
from django.urls import reverse

from .models import City, JobOffer


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

# Create your tests here.
