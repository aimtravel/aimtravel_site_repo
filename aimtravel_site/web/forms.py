from django import forms

from aimtravel_site.web.models import JobOffer, Company, Prices, AdditionalServices


class JobOfferDetailForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        fields = '__all__'


class JobOfferEditForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        fields = '__all__'

        widgets = {
            'job_position': forms.TextInput(attrs={'placeholder': 'Позиция'}),
            'employer': forms.TextInput(attrs={'placeholder': 'Работодател'}),
            'city': forms.TextInput(attrs={'placeholder': 'Град'}),
            'state': forms.TextInput(attrs={'placeholder': 'Щат'}),
            'sponsor': forms.TextInput(attrs={'placeholder': 'Спонсор'}),
            'offer_pic': forms.TextInput(attrs={'placeholder': 'Снимка-URL'}),
        }


class CompanyDetailForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'


class CompanyEditForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'

        widgets = {
            'employer_name': forms.TextInput(attrs={'placeholder': 'Работодател'}),
            'employer_city': forms.TextInput(attrs={'placeholder': 'Град'}),
            'employer_state': forms.TextInput(attrs={'placeholder': 'Щат'}),
            'employer_history': forms.Textarea(attrs={'placeholder': 'Кратка история'}),
            'employer_photo': forms.TextInput(attrs={'placeholder': 'Снимка-URL'}),
        }


class PriceDetailForm(forms.ModelForm):
    class Meta:
        model = Prices
        fields = '__all__'


class ServiceDetailForm(forms.ModelForm):
    class Meta:
        model = AdditionalServices
        fields = '__all__'
