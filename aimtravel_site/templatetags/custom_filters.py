import re

from django import template

register = template.Library()


@register.filter
def to_string(value):
    return str(value)


@register.filter
def housing_summary(value):
    """Return a rounded, consistently formatted weekly housing price in USD."""
    if value is None:
        return 'По оферта'
    cleaned = str(value).strip()
    if cleaned in ('', '-', '$', '0', 'N/A', 'Не'):
        return 'По оферта'

    amounts = re.findall(r'\d+(?:[.,]\d+)?', cleaned)
    if not amounts:
        return 'По оферта'

    rounded = [int(round(float(amount.replace(',', '.')))) for amount in amounts]
    rounded = [amount for amount in rounded if amount > 0]
    if not rounded:
        return 'По оферта'

    if len(rounded) > 1 and rounded[0] != rounded[1]:
        return f'${rounded[0]}–${rounded[1]}/седм.'
    return f'${rounded[0]}/седм.'
