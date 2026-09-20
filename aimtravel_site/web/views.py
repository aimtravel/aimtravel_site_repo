from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic as views

from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.utils.encoding import smart_str

from aimtravel_site.posting.models import *
from aimtravel_site.user_profile.models import Employee
from aimtravel_site.web.forms import JobOfferDetailForm, CompanyDetailForm, CompanyEditForm, PriceDetailForm, \
    ServiceDetailForm
from aimtravel_site.web.models import *
from aimtravel_site.main_page.models import *

UserModel = get_user_model()


# START - - - GENERIC VIEWS


# class CombinedView(views.ListView):
#     template_name = 'index.html'
#     context_object_name = 'combined_data'
#     paginate_by = 4
#
#     def get_last_news(self):
#         return News.objects.latest('date')
#
#     def get_main_feedback(self):
#         return MainFeedback.objects.order_by('-id')[:3]
#
#     def get_videos(self):
#         return Video.objects.latest('id')
#
#     def get_prices(self):
#         return Prices.objects.latest('id')
#
#     def get_about(self):
#         return AboutSection.objects.latest('id')
#
#     def get(self, request):
#         page_number = self.request.GET.get('page')
#         offer_queryset = JobOffer.objects.order_by('sold_out_offer', '-new_offer', '-ranking', '-wage')
#         offer_paginator = Paginator(offer_queryset, self.paginate_by)
#         offer_page = offer_paginator.get_page(page_number)
#
#         # Get the first 4 News items
#         news_queryset = News.objects.order_by('-date')[:4]
#
#         last_news_item = self.get_last_news()
#         main_feedback = self.get_main_feedback()
#         video = self.get_videos()
#         prices = self.get_prices()
#         about = self.get_about()
#
#         context = {
#             'about': about,
#             'offer_list': offer_page,
#             'last_4_news': news_queryset,
#             'very_last_news': last_news_item,
#             'main_feedback': main_feedback,
#             'video': video,
#             'prices': prices,
#         }
#
#         return render(request, self.template_name, context)


class WatUsaView(views.ListView):
    template_name = 'nav/wat-usa.html'
    context_object_name = 'wat_usa_data'

    def get_queryset(self):
        faq = Faq.objects.all()
        return faq

    def get_price(self):
        return Prices.objects.latest('id')

    def get_faq(self):
        return Faq.objects.all()

    def get_main_feedback(self):
        return MainFeedback.objects.order_by('-id')[:3]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        faq = self.get_faq()
        main_feedback = self.get_main_feedback()
        prices = self.get_price()

        context = {
            'faq': faq,
            'main_feedback': main_feedback,
            'prices': prices,
        }

        return context


class InternshipView(views.ListView):
    template_name = 'nav/internship.html'
    context_object_name = 'internship'

    def get_queryset(self):
        faq = Faq.objects.all()
        return faq

    def get_faq(self):
        return Faq.objects.all()

    def get_main_feedback(self):
        return MainFeedback.objects.order_by('-id')[:3]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        faq = self.get_faq()
        main_feedback = self.get_main_feedback()

        context = {
            'faq': faq,
            'main_feedback': main_feedback,
        }

        return context


class H2BView(views.ListView):
    template_name = 'nav/h2b-for-non-students.html'
    context_object_name = 'h2b'

    def get_queryset(self):
        faq = Faq.objects.all()
        return faq

    def get_faq(self):
        return Faq.objects.all()

    def get_main_feedback(self):
        return MainFeedback.objects.order_by('-id')[:3]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        faq = self.get_faq()
        main_feedback = self.get_main_feedback()

        context = {
            'faq': faq,
            'main_feedback': main_feedback,
        }

        return context


def contacts(request):
    return render(request, template_name='nav/contacts.html')


def admin_panel(request):
    return render(request, template_name='admin_panel.html')


def error_404(request, exception):
    return render(request, '404.html')


def error_500(request):
    return render(request, '404.html', status=500)


def under_construction(request):
    return render(request, 'under_construction.html')


