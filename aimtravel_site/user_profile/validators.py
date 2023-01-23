from django.core.exceptions import ValidationError


def only_letters(text):
    if not text.isalpha():
        raise ValidationError("Използвате забранен символ в текстово поле. Очакват се само букви.")


def only_digits(text):
    if not text.isdigit():
        raise ValidationError("Поле за телефонен номер или номер на документ трябва да съдържа само цифри.")

