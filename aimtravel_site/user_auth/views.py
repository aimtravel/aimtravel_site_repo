from django.contrib.auth import login, views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.files.storage import default_storage
from django.core.mail import send_mail, BadHeaderError
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import generic as views

from aimtravel_site.user_auth.forms import SignUpForm, SignInForm, MyProfileForm, EditProfileForm
from aimtravel_site.user_auth.models import AppUser
from aimtravel_site.taxes.models import Taxes
from aimtravel_site.user_profile.models import Employee, Students


class SignUpView(views.CreateView):
    template_name = 'user_auth/register-page.html'
    form_class = SignUpForm

    success_url = reverse_lazy('index')

    def form_valid(self, form):
        result = super().form_valid(form)

        login(self.request, self.object)
        return result


class SignInView(auth_views.LoginView):
    template_name = 'user_auth/auth_page.html'
    form_class = SignInForm

    def get_success_url(self):
        # Access the authenticated user and get their ID
        user_slug = self.request.user.slug

        # Redirect to the 'my-profile' view with the user ID
        return reverse_lazy('my-profile', kwargs={'slug': user_slug})


class SignOutView(auth_views.LogoutView):
    template_name = 'user_auth/sign-out.html'


def auth_option(request):
    return render(request, template_name='user_auth/auth_page.html')


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = AppUser.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': 'https://www.aimtravel.bg',
                        'site_name': 'AIM Travel',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'studentski@aimtravel.bg', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_reset.html",
                  context={"password_reset_form": password_reset_form})


class EditUserProfileView(LoginRequiredMixin, views.UpdateView):
    model = AppUser
    form_class = EditProfileForm
    template_name = 'user_auth/change_profile.html'
    context_object_name = 'edit_user'

    def form_valid(self, form):
        # Check if a new picture is uploaded
        if 'user_picture' in self.request.FILES:
            # Delete the old picture
            if form.instance.user_picture:
                default_storage.delete(form.instance.user_picture.path)

            # Save the new picture
            form.instance.user_picture = self.request.FILES['user_picture']

        return super().form_valid(form)

    def get_success_url(self):
        user = self.object
        user_slug = user.slug
        return reverse_lazy('my-profile', kwargs={'slug': user_slug})


class MyProfileView(LoginRequiredMixin, views.DetailView):
    model = AppUser
    template_name = 'user_auth/my_profile.html'
    form_class = MyProfileForm
    context_object_name = 'my_profile_details'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_profile = Employee.objects.all()
        students_profile = Students.objects.all()



        if employee_profile:
            # Add employee_profile to the context
            context['employee_profile'] = Employee.objects.all()
        if students_profile:
            # Add students_profile to the context
            context['students_profile'] = Students.objects.all()
            # Handle the case when there are no tax profiles

        tax_profile = Taxes.objects.filter(user=self.request.user)

        if not tax_profile.exists():
            context['latest_tax'] = None
            context['tax_profile'] = None
        else:
            # Add latest_tax to the context
            latest_tax = tax_profile.latest('pk')
            context['latest_tax'] = latest_tax
            # Add tax_profile to the context
            context['tax_profile'] = tax_profile

        return context