# END - - - GENERIC VIEWS


# START - - - STATIC VIEWS

def why_usa_tab(request):
    return render(request, template_name='nav/wat_usa/why_usa.html')


def who_tab(request):
    return render(request, template_name='nav/wat_usa/who.html')


def how_tab(request):
    return render(request, template_name='nav/wat_usa/how.html')


def price_tab(request):
    return render(request, template_name='nav/wat_usa/price.html')


def needed_docs(request):
    return render(request, template_name='nav/wat_usa/needed_docs.html')


def online(request):
    return render(request, template_name='nav/online-services.html')


# END - - - STATIC VIEWS


class CreateOfferView(LoginRequiredMixin, UserPassesTestMixin, views.CreateView):
    fields = '__all__'
    model = JobOffer
    template_name = 'job_offer/add_offer.html'
    success_url = reverse_lazy('offers')

    def test_func(self):
        return self.request.user.is_staff


class JobOfferListView(views.ListView):
    template_name = 'job_offer/offers.html'

    POSITION_GROUPS = (
        ('restaurant', 'Ресторант и обслужване', (
            'server', 'busser', 'runner', 'host', 'bartender', 'banquet',
            'food and beverage', 'food concession', 'restaurant', 'breakfast',
        )),
        ('kitchen', 'Кухня и приготвяне на храна', (
            'cook', 'kitchen', 'chocolatier', 'meat', 'deli', 'seafood',
        )),
        ('hotel', 'Хотел и обслужване на гости', (
            'front desk', 'guest service', 'bellperson', 'resort worker', 'clubhouse',
        )),
        ('housekeeping', 'Housekeeping и перално', (
            'housekeep', 'laundry', 'room attendant', 'houseperson',
            'public area', 'general cleaner',
        )),
        ('lifeguard', 'Спасители, басейн и плаж', (
            'lifeguard', 'pool', 'beach', 'ocean',
        )),
        ('retail', 'Продажби и обслужване на клиенти', (
            'retail', 'cashier', 'customer service',
        )),
        ('maintenance', 'Поддръжка и озеленяване', (
            'maintenance', 'grounds', 'engineering',
        )),
        ('activities', 'Забавления и общ персонал', (
            'activities', 'rentals', 'amusement', 'crew member',
            'team member', 'general staff',
        )),
    )

    @staticmethod
    def compact_wage(value):
        if value is None:
            return ''
        return ('%.2f' % float(value)).rstrip('0').rstrip('.')

    def get(self, request):
        student_mode = request.user.is_authenticated
        public_session_keys = {
            'state': 'selected_state', 'city': 'selected_city',
            'job_position': 'selected_job_position',
            'suitable_for': 'selected_suitable_for',
            'min_wage': 'selected_min_wage', 'max_wage': 'selected_max_wage',
            'tips_only': 'selected_tips_only', 'housing': 'selected_housing',
            'q': 'offer_search',
        }
        private_session_keys = {
            'sponsor': 'selected_sponsor',
            'assignment': 'selected_assignment',
            'availability': 'selected_availability',
        }
        session_keys = dict(public_session_keys)
        if student_mode:
            session_keys.update(private_session_keys)
        if 'clear_filter' in request.GET:
            for session_key in tuple(public_session_keys.values()) + tuple(private_session_keys.values()):
                request.session.pop(session_key, None)
            return redirect(f"{reverse('offers')}#offers-page-top-row")

        filter_submission = (
            any(key in request.GET for key in session_keys) or
            'sort_by' in request.GET
        )
        selected = {}
        for query_key, session_key in session_keys.items():
            if query_key in request.GET:
                value = request.GET.get(query_key, '').strip()
                request.session[session_key] = value
            elif filter_submission:
                value = ''
                request.session[session_key] = ''
            else:
                value = request.session.get(session_key, '')
            selected[query_key] = value

        sort_by = request.GET.get('sort_by') or 'popular'
        offers = JobOffer.objects.select_related('city').all()
        wage_stats = JobOffer.objects.aggregate(minimum=Min('wage'), maximum=Max('wage'))
        wage_min = self.compact_wage(wage_stats['minimum'] or 0)
        wage_max = self.compact_wage(wage_stats['maximum'] or 0)

        if selected['q']:
            offers = offers.filter(
                Q(job_position__icontains=selected['q']) |
                Q(employer_name__icontains=selected['q']) |
                Q(city__name__icontains=selected['q']) |
                Q(city__state__icontains=selected['q'])
            )
        if selected['state']:
            offers = offers.filter(city__state=selected['state'])
        if selected['city']:
            offers = offers.filter(city__name=selected['city'])
        if selected['job_position']:
            terms = dict((key, words) for key, label, words in self.POSITION_GROUPS).get(
                selected['job_position']
            )
            if terms:
                position_query = Q()
                for term in terms:
                    position_query |= Q(job_position__icontains=term)
                offers = offers.filter(position_query)
            else:
                offers = offers.filter(job_position=selected['job_position'])
        if selected['suitable_for']:
            offers = offers.filter(suitable_for=selected['suitable_for'])
        if selected['min_wage']:
            try:
                offers = offers.filter(wage__gte=float(selected['min_wage']))
            except (TypeError, ValueError):
                selected['min_wage'] = ''
        if selected['max_wage']:
            try:
                offers = offers.filter(wage__lte=float(selected['max_wage']))
            except (TypeError, ValueError):
                selected['max_wage'] = ''
        if selected['tips_only'] == '1':
            offers = offers.filter(tips__iexact='Да')
        if selected['housing']:
            offers = offers.filter(housing=selected['housing'])
        if student_mode:
            if selected['sponsor']:
                offers = offers.filter(sponsor=selected['sponsor'])
            if selected['assignment'] == '1':
                offers = offers.filter(assignment=True)
            if selected['availability'] == 'active':
                offers = offers.filter(
                    Q(availability_status='available') |
                    Q(availability_status='last_seats')
                )
            elif selected['availability']:
                offers = offers.filter(availability_status=selected['availability'])

        ordering = {
            'new': ('-new_offer', '-ranking', '-wage'),
            'decrease_wage': ('-wage', '-ranking'),
            'increase_wage': ('wage', '-ranking'),
            'last_offer': ('-last_seats', '-ranking', '-wage'),
            'popular': ('sold_out_offer', '-ranking', '-last_seats', '-new_offer', '-wage'),
        }
        offers = offers.order_by(*ordering.get(sort_by, ordering['popular']))

        states = JobOffer.objects.exclude(city__state__isnull=True).values_list(
            'city__state', flat=True
        ).distinct().order_by('city__state')
        cities = City.objects.filter(joboffer__isnull=False).distinct().order_by('name')
        position_groups = tuple((key, label) for key, label, terms in self.POSITION_GROUPS)
        position_labels = dict(position_groups)
        suitable_for = JobOffer.objects.exclude(suitable_for__isnull=True).exclude(
            suitable_for=''
        ).values_list('suitable_for', flat=True).distinct().order_by('suitable_for')
        housing = JobOffer.objects.exclude(housing__isnull=True).exclude(
            housing=''
        ).exclude(
            housing__in=('', '-', '$', '0', 'N/A', 'Не')
        ).values_list('housing', flat=True).distinct().order_by('housing')

        paginator = Paginator(offers, 12)
        page_obj = paginator.get_page(request.GET.get('page'))
        query_params = request.GET.copy()
        query_params.pop('page', None)
        query_params.pop('clear_filter', None)
        page_query = query_params.urlencode()

        labels = {
            'state': 'Щат', 'city': 'Град', 'job_position': 'Категория',
            'suitable_for': 'Подходящо за', 'min_wage': 'Минимум',
            'max_wage': 'Максимум', 'tips_only': 'Бакшиш',
            'housing': 'Настаняване', 'q': 'Търсене',
            'sponsor': 'Спонсор', 'assignment': 'Assignment',
            'availability': 'Наличност',
        }
        availability_labels = dict((key, label) for key, label in JobOffer.AVAILABILITY_CHOICES)
        availability_labels['active'] = 'Само активни'
        active_filters = []
        for key, value in selected.items():
            if not value:
                continue
            if key in ('min_wage', 'max_wage'):
                display_value = '$' + self.compact_wage(value)
            elif key == 'tips_only':
                display_value = 'Само с бакшиш'
            elif key == 'job_position':
                display_value = position_labels.get(value, value)
            elif key == 'assignment':
                display_value = 'Само assignments'
            elif key == 'availability':
                display_value = availability_labels.get(value, value)
            else:
                display_value = value
            active_filters.append({
                'param': key, 'label': labels[key], 'value': display_value,
            })

        context = {
            'states': states, 'cities': cities, 'position_groups': position_groups,
            'suitable_for': suitable_for, 'housing': housing,
            'page_obj': page_obj, 'result_count': paginator.count,
            'active_filters': active_filters,
            'page_query_prefix': (page_query + '&') if page_query else '',
            'selected_state': selected['state'],
            'selected_city': selected['city'],
            'selected_job_position': selected['job_position'],
            'selected_suitable_for': selected['suitable_for'],
            'selected_min_wage': selected['min_wage'] or wage_min,
            'selected_max_wage': selected['max_wage'] or wage_max,
            'selected_tips_only': selected['tips_only'],
            'selected_housing': selected['housing'],
            'wage_min': wage_min, 'wage_max': wage_max,
            'offer_search': selected['q'], 'sort_by': sort_by,
            'student_mode': student_mode,
            'sponsors': JobOffer.SPONSOR_CHOICES,
            'availability_choices': JobOffer.AVAILABILITY_CHOICES,
            'selected_sponsor': selected.get('sponsor', ''),
            'selected_assignment': selected.get('assignment', ''),
            'selected_availability': selected.get('availability', ''),
        }
        return render(request, self.template_name, context)

    def get_success_url(self):
        return '/rabotnioferti#offers-page-top-row'


