from django import forms

from aimtravel_site import settings
from aimtravel_site.taxes.models import *

User = get_user_model()


class AddTaxes(forms.ModelForm):
    class Meta:
        model = Taxes
        exclude = ['user', 'first_name',
                   'family_name', 'email']
        # Exclude the user, first and last name fields from being displayed in the form

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pop the user from kwargs
        super().__init__(*args, **kwargs)
        if user:
            self.instance.user = user  # Set the user on the form instance
            self.instance.first_name = user.first_name  # Automatically set the first name
            self.instance.family_name = user.last_name
            self.instance.email = user.email
            # Automatically set the last_name in userAuth, a.k.a. family_name in taxes model


class AdminAddTaxes(forms.ModelForm):
    class Meta:
        model = Taxes
        fields = ['user', 'first_name', 'family_name', 'email']


class AdminEditTaxes(forms.ModelForm):
    passport_copy_clear = forms.BooleanField(required=False)
    visa_copy_clear = forms.BooleanField(required=False)
    ssn_copy_clear = forms.BooleanField(required=False)
    last_paycheck_doc_clear = forms.BooleanField(required=False)
    w2_form_clear = forms.BooleanField(required=False)
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


class EditTaxesForm(forms.ModelForm):
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
    passport_copy_clear = forms.BooleanField(required=False)
    visa_copy_clear = forms.BooleanField(required=False)
    ssn_copy_clear = forms.BooleanField(required=False)
    last_paycheck_doc_clear = forms.BooleanField(required=False)
    w2_form_clear = forms.BooleanField(required=False)
    bank_account_screenshot_clear = forms.BooleanField(required=False)
    us_document_copy_clear = forms.BooleanField(required=False)
    signed_and_scanned_contract_clear = forms.BooleanField(required=False)

    class Meta:
        model = Taxes
        exclude = ['user']
