"""Public, fixed contact links; no participant data or redirects."""
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def viber_contact(request):
    return render(request, 'viber_contact.html')


@require_GET
def viber_contact_card(request):
    card = '\r\n'.join([
        'BEGIN:VCARD', 'VERSION:3.0', 'N:Travel;AIM;;;', 'FN:AIM Travel',
        'ORG:AIM Travel', 'TEL;TYPE=CELL:+359889966583',
        'EMAIL:studentski@aimtravel.bg', 'URL:https://aimtravel.bg/', 'END:VCARD', '',
    ])
    response = HttpResponse(card, content_type='text/vcard; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="AIM-Travel.vcf"'
    response['X-Content-Type-Options'] = 'nosniff'
    return response
