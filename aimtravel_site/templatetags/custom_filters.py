from django import template

register = template.Library()


@register.filter
def to_string(value):
    return str(value)


@register.filter
def housing_summary(value):
    """Return a compact, user-friendly weekly housing price."""
    if value is None:
        return 'По оферта'
    cleaned = str(value).strip()
    if cleaned in ('', '-', '$', '0', 'N/A', 'Не'):
        return 'По оферта'
    if not cleaned.startswith('$'):
        cleaned = f'${cleaned}'
    return f'{cleaned}/седм.'
