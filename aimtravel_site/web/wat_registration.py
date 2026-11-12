"""Public interest form for the WAT 2027 roadshow."""
import json
import logging
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import UUID, uuid4

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods


logger = logging.getLogger(__name__)

PRIORITY_UNIVERSITIES = (
    'УНСС – Университет за национално и световно стопанство',
    'НБУ – Нов български университет',
    'ТУ-София – Технически университет – София',
    'НСА – Национална спортна академия „Васил Левски“',
    'СУ – Софийски университет „Св. Климент Охридски“',
    'УАСГ (ВИАС) – Университет по архитектура, строителство и геодезия',
)

OTHER_SOFIA_UNIVERSITIES = (
    'Академия на МВР – София',
    'Висше строително училище „Любен Каравелов“ – София',
    'Висше транспортно училище „Тодор Каблешков“ – София',
    'Висше училище по телекомуникации и пощи – София',
    'Военна академия „Георги Стойков Раковски“ – София',
    'Лесотехнически университет – София',
    'Медицински университет – София',
    'Минно-геоложки университет „Св. Иван Рилски“ – София',
    'НАТФИЗ „Кръстьо Сарафов“ – София',
    'Национална музикална академия „Проф. Панчо Владигеров“ – София',
    'Национална художествена академия – София',
    'Театрален колеж „Любен Гройс“ – София',
    'УниБИТ – Университет по библиотекознание и информационни технологии',
    'Университет по застраховане и финанси – София',
    'ХТМУ – Химикотехнологичен и металургичен университет',
)


def _form_context(**extra):
    return {
        'priority_universities': PRIORITY_UNIVERSITIES,
        'other_universities': OTHER_SOFIA_UNIVERSITIES,
        **extra,
    }


def _clean(value, limit):
    return ' '.join((value or '').split()).strip()[:limit]


def _registration_id(value):
    try:
        return str(UUID(str(value)))
    except (TypeError, ValueError, AttributeError):
        return str(uuid4())


def _send_to_sheet(payload):
    webhook_url = getattr(settings, 'GOOGLE_SHEETS_WEBHOOK_URL', '').strip()
    webhook_secret = getattr(settings, 'GOOGLE_SHEETS_WEBHOOK_SECRET', '').strip()
    if not webhook_url or not webhook_secret:
        return False
    outbound = {**payload, 'secret': webhook_secret}
    request = Request(
        webhook_url,
        data=json.dumps(outbound, ensure_ascii=False).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    reference = payload.get('registration_id', '')
    # Retry only an explicit busy acknowledgement. Unknown delivery outcomes
    # retain the same ID for a later retry; the receiver deduplicates that ID.
    for attempt in range(3):
        try:
            with urlopen(request, timeout=45) as response:
                body = json.loads(response.read(4096).decode('utf-8'))
                if 200 <= response.status < 300 and isinstance(body, dict):
                    if body.get('ok') is True:
                        return True
                    if body.get('error') == 'busy' and attempt < 2:
                        time.sleep(0.5)
                        continue
                logger.warning('WAT registration delivery not acknowledged reference=%s', reference)
                return False
        except HTTPError as error:
            logger.warning('WAT registration HTTP failure reference=%s status=%s', reference, error.code)
            return False
        except (OSError, URLError, ValueError) as error:
            logger.warning('WAT registration transport failure reference=%s type=%s', reference, type(error).__name__)
            return False
    return False


@never_cache
@ensure_csrf_cookie
@require_http_methods(['GET', 'POST'])
def wat_2027_registration(request):
    context = _form_context(**{
        'values': {},
        'errors': {},
        'success': request.GET.get('success') == '1',
        'registration_id': str(uuid4()),
    })
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
        'specialty': _clean(request.POST.get('specialty'), 200),
        'notes': _clean(request.POST.get('notes'), 1000),
    }
    payload = {
        'kind': 'wat_registration',
        'registration_id': _registration_id(request.POST.get('registration_id')),
        'registered_at': timezone.now().isoformat(),
        **values,
        'source': 'WAT 2027 сайт',
        'page': request.build_absolute_uri(request.path),
    }
    if not _send_to_sheet(payload):
        return render(request, 'wat_2027_registration.html', _form_context(**{
            'values': values,
            'errors': {'form': 'Не получихме потвърждение от таблицата. Данните са запазени във формата. Изчакай малко и натисни отново „Изпрати регистрацията“. Код: ' + payload['registration_id']},
            'registration_id': payload['registration_id'],
        }), status=503)
    return redirect(f"{reverse('wat 2027 registration')}?success=1")
