from django.core.exceptions import ValidationError


def max_value(value):
    if value <=0 or value > 1000:
        raise ValidationError('Рангът на офертата трябва да е между 1 и 1000.')
