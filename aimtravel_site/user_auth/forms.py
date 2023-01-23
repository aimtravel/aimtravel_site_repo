from django import forms
from django.contrib.auth import forms as auth_forms, get_user_model, password_validation
from django.core.exceptions import ValidationError

UserModel = get_user_model()


class SignUpForm(auth_forms.UserCreationForm):
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
        fields = (UserModel.USERNAME_FIELD, 'password1', 'password2')

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


class EditForm(auth_forms.UserChangeForm):
    fieldsets = (
        (None, {'fields': ("email", "password")}),
        ("Permissions", {'fields': ('is_staff', 'is_active', 'date_joined')})
    )

    class Meta:
        model = UserModel
        fields = '__all__'
        field_classes = {'email': auth_forms.UsernameField}
