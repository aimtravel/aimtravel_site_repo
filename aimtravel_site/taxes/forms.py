from django import forms

from aimtravel_site import settings
from aimtravel_site.taxes.models import *


class AddTaxes(forms.ModelForm):
    class Meta:
        model = Taxes
        fields = '__all__'


class EditTaxes(forms.ModelForm):
    passport_copy_clear = forms.BooleanField(required=False)
    visa_copy_clear = forms.BooleanField(required=False)
    ssn_copy_clear = forms.BooleanField(required=False)
    last_paycheck_w2_clear = forms.BooleanField(required=False)
    bank_account_screenshot_clear = forms.BooleanField(required=False)
    us_document_copy_clear = forms.BooleanField(required=False)
    signed_and_scanned_contract_clear = forms.BooleanField(required=False)
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(format='%d.%m.%Y'),
        input_formats=settings.DATE_INPUT_FORMATS
    )
    issue_date = forms.DateField(
        required=False,
        widget=forms.DateInput(format='%d.%m.%Y'),
        help_text="dd-mm-yyyy",
        input_formats=settings.DATE_INPUT_FORMATS
    )
    arrival_date_in_usa = forms.DateField(
        required=False,
        widget=forms.DateInput(format='%d.%m.%Y'),
        input_formats=settings.DATE_INPUT_FORMATS
    )
    departure_date_in_usa = forms.DateField(
        required=False,
        widget=forms.DateInput(format='%d.%m.%Y'),
        input_formats=settings.DATE_INPUT_FORMATS
    )

    class Meta:
        model = Taxes
        exclude = ['user']


class AdminEditTaxes(forms.ModelForm):
    passport_copy_clear = forms.BooleanField(required=False)
    visa_copy_clear = forms.BooleanField(required=False)
    ssn_copy_clear = forms.BooleanField(required=False)
    last_paycheck_w2_clear = forms.BooleanField(required=False)
    bank_account_screenshot_clear = forms.BooleanField(required=False)
    us_document_copy_clear = forms.BooleanField(required=False)
    signed_and_scanned_contract_clear = forms.BooleanField(required=False)
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(format='%d.%m.%Y'),
        input_formats=settings.DATE_INPUT_FORMATS
    )
    issue_date = forms.DateField(
        required=False,
        widget=forms.DateInput(format='%d.%m.%Y'),
        help_text="dd-mm-yyyy",
        input_formats=settings.DATE_INPUT_FORMATS
    )
    arrival_date_in_usa = forms.DateField(
        required=False,
        widget=forms.DateInput(format='%d.%m.%Y'),
        input_formats=settings.DATE_INPUT_FORMATS
    )
    departure_date_in_usa = forms.DateField(
        required=False,
        widget=forms.DateInput(format='%d.%m.%Y'),
        input_formats=settings.DATE_INPUT_FORMATS
    )

    class Meta:
        model = Taxes
        exclude = ['user']


class TaxesDetailForm(forms.ModelForm):
    class Meta:
        model = Taxes
        fields = '__all__'