class DetailsOfferView(views.DetailView):
    model = JobOffer
    template_name = 'job_offer/details_offer.html'
    form_class = JobOfferDetailForm
    context_object_name = 'offer_details'


class EditOfferView(LoginRequiredMixin, UserPassesTestMixin, views.UpdateView):
    model = JobOffer
    fields = '__all__'
    template_name = 'job_offer/edit_offer.html'
    context_object_name = 'edit_offer'

    def get_success_url(self):
        offer_pk = self.kwargs['pk']
        return reverse_lazy('details offer', kwargs={'pk': offer_pk})

    def test_func(self):
        return self.request.user.is_staff


class DeleteOfferView(LoginRequiredMixin, UserPassesTestMixin, views.DeleteView):
    model = JobOffer
    template_name = 'job_offer/delete_offer.html'
    context_object_name = 'delete_offer'
    template_name_suffix = '_confirm_delete'
    success_url = reverse_lazy('offers')

    def test_func(self):
        return self.request.user.is_staff


# PRICING SECTION


class CreatePriceView(LoginRequiredMixin, UserPassesTestMixin, views.CreateView):
    fields = '__all__'
    model = Prices
    template_name = 'price/add_price.html'
    success_url = reverse_lazy('prices')

    def test_func(self):
        return self.request.user.is_superuser


