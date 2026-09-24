"""Best-effort synchronization of offer leads to the staff Google Sheet."""
import json
import logging
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.conf import settings

from aimtravel_site.templatetags.custom_filters import housing_summary

from .models import OfferLead


logger = logging.getLogger(__name__)


def sync_offer_lead_to_sheet(lead_id, base_url):
    """Send the lead's current favorites without blocking database updates."""
    webhook_url = getattr(settings, 'GOOGLE_SHEETS_WEBHOOK_URL', '').strip()
    webhook_secret = getattr(settings, 'GOOGLE_SHEETS_WEBHOOK_SECRET', '').strip()
    if not webhook_url or not webhook_secret:
        return False

    lead = (
        OfferLead.objects.prefetch_related('favorite_offers__city')
        .filter(pk=lead_id)
        .first()
    )
    if not lead:
        return False

    offers = []
    for offer in lead.favorite_offers.all().order_by('pk'):
        offers.append({
            'id': offer.pk,
            'employer': offer.employer_name or '',
            'position': offer.job_position or '',
            'city': offer.city.name or '',
            'state': offer.city.state or '',
            'wage': offer.wage,
            'housing': housing_summary(offer.housing),
            'url': f'{base_url}/offer/details/{offer.pk}/',
        })

    payload = {
        'secret': webhook_secret,
        'student_id': lead.pk,
        'created_at': lead.created_at.isoformat(),
        'first_name': lead.first_name,
        'last_name': lead.last_name,
        'email': lead.email,
        'phone': lead.phone,
        'university': lead.university,
        'course': lead.course,
        'specialty': lead.specialty,
        'status': lead.get_status_display(),
        'updated_at': lead.updated_at.isoformat(),
        'offers': offers,
    }
    request = Request(
        webhook_url,
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urlopen(request, timeout=4) as response:
            body = json.loads(response.read().decode('utf-8'))
            return 200 <= response.status < 300 and body.get('ok') is True
    except (OSError, URLError, ValueError):
        logger.exception('Google Sheets lead sync failed for lead %s', lead_id)
        return False
