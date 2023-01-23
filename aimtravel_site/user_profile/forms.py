from django import forms

from aimtravel_site.user_profile.models import Students, Employee

YES_NO_CHOICES = {
    ('yes', 'Yes'),
    ('no', 'No'),
}

"""
Below two forms are related with Student Model. 
First collect data needed for WAT program.
Second shows already saved info.
"""


class StudentEditForm(forms.ModelForm):
    is_received_visa = forms.BooleanField(required=False)
    is_fulltime_student = forms.BooleanField(required=False)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(format='%d-%m-%y'),
        input_formats=[
            '%d-%m-%Y',
            '%d-%m-%y',
            '%d.%m.%y',
            '%d.%m.%Y',
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m/%d/%y',
            '%b %d %Y',
            '%b %d, %Y',
            '%d %b %Y',
            '%d %b, %Y',
            '%B %d %Y',
            '%B %d, %Y',
            '%d %B %Y',
            '%d %B, %Y']
    )
    passport_date_of_issue = forms.DateField(
        required=False,
        widget=forms.DateInput(format='%d-%m-%y'),
        input_formats=[
            '%d-%m-%Y',
            '%d-%m-%y',
            '%d.%m.%y',
            '%d.%m.%Y',
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m/%d/%y',
            '%b %d %Y',
            '%b %d, %Y',
            '%d %b %Y',
            '%d %b, %Y',
            '%B %d %Y',
            '%B %d, %Y',
            '%d %B %Y',
            '%d %B, %Y']
    )
    file_field = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
    )

    class Meta:
        model = Students
        exclude = ['user']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Име'}),
            'middle_name': forms.TextInput(attrs={'placeholder': 'Презиме'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия'}),
            'date_of_birth': forms.DateField(),
            'place_of_birth': forms.TextInput(attrs={'placeholder': 'Място на раждане'}),
            'city': forms.TextInput(attrs={'placeholder': 'Град'}),
            'province': forms.TextInput(attrs={'placeholder': 'Област'}),
            'street': forms.TextInput(attrs={'placeholder': 'Улица/ж.к.,№,бл.,вх.,ап.'}),
            'bg_personal_number': forms.TextInput(attrs={'placeholder': 'ЕГН'}),
            'nationality': forms.TextInput(attrs={'placeholder': 'Националност'}),
            'country_of_birth': forms.TextInput(attrs={'placeholder': 'Държава на раждане'}),
            'id_passport_number': forms.TextInput(attrs={'placeholder': 'Номер на паспорт'}),
            'passport_date_of_issue': forms.TextInput(attrs={'placeholder': 'Дата на издаване'}),
            'is_received_visa': forms.BooleanField(),
            'Phone': forms.TextInput(attrs={'placeholder': 'Телефонен номер'}),
            'email': forms.EmailInput(attrs={'placeholder': 'E-mail'}),
            'university': forms.TextInput(attrs={'placeholder': 'Университет'}),
            'year_of_education': forms.TextInput(attrs={'placeholder': 'Курс'}),
            'foreign_university': forms.TextInput(attrs={'placeholder': 'Чуждестранен университет'}),
            'is_fulltime_student': forms.BooleanField(),
            'search_job_pref': forms.TextInput(attrs={'placeholder': 'Предпочитана работа'}),
            'how_to_reach': forms.TextInput(attrs={'placeholder': 'Как да комуникираме?'}),
        }


class StudentDetailsForm(forms.ModelForm):
    file_field = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
    )

    class Meta:
        model = Students
        exclude = ['user']


"""
Below two forms are related with Employee Model. 
They collect data related to the employees, that can be seen on the 'about us' page and 'employee profile' page as well.
"""


class EmployeeDetailsForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ['user']


class EmployeeEditForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ['user']
        widgets = {
            'employee_first_name': forms.TextInput(attrs={'placeholder': 'Име'}, ),
            'employee_last_name': forms.TextInput(attrs={'placeholder': 'Фамилия'}, ),
            'employee_role': forms.TextInput(attrs={'placeholder': 'Позиция'}, ),
            'employee_pic': forms.TextInput(attrs={'placeholder': 'Снимка URL'}, ),
            'employee_phone': forms.TextInput(attrs={'placeholder': 'Телефон'}, ),
            'employee_email': forms.TextInput(attrs={'placeholder': 'E-mail'}, ),
        }
