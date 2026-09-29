import re

from django import template

register = template.Library()


@register.filter
def to_string(value):
    return str(value)


@register.filter
def housing_summary(value):
    """Return a rounded, consistently formatted weekly housing price in USD."""
    housing_range = housing_weekly_range(value)
    if housing_range is None:
        return 'По оферта'
    low, high = housing_range
    if low == high == 0:
        return 'Безплатно'
    if low != high:
        return f'${low}–${high}/седм.'
    return f'${low}/седм.'


def housing_weekly_range(value):
    """Return a rounded (minimum, maximum) weekly USD range, or None."""
    if value is None:
        return None
    cleaned = str(value).strip()
    if cleaned.lower() in ('0', 'free', 'безплатно', 'безплатен'):
        return 0, 0
    if cleaned in ('', '-', '$', 'N/A', 'Не'):
        return None
    amounts = re.findall(r'\d+(?:[.,]\d+)?', cleaned)
    rounded = [int(round(float(amount.replace(',', '.')))) for amount in amounts]
    rounded = [amount for amount in rounded if amount > 0]
    if not rounded:
        return None
    return min(rounded), max(rounded)