class DisplayPricesView(views.ListView):
    model = Prices
    ordering = ['price']
    template_name = 'price/prices.html'
    context_object_name = 'prices_list'


class EditPriceView(LoginRequiredMixin, UserPassesTestMixin, views.UpdateView):
    model = Prices
    fields = '__all__'
    template_name = 'price/edit_price.html'
    context_object_name = 'edit_price'

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        price_pk = self.kwargs['pk']
        return reverse_lazy('details price', kwargs={'pk': price_pk})


class DetailsPriceView(views.DetailView):
    model = Prices
    template_name = 'price/details_price.html'
    form_class = PriceDetailForm
    context_object_name = 'price_details'


class DeletePriceView(LoginRequiredMixin, UserPassesTestMixin, views.DeleteView):
    model = Prices
    template_name = 'price/delete_price.html'
    context_object_name = 'delete_price'
    template_name_suffix = '_confirm_delete'
    success_url = reverse_lazy('prices')

    def test_func(self):
        return self.request.user.is_superuser


# SERVICES SECTION


class CreateServiceView(LoginRequiredMixin, UserPassesTestMixin, views.CreateView):
    fields = '__all__'
    model = AdditionalServices
    template_name = 'additional_services/add_service.html'
    success_url = reverse_lazy('services')

    def test_func(self):
        return self.request.user.is_staff


