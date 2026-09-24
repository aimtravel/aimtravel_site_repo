import re

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from aimtravel_site.user_auth.models import AppUser
from aimtravel_site.web.models import OfferLead


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class UnifiedLoginTests(TestCase):
    def test_person_can_create_profile_with_only_email_and_phone(self):
        response = self.client.post(reverse('sign in'), {
            'action': 'person_start',
            'email': 'student@example.com',
            'phone': '0888 123 456',
            'privacy_consent': 'on',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Въведи 6-цифрения код')
        self.assertEqual(len(mail.outbox), 1)
        code = re.search(r'\b(\d{6})\b', mail.outbox[0].body).group(1)

        response = self.client.post(reverse('sign in'), {
            'action': 'person_verify',
            'code': code,
        })

        self.assertRedirects(response, reverse('student portal'))
        user = AppUser.objects.get(email='student@example.com')
        lead = OfferLead.objects.get(email='student@example.com')
        self.assertEqual(user.phone, '0888123456')
        self.assertFalse(user.has_usable_password())
        self.assertEqual(lead.phone, '0888123456')
        self.assertEqual(lead.user, user)
        self.assertEqual(lead.lifecycle_stage, 'lead')

    def test_wrong_code_does_not_create_account(self):
        self.client.post(reverse('sign in'), {
            'action': 'person_start',
            'email': 'student@example.com',
            'phone': '0888123456',
            'privacy_consent': 'on',
        })
        response = self.client.post(reverse('sign in'), {
            'action': 'person_verify', 'code': '000000',
        })
        self.assertContains(response, 'Кодът не е правилен')
        self.assertFalse(AppUser.objects.filter(email='student@example.com').exists())

    def test_person_cannot_use_consultant_login(self):
        AppUser.objects.create_user(email='person@example.com', password='Test-pass-194!')
        response = self.client.post(reverse('sign in'), {
            'action': 'consultant_login',
            'username': 'person@example.com',
            'password': 'Test-pass-194!',
        })
        self.assertContains(response, 'само за консултанти')

    def test_staff_can_use_consultant_login(self):
        user = AppUser.objects.create_user(
            email='consultant@aimtravel.bg', password='Test-pass-194!', is_staff=True,
        )
        response = self.client.post(reverse('sign in'), {
            'action': 'consultant_login',
            'username': user.email,
            'password': 'Test-pass-194!',
        })
        self.assertRedirects(response, reverse('my-profile', kwargs={'slug': user.slug}))
