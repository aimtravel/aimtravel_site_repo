from django import forms
from aimtravel_site.taxes.models import *


class AddTaxes(forms.ModelForm):
    class Meta:
        model = Taxes
        fields = '__all__'


class EditTaxes(forms.ModelForm):
    class Meta:
        model = Taxes
        exclude = ['user']
        # fields = '__all__'
        # widgets = {
        #     'user': forms.HiddenInput(),  # Hide the user field in the HTML form
        # }


class AdminEditTaxes(forms.ModelForm):
    passport_copy_clear = forms.BooleanField(required=False)
    visa_copy_clear = forms.BooleanField(required=False)
    ssn_copy_clear = forms.BooleanField(required=False)
    last_paycheck_w2_clear = forms.BooleanField(required=False)
    bank_account_screenshot_clear = forms.BooleanField(required=False)
    us_document_copy_clear = forms.BooleanField(required=False)

    class Meta:
        model = Taxes
        exclude = ['user']


class TaxesDetailForm(forms.ModelForm):
    class Meta:
        model = Taxes
        fields = '__all__'
