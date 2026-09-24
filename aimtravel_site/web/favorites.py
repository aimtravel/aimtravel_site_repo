"""Favorite offers using the existing OfferLead storage."""
import csv
import io
from uuid import UUID

from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST

from .models import OfferLead
from aimtravel_site.templatetags.custom_filters import housing_summary


def _lead(request):
    # A logged-in account always owns its own list, even on a shared browser.
    if request.user.is_authenticated:
        if request.user.is_staff:
            return None
        email = (request.user.email or '').strip()
        if not email:
            return None
        return OfferLead.objects.filter(email__iexact=email).first()
    token = request.POST.get('lead_token', '')
    if not token:
        return None
    try:
        token = UUID(token)
    except (ValueError, TypeError, AttributeError):
        return None
    return OfferLead.objects.filter(public_id=token).first()


def _offers(lead):
    return lead.favorite_offers.select_related('city').order_by('-wage', 'pk')


@never_cache
@ensure_csrf_cookie
@require_http_methods(['GET', 'POST'])
def favorites_page(request):
    if request.method == 'GET':
        return render(request, 'job_offer/favorites.html')
    lead = _lead(request)
    if not lead:
        return JsonResponse({'ok': False, 'error': 'Не намерихме запазен списък в този браузър.'}, status=404)
    items = [{
        'id': str(offer.pk),
        'position': offer.job_position or 'Работна оферта',
        'employer': offer.employer_name or 'AIM Travel',
        'city': offer.city.name or '',
        'state': offer.city.state or '',
        'wage': offer.wage,
        'tips': offer.tips == 'Да',
        'housing': housing_summary(offer.housing),
        'image': offer.offer_pic.url if offer.offer_pic else '',
        'url': reverse('details offer', kwargs={'pk': offer.pk}),
    } for offer in _offers(lead)]
    return JsonResponse({'ok': True, 'offers': items})


@never_cache
@require_POST
def remove_favorite(request):
    lead = _lead(request)
    if not lead:
        return JsonResponse({'ok': False, 'error': 'Списъкът не е достъпен.'}, status=404)
    offer_id = request.POST.get('offer_id', '')
    if (not offer_id.isascii() or not offer_id.isdigit()
            or len(offer_id) > 18 or int(offer_id) < 1):
        return JsonResponse({'ok': False, 'error': 'Невалидна оферта.'}, status=400)
    lead.favorite_offers.remove(int(offer_id))
    lead.updated_at = timezone.now()
    lead.save(update_fields=['updated_at'])
    return JsonResponse({'ok': True})


def _csv_cell(value):
    value = '' if value is None else str(value)
    # User-entered values must remain text when opened in a spreadsheet.
    if value.lstrip().startswith(('=', '+', '-', '@')) or value.startswith(('\t', '\r', '\n')):
        return "'" + value
    return value


@never_cache
@staff_member_required
def export_favorites(request):
    if not request.user.has_perm('web.view_offerlead'):
        raise PermissionDenied
    output = io.StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(['ID студент', 'Имена', 'Имейл', 'Телефон', 'Университет', 'Курс',
                     'Специалност', 'Статус', 'Създаден на', 'ID оферта',
                     'Работодател', 'Позиция', 'Град', 'Щат', 'Линк'])
    for lead in OfferLead.objects.prefetch_related('favorite_offers__city').order_by('pk').iterator(chunk_size=200):
        base = [lead.pk, f'{lead.first_name} {lead.last_name}'.strip(), lead.email,
                lead.phone, lead.university, lead.course, lead.specialty,
                lead.get_status_display(), lead.created_at.isoformat()]
        offers = list(lead.favorite_offers.all())
        for offer in offers or [None]:
            detail = [offer.pk, offer.employer_name, offer.job_position,
                      offer.city.name, offer.city.state,
                      request.build_absolute_uri(reverse('details offer', kwargs={'pk': offer.pk}))] if offer else [''] * 6
            writer.writerow([_csv_cell(value) for value in base + detail])
    response = HttpResponse('\ufeff' + output.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="aim-favorites.csv"'
    return response
