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


class TaxesDetailForm(forms.ModelForm):
    class Meta:
        model = Taxes
        fields = '__all__'
