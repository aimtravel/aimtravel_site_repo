import hmac
import secrets

from django.conf import settings
from django.contrib.auth import login, views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.files.storage import default_storage
from django.core.mail import send_mail, BadHeaderError
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import generic as views

from aimtravel_site.user_auth.forms import (
    SignUpForm, SignInForm, PersonAccessForm, VerificationCodeForm,
    MyProfileForm, EditProfileForm,
)
from aimtravel_site.user_auth.models import AppUser
from aimtravel_site.taxes.models import Taxes
from aimtravel_site.user_profile.models import Employee, Students
from aimtravel_site.web.models import OfferLead


class SignUpView(views.CreateView):
    template_name = 'user_auth/register-page.html'
    form_class = SignUpForm

    # success_url = reverse_lazy('index')

    def form_valid(self, form):
        result = super().form_valid(form)

        login(self.request, self.object)
        return redirect(self.object.get_absolute_url())
    # def get_success_url(self):
    #     # Access the authenticated user and get their ID
    #     user_slug = self.request.user.slug
    #
    #     # Redirect to the 'my-profile' view with the user ID
    #     return reverse_lazy('my-profile', kwargs={'slug': user_slug})


class SignInView(views.View):
    template_name = 'user_auth/auth_page.html'

    challenge_session_key = 'person_login_challenge'
    payload_session_key = 'person_login_payload'
    challenge_lifetime = 10 * 60
    max_attempts = 5

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(self._success_url(request.user))
        return self._render(request)

    def post(self, request):
        action = request.POST.get('action', 'person_start')
        if action == 'consultant_login':
            return self._consultant_login(request)
        if action == 'person_verify':
            return self._person_verify(request)
        return self._person_start(request)

    def _render(self, request, **extra):
        context = {
            'person_form': extra.pop('person_form', PersonAccessForm()),
            'consultant_form': extra.pop('consultant_form', SignInForm(request=request)),
            'code_form': extra.pop('code_form', VerificationCodeForm()),
            'verification_mode': extra.pop('verification_mode', False),
            'verification_email': extra.pop('verification_email', ''),
        }
        context.update(extra)
        return render(request, self.template_name, context)

    def _next_url(self, request):
        candidate = request.POST.get('next') or request.GET.get('next') or ''
        if candidate and url_has_allowed_host_and_scheme(
            candidate, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
        ):
            return candidate
        return ''

    @staticmethod
    def _success_url(user):
        if user.is_staff:
            return reverse('my-profile', kwargs={'slug': user.slug})
        return reverse('student portal')

    def _consultant_login(self, request):
        form = SignInForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(self._next_url(request) or self._success_url(user))
        return self._render(request, consultant_form=form, active_tab='consultant')

    def _person_start(self, request):
        form = PersonAccessForm(request.POST)
        if not form.is_valid():
            return self._render(request, person_form=form, active_tab='person')

        payload = {
            key: form.cleaned_data.get(key, '')
            for key in (
                'email', 'phone', 'first_name', 'last_name', 'university',
                'course', 'specialty', 'lead_token',
            )
        }
        existing_user = AppUser.objects.filter(email=payload['email']).first()
        if existing_user and existing_user.is_staff:
            form.add_error('email', 'Използвай входа за AIM консултант с този имейл.')
            return self._render(request, person_form=form, active_tab='person')

        now = int(timezone.now().timestamp())
        previous_challenge = request.session.get(self.challenge_session_key, {})
        if (
            previous_challenge.get('email') == payload['email'] and
            now - previous_challenge.get('sent_at', 0) < 60
        ):
            form.add_error(None, 'Код вече е изпратен. Изчакай една минута преди нов опит.')
            return self._render(request, person_form=form, active_tab='person')

        code = f'{secrets.randbelow(1000000):06d}'
        request.session[self.challenge_session_key] = {
            'email': payload['email'],
            'code_hash': salted_hmac(
                'person-login', f"{payload['email']}:{code}"
            ).hexdigest(),
            'expires_at': now + self.challenge_lifetime,
            'attempts': 0,
            'sent_at': now,
            'next': self._next_url(request),
        }
        request.session[self.payload_session_key] = payload

        try:
            send_mail(
                'Твоят код за вход в AIM Travel',
                (
                    f'Кодът ти за вход е: {code}\n\n'
                    'Кодът е валиден 10 минути. Ако не си поискал този код, '
                    'не е необходимо да правиш нищо.'
                ),
                settings.DEFAULT_FROM_EMAIL,
                [payload['email']],
                fail_silently=False,
            )
        except Exception:
            request.session.pop(self.challenge_session_key, None)
            request.session.pop(self.payload_session_key, None)
            form.add_error(None, 'Не успяхме да изпратим кода. Опитай отново след малко.')
            return self._render(request, person_form=form, active_tab='person')

        return self._render(
            request,
            verification_mode=True,
            verification_email=payload['email'],
            active_tab='person',
        )

    def _person_verify(self, request):
        form = VerificationCodeForm(request.POST)
        challenge = request.session.get(self.challenge_session_key)
        payload = request.session.get(self.payload_session_key)
        if not challenge or not payload:
            form.add_error(None, 'Заявката е изтекла. Поискай нов код.')
            return self._render(request, code_form=form, active_tab='person')

        now = int(timezone.now().timestamp())
        if now > challenge.get('expires_at', 0):
            request.session.pop(self.challenge_session_key, None)
            request.session.pop(self.payload_session_key, None)
            form.add_error(None, 'Кодът е изтекъл. Поискай нов код.')
            return self._render(request, code_form=form, active_tab='person')

        if not form.is_valid():
            return self._render(
                request, code_form=form, verification_mode=True,
                verification_email=challenge['email'], active_tab='person',
            )

        challenge['attempts'] = challenge.get('attempts', 0) + 1
        request.session[self.challenge_session_key] = challenge
        expected = salted_hmac(
            'person-login', f"{challenge['email']}:{form.cleaned_data['code']}"
        ).hexdigest()
        if not hmac.compare_digest(expected, challenge['code_hash']):
            if challenge['attempts'] >= self.max_attempts:
                request.session.pop(self.challenge_session_key, None)
                request.session.pop(self.payload_session_key, None)
                form.add_error(None, 'Твърде много опити. Поискай нов код.')
                return self._render(request, code_form=form, active_tab='person')
            form.add_error('code', 'Кодът не е правилен.')
            return self._render(
                request, code_form=form, verification_mode=True,
                verification_email=challenge['email'], active_tab='person',
            )

        with transaction.atomic():
            user, user_created = AppUser.objects.get_or_create(
                email=payload['email'],
                defaults={
                    'phone': payload['phone'],
                    'first_name': payload['first_name'] or None,
                    'last_name': payload['last_name'] or None,
                },
            )
            if user_created:
                user.set_unusable_password()
            user.phone = payload['phone']
            if payload['first_name']:
                user.first_name = payload['first_name']
            if payload['last_name']:
                user.last_name = payload['last_name']
            user.save()

            lead = None
            if payload.get('lead_token'):
                lead = OfferLead.objects.filter(
                    public_id=payload['lead_token'], email=payload['email']
                ).first()
            if not lead:
                lead, _ = OfferLead.objects.get_or_create(
                    email=payload['email'],
                    defaults={'phone': payload['phone']},
                )
            lead.user = user
            lead.phone = payload['phone']
            for field in ('first_name', 'last_name', 'university', 'course', 'specialty'):
                if payload.get(field):
                    setattr(lead, field, payload[field])
            lead.privacy_consent = True
            lead.save()

        request.session.pop(self.challenge_session_key, None)
        request.session.pop(self.payload_session_key, None)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect(challenge.get('next') or self._success_url(user))


class StudentPortalView(LoginRequiredMixin, views.TemplateView):
    template_name = 'user_auth/student_portal.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('my-profile', slug=request.user.slug)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lead = OfferLead.objects.filter(user=self.request.user).prefetch_related(
            'favorite_offers__city'
        ).first()
        if not lead:
            lead = OfferLead.objects.filter(email=self.request.user.email).first()
            if lead:
                lead.user = self.request.user
                lead.save(update_fields=['user'])
        is_customer = bool(
            lead and (
                lead.lifecycle_stage in ('customer', 'enrolled') or
                lead.application_submitted_at or
                lead.contract_status != 'none'
            )
        )
        context.update({
            'lead': lead,
            'favorite_offers': lead.favorite_offers.all() if lead else [],
            'application_url': settings.APPLICATION_FORM_URL,
            'is_customer': is_customer,
            'is_enrolled': bool(
                lead and (
                    lead.lifecycle_stage == 'enrolled' or lead.contract_status == 'signed'
                )
            ),
        })
        return context


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