class DisplayAdditionalServicesView(views.ListView):
    model = AdditionalServices
    template_name = 'additional_services/additional_services.html'
    context_object_name = 'services_list'
    ordering = 'pk'


class EditServiceView(LoginRequiredMixin, UserPassesTestMixin, views.UpdateView):
    model = AdditionalServices
    fields = '__all__'
    template_name = 'additional_services/edit_service.html'
    context_object_name = 'edit_service'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        service_pk = self.kwargs['pk']
        return reverse_lazy('details service', kwargs={'pk': service_pk})


class DetailsServiceView(views.DetailView):
    model = AdditionalServices
    template_name = 'additional_services/details_service.html'
    form_class = ServiceDetailForm
    context_object_name = 'service_details'


class DeleteServiceView(LoginRequiredMixin, UserPassesTestMixin, views.DeleteView):
    model = AdditionalServices
    template_name = 'additional_services/delete_service.html'
    context_object_name = 'delete_service'
    template_name_suffix = '_confirm_delete'
    success_url = reverse_lazy('services')

    def test_func(self):
        return self.request.user.is_staff


class AllEmployeeView(views.ListView):
    model = Employee
    template_name = 'about_us/about.html'
    context_object_name = 'employee_list'
    ordering = 'user'


# EMPLOYER`s SECTION


class CreateCompanyView(LoginRequiredMixin, UserPassesTestMixin, views.CreateView):
    fields = '__all__'
    model = Company
    template_name = 'employer/add_employer.html'
    success_url = reverse_lazy('employers')

    def test_func(self):
        return self.request.user.is_staff


class CompanyDetailView(views.DetailView):
    model = Company
    template_name = 'employer/details_employer.html'
    form_class = CompanyDetailForm
    context_object_name = 'employer_details'


class AllCompanyView(views.ListView):
    model = Company
    template_name = 'employer/view_all.html'
    context_object_name = 'employers'
    paginate_by = 4
    ordering = 'employer_name'


class EditCompanyView(LoginRequiredMixin, UserPassesTestMixin, views.UpdateView):
    model = Company
    template_name = 'employer/edit_employer.html'
    context_object_name = 'edit_employer'
    form_class = CompanyEditForm

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        emp_pk = self.kwargs['pk']
        return reverse_lazy('employer details', kwargs={'pk': emp_pk})


class DeleteCompanyView(LoginRequiredMixin, UserPassesTestMixin, views.DeleteView):
    model = Company
    template_name = 'employer/delete_employer.html'
    context_object_name = 'delete_company'
    template_name_suffix = '_confirm_delete'
    success_url = reverse_lazy('employers')

    def test_func(self):
        return self.request.user.is_staff


# FUNCTIONAL VIEWS

@require_POST
def form_submission_view(request):
    name = request.POST.get('name')
    university = request.POST.get('university')
    email = request.POST.get('email-field')
    phone = request.POST.get('phone-field')

    message = request.POST.get('message')

    subject = f"HIGH PRIORITY!!! - {name} - Запитване за студентска бригада"
    mail_message = f"Име и Фамилия: {name}\nУниверситет: {university}\nEmail: {email}\nТелефон: {phone}\n\nЗапитване: {message}"
    encoded_message = smart_str(mail_message, encoding='utf-8')
    send_mail(subject, encoded_message, email, ['studentski@aimtravel.bg'], fail_silently=False)

    return render(request, 'success.html')
