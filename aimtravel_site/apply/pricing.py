"""Server-owned EUR quotes. Discount amounts are never taken from the browser."""
from django.utils import timezone
from rest_framework.exceptions import ValidationError

PRICES = {"full_arranged": 1699, "self_arranged": 1499}
DEPOSIT = 200
SEVIS = 32
PROTECTION = 249


def quote(option, protection=False, code="", *, lock=False, adjustment=0):
    from .models import DiscountCode

    base = PRICES[option]
    discount = None
    normalized = code.strip().upper()
    if isinstance(adjustment, bool) or not isinstance(adjustment, int) or not 0 <= adjustment <= 690 or adjustment % 10:
        raise ValidationError({"fee_adjustment_eur": "Въведи сума от 0 до 690 евро, кратна на 10."})
    if normalized and adjustment:
        raise ValidationError({"fee_adjustment_eur": "Корекцията не може да се комбинира с код."})
    if normalized:
        query = DiscountCode.objects
        if lock:
            query = query.select_for_update()
        discount = query.filter(code=normalized, active=True).first()
        now = timezone.now()
        if (discount is None or discount.season != 2027
                or (discount.starts_at and now < discount.starts_at)
                or (discount.expires_at and now >= discount.expires_at)
                or discount.used_count >= discount.max_uses
                or discount.amount_eur > base - 800):
            raise ValidationError({"discount_code": "Невалиден, изтекъл или изчерпан код."})
    amount = discount.amount_eur if discount else adjustment
    return {
        "base_price_eur": base,
        "discount_eur": amount,
        "price_eur": base - amount,
        "protection_fee_eur": PROTECTION if protection else 0,
        "first_payment_eur": DEPOSIT + SEVIS + (PROTECTION if protection else 0),
        "discount_code": normalized,
    }, discount
