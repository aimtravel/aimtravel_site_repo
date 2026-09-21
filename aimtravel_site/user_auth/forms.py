from django import forms
from django.contrib.auth import forms as auth_forms, get_user_model, password_validation
from django.core.exceptions import ValidationError

from aimtravel_site.user_auth.models import AppUser

UserModel = get_user_model()


class SignUpForm(auth_forms.UserCreationForm):
    first_name = forms.CharField(
        label="Име",
        strip=False,
        widget=forms.TextInput(),
        help_text='Въведете името си',
    )
    last_name = forms.CharField(
        label="Фамилия",
        strip=False,
        widget=forms.TextInput(),
        help_text='Въведете фамилията си',
    )
    password1 = forms.CharField(
        label="Парола",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Потвърди паролата",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text="Моля въведете отново паролата за потвърждение",
    )

    class Meta:
        model = UserModel
        fields = (UserModel.USERNAME_FIELD, 'first_name', 'last_name', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password2", error)
    """
    No need of override save method if use signal
    """
    # def save(self, commit=True):
    #     user = super().save(commit=commit)
    #
    #     profile = UserModel(user=user)
    #
    #     if commit:
    #         profile.save()
    #
    #     return user


class SignInForm(auth_forms.AuthenticationForm):
    username = auth_forms.UsernameField(widget=forms.EmailInput(attrs={
        "autofocus": True,
        "placeholder": "your@email.com",
        "class": "form-control fakepassword",
    }))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            "placeholder": "Password",
            "class": "form-control",
        }),
    )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError(
                'Този вход е само за консултанти на AIM Travel.',
                code='staff_only',
            )


class PersonAccessForm(forms.Form):
    email = forms.EmailField(
        label='Имейл',
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'placeholder': 'ivan.petrov@gmail.com',
        }),
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=40,
        widget=forms.TextInput(attrs={
            'autocomplete': 'tel',
            'inputmode': 'tel',
            'placeholder': '0888 123 456',
        }),
    )
    first_name = forms.CharField(
        label='Име', max_length=80, required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'given-name'}),
    )
    last_name = forms.CharField(
        label='Фамилия', max_length=80, required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'family-name'}),
    )
    university = forms.CharField(label='Университет', max_length=160, required=False)
    course = forms.ChoiceField(
        label='Курс', required=False,
        choices=(
            ('', 'Избери курс'), ('1 курс', '1 курс'), ('2 курс', '2 курс'),
            ('3 курс', '3 курс'), ('4 курс', '4 курс'), ('5 курс', '5 курс'),
            ('Магистратура', 'Магистратура'),
        ),
    )
    specialty = forms.CharField(label='Специалност', max_length=160, required=False)
    lead_token = forms.CharField(required=False, widget=forms.HiddenInput())
    privacy_consent = forms.BooleanField(
        label='Съгласен/на съм AIM Travel да използва данните ми за профила и програмата.',
    )

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()

    def clean_phone(self):
        raw_phone = self.cleaned_data['phone'].strip()
        digits = ''.join(character for character in raw_phone if character.isdigit())
        if digits.startswith('359') and len(digits) >= 11:
            digits = '0' + digits[3:]
        if len(digits) < 9:
            raise ValidationError('Въведи валиден телефонен номер.')
        return digits


class VerificationCodeForm(forms.Form):
    code = forms.CharField(
        label='Код за вход',
        min_length=6,
        max_length=6,
        widget=forms.TextInput(attrs={
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
            'placeholder': '000000',
        }),
    )

    def clean_code(self):
        code = self.cleaned_data['code'].strip()
        if not code.isdigit():
            raise ValidationError('Кодът съдържа само цифри.')
        return code


class EditForm(auth_forms.UserChangeForm):
    fieldsets = (
        (None, {'fields': ("email", "password")}),
        ("Permissions", {'fields': ('is_staff', 'is_active', 'date_joined')}),
        ("Additional", {'fields': 'user_picture'}),
    )

    class Meta:
        model = UserModel
        fields = '__all__'
        field_classes = {'email': auth_forms.UsernameField}


class MyProfileForm(forms.ModelForm):
    class Meta:
        model = AppUser
        exclude = ['user']


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ['first_name', 'last_name', 'user_picture']
