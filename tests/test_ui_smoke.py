"""UI smoke tests: every public page must render.

Each page is requested through Django's test client against a fresh test
database built from the project's migrations. A page passes when it answers
HTTP 200 with a page <title> naming AIM Travel. Pages that read "the latest X"
(e.g. the homepage sliders) get one placeholder record per model, created
generically from the model's field types, so the tests keep working when
fields are added or renamed.

The tests describe production as of 2026-10-07 without changing it; pages
that are already broken on https://aimtravel.bg/ are marked expectedFailure
(see KnownBrokenPagesTest) so that fixing them shows up as an unexpected pass.

Run:  python manage.py test tests
"""
import datetime
import itertools
import re
import unittest

from django.db import models
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from aimtravel_site.main_page import models as main_page_models
from aimtravel_site.posting.models import News
from aimtravel_site.web.models import Prices

TITLE_RE = re.compile(rb"<title>[^<]*AIM Travel[^<]*</title>")

_counter = itertools.count(1)


def make(model, **overrides):
    """Create one row of `model`, filling every required field with a placeholder."""
    values = {}
    for field in model._meta.concrete_fields:
        if field.name in overrides or field.primary_key or field.auto_created:
            continue
        if isinstance(field, models.FileField):  # incl. ImageField
            # Optional too: views and templates read image URLs unconditionally.
            values[field.name] = f"smoke/placeholder-{next(_counter)}.jpg"
            continue
        if field.null or field.has_default() or getattr(field, "auto_now", False) \
                or getattr(field, "auto_now_add", False):
            continue
        if isinstance(field, models.CharField) and field.blank and not field.unique:
            continue
        n = next(_counter)
        if isinstance(field, models.ForeignKey):
            value = make(field.related_model)
        elif field.choices:
            value = field.choices[0][0]
        elif isinstance(field, models.FileField):  # incl. ImageField
            value = f"smoke/placeholder-{n}.jpg"
        elif isinstance(field, models.EmailField):
            value = f"smoke{n}@example.com"
        elif isinstance(field, models.URLField):
            value = f"https://example.com/{n}"
        elif isinstance(field, models.SlugField):
            value = f"smoke-{n}"
        elif isinstance(field, (models.CharField, models.TextField)):
            value = f"Smoke {n}"[: field.max_length or None]
        elif isinstance(field, models.BooleanField):
            value = False
        elif isinstance(field, (models.IntegerField, models.FloatField, models.DecimalField)):
            value = 1
        elif isinstance(field, models.DateTimeField):
            value = timezone.now()
        elif isinstance(field, models.DateField):
            value = datetime.date.today()
        else:
            raise TypeError(f"make(): no placeholder for {model.__name__}.{field.name} ({type(field).__name__})")
        values[field.name] = value
    values.update(overrides)
    return model.objects.create(**values)


# Public pages, by URL name. Staff-only and object-detail pages are not listed:
# they redirect to login or need specific records, which is not a smoke check.
PUBLIC_PAGES = [
    "index",
    "news",
    "story",
    "taxes",
    "sign in",
    "sign up",
    "password_reset",
    "contacts",
    "wat usa",
    "online",
    "internship",
    "h2b-for-non-students",
    "offers",
    "wat 2027 registration",
    "favorite offers",
    "under-construction",
]


class SeededTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Every model the views read with .latest() (homepage, /wat_usa/, /taxes/).
        for name in ("MainSlider", "SecondSlider", "ThirdSlider", "ForthSlider",
                     "MainServicesSection", "MainPricingSection", "AboutSection",
                     "CallToActionSection", "Video"):
            make(getattr(main_page_models, name))
        make(News, news_image="smoke/news.jpg")
        make(Prices)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PublicPagesRenderTest(SeededTestCase):
    def test_public_pages_render(self):
        for name in PUBLIC_PAGES:
            with self.subTest(page=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200, f"{name} ({url})")
                self.assertRegex(response.content, TITLE_RE, f"{name} ({url}): no AIM Travel <title>")

    def test_team_page_answers(self):
        # Live /team/ currently answers 200 with an empty body; only the status is checked.
        self.assertEqual(self.client.get(reverse("team")).status_code, 200)

    def test_admin_login_renders(self):
        response = self.client.get(reverse("admin:login"))
        self.assertEqual(response.status_code, 200)

    def test_unknown_url_renders_not_found_page(self):
        # The custom handler404 (web.views.error_404) renders the site's
        # not-found page; it currently answers 200, not 404, as on the live site.
        response = self.client.get("/this-page-does-not-exist-smoke/")
        self.assertLess(response.status_code, 500)
        self.assertRegex(response.content, TITLE_RE)


class KnownBrokenPagesTest(SeededTestCase):
    """Pages that already answer HTTP 500 on https://aimtravel.bg/ (2026-10-07).

    Left unfixed on purpose: this baseline records production as it is.
    When one is fixed, its test passes "unexpectedly" — remove the decorator then.
    """

    @unittest.expectedFailure
    def test_prices_page_renders(self):
        # FieldError: the view orders by a 'price' field removed in web migration 0008.
        self.assertEqual(self.client.get(reverse("prices")).status_code, 200)

    @unittest.expectedFailure
    def test_services_page_renders(self):
        # TemplateDoesNotExist: base3.html.
        self.assertEqual(self.client.get(reverse("services")).status_code, 200)
