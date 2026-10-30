"""Public, fixed contact links; no participant data or redirects."""
from django.http import HttpResponse
from django.views.decorators.http import require_safe


@require_safe
def viber_contact(request):
    # Compatibility for emails already sent with the former HTTPS destination.
    return HttpResponse(status=302, headers={'Location': 'viber://chat?number=%2B359889966583'})


@require_safe
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
