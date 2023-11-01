from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator
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

UserModel = get_user_model()


# START - - - GENERIC VIEWS


class CombinedView(views.ListView):
    template_name = 'index.html'
    context_object_name = 'combined_data'
    paginate_by = 4

    def get_last_news(self):
        return News.objects.latest('date')

    def get_main_feedback(self):
        return MainFeedback.objects.order_by('-id')[:3]

    def get_videos(self):
        return Video.objects.latest('id')

    def get(self, request):
        page_number = self.request.GET.get('page')
        offer_queryset = JobOffer.objects.order_by('sold_out_offer', '-new_offer', '-ranking', '-wage')
        offer_paginator = Paginator(offer_queryset, self.paginate_by)
        offer_page = offer_paginator.get_page(page_number)

        # Get the first 4 News items
        news_queryset = News.objects.order_by('-date')[:4]

        last_news_item = self.get_last_news()
        main_feedback = self.get_main_feedback()
        video = self.get_videos()

        context = {
            'offer_list': offer_page,
            'last_4_news': news_queryset,
            'very_last_news': last_news_item,
            'main_feedback': main_feedback,
            'video': video,
        }

        return render(request, self.template_name, context)


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


def taxes(request):
    return render(request, template_name='nav/taxes.html')


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

    def get(self, request):
        # Retrieve the selected filter options from the session
        selected_state = request.session.get('selected_state', [])
        selected_city = request.session.get('selected_city', [])
        selected_job_position = request.session.get('selected_job_position', [])
        selected_suitable_for = request.session.get('selected_suitable_for', [])
        selected_wage = request.session.get('selected_wage', [])
        selected_housing = request.session.get('selected_housing', [])

        # Check if the "clear_filter" parameter is present in the request's GET parameters
        if 'clear_filter' in request.GET:
            # Remove filter options from the session
            request.session.pop('selected_state', None)
            request.session.pop('selected_city', None)
            request.session.pop('selected_job_position', None)
            request.session.pop('selected_suitable_for', None)
            request.session.pop('selected_wage', None)
            request.session.pop('selected_housing', None)

            # Redirect to the same page to clear the URL query parameters
            return redirect(request.path)

        states = JobOffer.objects.values_list('city__state', flat=True).distinct()
        cities = JobOffer.objects.values_list('city', flat=True).distinct()
        job_positions = JobOffer.objects.values_list('job_position', flat=True).distinct()
        suitable_for = JobOffer.objects.values_list('suitable_for', flat=True).distinct()
        wages = JobOffer.objects.values_list('wage', flat=True).distinct()
        housing = JobOffer.objects.values_list('housing', flat=True).distinct()

        states = sorted(states)
        cities = sorted(cities)
        job_positions = sorted(job_positions)
        suitable_for = sorted(suitable_for)
        wages = sorted(wages)
        housing = sorted(housing)

        filtered_offers = JobOffer.objects.all()
        filtered_offers = filtered_offers.order_by('sold_out_offer', '-new_offer', '-ranking', '-wage')

        # Check if the filter parameters are present in the request's GET parameters
        if 'state' in request.GET:
            selected_state = request.GET.getlist('state')
        if 'city' in request.GET:
            selected_city = request.GET.getlist('city')
        if 'job_position' in request.GET:
            selected_job_position = request.GET.getlist('job_position')
        if 'suitable_for' in request.GET:
            selected_suitable_for = request.GET.getlist('suitable_for')
        if 'wage' in request.GET:
            selected_wage = request.GET.getlist('wage')
        if 'housing' in request.GET:
            selected_housing = request.GET.getlist('housing')

        # selected_state = request.GET.getlist('state')
        # selected_city = request.GET.getlist('city')
        # selected_job_position = request.GET.getlist('job_position')
        # selected_suitable_for = request.GET.getlist('suitable_for')
        # selected_wage = request.GET.getlist('wage')
        # selected_housing = request.GET.getlist('housing')

        # Store the selected filter options in the session
        request.session['selected_state'] = selected_state
        request.session['selected_city'] = selected_city
        request.session['selected_job_position'] = selected_job_position
        request.session['selected_suitable_for'] = selected_suitable_for
        request.session['selected_wage'] = selected_wage
        request.session['selected_housing'] = selected_housing
        request.session.save()

        # Apply the selected filter options to the queryset
        if selected_state:
            filtered_offers = filtered_offers.filter(city__state__in=selected_state)
        if selected_city:
            filtered_offers = filtered_offers.filter(city__in=selected_city)
        if selected_job_position:
            filtered_offers = filtered_offers.filter(job_position__in=selected_job_position)
        if selected_suitable_for:
            filtered_offers = filtered_offers.filter(suitable_for__in=selected_suitable_for)
        if selected_wage:
            filtered_offers = filtered_offers.filter(wage__in=selected_wage)
        if selected_housing:
            filtered_offers = filtered_offers.filter(housing__in=selected_housing)

        paginator = Paginator(filtered_offers, 12)  # Display 12 offers per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # formatted_wages = list(map(lambda wage: f"${Decimal(wage):.2f}", wages))

        context = {
            'states': states,
            'cities': cities,
            'job_positions': job_positions,
            'suitable_for': suitable_for,
            'wages': wages,
            'housing': housing,
            'filtered_offers': filtered_offers,
            'page_obj': page_obj,
            'selected_state': selected_state,
            'selected_city': selected_city,
            'selected_job_position': selected_job_position,
            'selected_suitable_for': selected_suitable_for,
            'selected_wage': selected_wage,
            'selected_housing': selected_housing,
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

    return render(request, 'job_offer/success.html')
