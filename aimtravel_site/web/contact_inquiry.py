"""Contact callback form: signed, short-lived, single-attempt image CAPTCHA."""
import base64
import io
import logging
import os
from pathlib import Path
import secrets
import subprocess
import time

from django.conf import settings
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.crypto import constant_time_compare, salted_hmac
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

SALT = 'aim-contact-captcha-v1'
ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
logger = logging.getLogger(__name__)


def _deliver(mail):
    """Use authenticated SMTP, or the hosting account's local mail transport.

    SuperHosting supports /usr/sbin/sendmail for Python. This only applies when
    no SMTP password is configured; SMTP failures never trigger a second send.
    """
    if (settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend'
            and not getattr(settings, 'EMAIL_HOST_PASSWORD', '')):
        sender = 'studentski@aimtravel.bg'
        mail.from_email = sender
        validate_email(sender)
        if sender.rsplit('@', 1)[-1].lower() != 'aimtravel.bg':
            raise ValueError('Contact sender must belong to aimtravel.bg')
        result = subprocess.run(
            ['/usr/sbin/sendmail', '-oi', '-f', sender, 'studentski@aimtravel.bg'],
            input=mail.message().as_bytes(), stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=20, check=False,
        )
        if result.returncode:
            raise RuntimeError('Local mail transport rejected message')
        return 1
    return mail.send(fail_silently=False)


def _digest(value):
    return salted_hmac(SALT, value, algorithm='sha256').hexdigest()


def _binding(request):
    get_token(request)
    return _digest(request.META['CSRF_COOKIE'])


def _consume(nonce):
    # Exclusive creation is shared across Passenger workers, unlike LocMemCache.
    directory = Path(settings.BASE_DIR) / 'tmp' / 'contact-captcha-used'
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    now = time.time()
    for item in directory.iterdir():
        if len(item.name) == 32 and all(c in '0123456789abcdef' for c in item.name):
            try:
                if item.stat().st_mtime < now - 900:
                    item.unlink()
            except FileNotFoundError:
                pass
    try:
        fd = os.open(str(directory / nonce), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    os.close(fd)
    return True


def _image(answer):
    from PIL import Image, ImageDraw, ImageFont
    image = Image.new('RGB', (240, 76), '#f3f6fa')
    draw = ImageDraw.Draw(image)
    font_path = Path(settings.BASE_DIR) / 'static/fonts/Jost/fontrepo/Jost-SemiBold.ttf'
    try:
        font = ImageFont.truetype(str(font_path), 38)
    except OSError:
        # Pillow's built-in font is always available; enlarge before compositing.
        font = ImageFont.load_default()
    for _ in range(85):
        x, y = secrets.randbelow(240), secrets.randbelow(76)
        draw.ellipse((x, y, x + 2, y + 2), fill='#acbac7')
    for index, char in enumerate(answer):
        glyph = Image.new('RGBA', (50, 65))
        ImageDraw.Draw(glyph).text((7, 3), char, font=font, fill='#102c3d')
        if not font_path.exists():
            glyph = glyph.crop((5, 3, 20, 19)).resize((38, 48))
        glyph = glyph.rotate(secrets.randbelow(19) - 9, resample=Image.Resampling.BICUBIC)
        image.paste(glyph, (index * 36 + 5, secrets.randbelow(7) + 5), glyph)
    for _ in range(2):
        draw.line((0, secrets.randbelow(76), 240, secrets.randbelow(76)), fill='#8ba1b3', width=1)
    output = io.BytesIO()
    image.save(output, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(output.getvalue()).decode('ascii')


def _new_answer():
    return ''.join(secrets.choice(ALPHABET) for _ in range(6))


@never_cache
@require_GET
def contact_captcha(request):
    answer = _new_answer()
    nonce = secrets.token_hex(16)
    payload = {'n': nonce, 'h': _digest(nonce + answer), 'b': _binding(request)}
    return JsonResponse({'image': _image(answer), 'token': signing.dumps(payload, salt=SALT)})


def _valid_captcha(request):
    token = request.POST.get('captcha_token', '')
    answer = request.POST.get('captcha_answer', '').strip().upper()
    if len(token) > 1000 or len(answer) != 6:
        return False
    try:
        data = signing.loads(token, salt=SALT, max_age=300)
        nonce = data['n']
        if len(nonce) != 32 or any(c not in '0123456789abcdef' for c in nonce):
            return False
        if not constant_time_compare(data['b'], _binding(request)):
            return False
        if not _consume(nonce):
            return False
        return constant_time_compare(data['h'], _digest(nonce + answer))
    except (signing.BadSignature, KeyError, TypeError, ValueError, OSError):
        return False


@never_cache
@require_POST
@csrf_protect
def contact_inquiry(request):
    def error(message, status=400):
        return JsonResponse({'message': message}, status=status)
    if request.POST.get('website') or not _valid_captcha(request):
        return error('Проверката е неуспешна или е изтекла. Въведи символите от новата картинка.')
    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone-field', '').strip()
    email = request.POST.get('email-field', '').strip()
    message = request.POST.get('message', '').strip()
    if not 2 <= len(name) <= 120 or not 6 <= len(phone) <= 30 or not 1 <= len(message) <= 5000:
        return error('Попълни име, телефон и съобщение в посочените полета.')
    if len(email) > 254 or '\n' in email or '\r' in email:
        return error('Провери имейл адреса.')
    if email:
        try:
            validate_email(email)
        except ValidationError:
            return error('Провери имейл адреса.')
    body = f'Запитване за обратно обаждане от сайта\n\nИме: {name}\nТелефон: {phone}\nИмейл: {email or "не е посочен"}\n\n{message}'
    try:
        mail = EmailMessage(
            subject='AIM Travel: запитване за обратно обаждане', body=body,
            from_email=getattr(settings, 'EMAIL_HOST_USER', '') or settings.DEFAULT_FROM_EMAIL,
            to=['studentski@aimtravel.bg'], reply_to=[email] if email else [],
        )
        if _deliver(mail) != 1:
            raise RuntimeError('No message accepted')
    except Exception as exc:
        logger.error('Contact inquiry delivery failed: %s (SMTP code %s)',
                     type(exc).__name__, getattr(exc, 'smtp_code', 'n/a'))
        return error('Не успяхме да изпратим съобщението. Опитай отново или ни пиши във Viber.', 503)
    return JsonResponse({'message': 'Благодарим ти! Получихме съобщението и ще ти се обадим на посочения телефон.'})

