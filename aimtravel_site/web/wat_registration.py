"""Public interest form for the WAT 2027 roadshow."""
import json
import logging
from urllib.error import URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods


logger = logging.getLogger(__name__)


def _clean(value, limit):
    return ' '.join((value or '').split()).strip()[:limit]


def _send_to_sheet(payload):
    webhook_url = getattr(settings, 'GOOGLE_SHEETS_WEBHOOK_URL', '').strip()
    webhook_secret = getattr(settings, 'GOOGLE_SHEETS_WEBHOOK_SECRET', '').strip()
    if not webhook_url or not webhook_secret:
        return False
    payload['secret'] = webhook_secret
    request = Request(
        webhook_url,
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urlopen(request, timeout=6) as response:
            body = json.loads(response.read().decode('utf-8'))
            return 200 <= response.status < 300 and body.get('ok') is True
    except (OSError, URLError, ValueError):
        logger.exception('WAT 2027 registration sync failed')
        return False


@never_cache
@ensure_csrf_cookie
@require_http_methods(['GET', 'POST'])
def wat_2027_registration(request):
    context = {
        'values': {},
        'errors': {},
        'success': request.GET.get('success') == '1',
    }
    if request.method == 'GET':
        return render(request, 'wat_2027_registration.html', context)

    # Hidden field: bots often fill it, people never see it.
    if request.POST.get('website'):
        return redirect(f"{reverse('wat 2027 registration')}?success=1")

    values = {
        'full_name': _clean(request.POST.get('full_name'), 160),
        'phone': _clean(request.POST.get('phone'), 50),
        'course': _clean(request.POST.get('course'), 40),
        'email': _clean(request.POST.get('email'), 254),
        'university': _clean(request.POST.get('university'), 200),
        'notes': _clean(request.POST.get('notes'), 1000),
    }
    errors = {}
    if values['email']:
        try:
            validate_email(values['email'])
        except ValidationError:
            errors['email'] = 'Провери дали имейл адресът е изписан правилно.'
    if not any(values.values()):
        errors['form'] = 'Попълни поне едно поле, за да имаме информация за контакт.'
    if errors:
        return render(request, 'wat_2027_registration.html', {
            'values': values, 'errors': errors,
        }, status=400)

    payload = {
        'kind': 'wat_registration',
        'registration_id': str(uuid4()),
        'registered_at': timezone.now().isoformat(),
        **values,
        'source': 'WAT 2027 сайт',
        'page': request.build_absolute_uri(request.path),
    }
    if not _send_to_sheet(payload):
        return render(request, 'wat_2027_registration.html', {
            'values': values,
            'errors': {'form': 'В момента не успяхме да запазим данните. Опитай отново след малко.'},
        }, status=503)
    return redirect(f"{reverse('wat 2027 registration')}?success=1")
