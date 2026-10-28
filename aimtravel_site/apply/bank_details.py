"""Bank details from the supplied 2027 agreement, attached to the email."""
from io import BytesIO
from pathlib import Path

from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

BANK_IBAN = 'BG60UNCR70001523205219'
BANK_NAME = 'УниКредит Булбанк АД'
BANK_BENEFICIARY = 'АГЕНЦИЯ ЗА МЕЖДУНАРОДНА МОБИЛНОСТ ООД'

def bank_pdf(application):
    font = Path(settings.BASE_DIR) / 'static/fonts/Jost/fontrepo/Jost-Regular.ttf'
    pdfmetrics.registerFont(TTFont('AIMBank', str(font)))
    result = BytesIO()
    page = canvas.Canvas(result, pagesize=(595, 842))
    page.setTitle('AIM Travel • Банкови данни')
    page.setFont('AIMBank', 20)
    page.drawString(50, 775, 'Данни за банков превод')
    page.setFont('AIMBank', 12)
    lines = [
        f'Получател: {BANK_BENEFICIARY}',
        f'Банка: {BANK_NAME}',
        f'IBAN: {BANK_IBAN}',
        'Валута: EUR',
        f'Основание: {application.contract_number}',
        '',
        'Депозит: 200 евро',
        'SEVIS: 32 евро',
    ]
    if application.save_exchange:
        lines.append(f'Save Exchange: {application.protection_fee_eur} евро')
    lines += ['', f'Първа вноска: {232 + application.protection_fee_eur} евро',
              'Срок: до 5 работни дни от подписване на договора.']
    if application.save_exchange:
        lines += ['Срок за Save Exchange съгласно анекса:',
                  'до 7 календарни дни от подписването на анекса.']
    y = 730
    for line in lines:
        page.drawString(50, y, line)
        y -= 26
    page.save()
    return result.getvalue()
