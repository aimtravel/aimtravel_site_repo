from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic as views
from django_filters import views as filter_views

from aimtravel_site.user_profile.models import Employee
from aimtravel_site.web.filters import OfferFilter
from aimtravel_site.web.forms import JobOfferDetailForm, CompanyDetailForm, CompanyEditForm, PriceDetailForm, \
    ServiceDetailForm
from aimtravel_site.web.models import JobOffer, Prices, AdditionalServices, Company

UserModel = get_user_model()


# START - - - GENERIC VIEWS

def index(request):
    return render(request, template_name='index.html')


def contacts(request):
    return render(request, template_name='about_us/contact_us.html')


def admin_panel(request):
    return render(request, template_name='admin_panel.html')


def error_404(request, exception):
    return render(request, '404.html')

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


# END - - - STATIC VIEWS


class CreateOfferView(LoginRequiredMixin, UserPassesTestMixin, views.CreateView):
    fields = '__all__'
    model = JobOffer
    template_name = 'job_offer/add_offer.html'
    success_url = reverse_lazy('offers')

    def test_func(self):
        return self.request.user.is_staff


class DisplayOfferView(views.ListView):
    model = JobOffer
    template_name = 'job_offer/offers.html'
    context_object_name = 'offer_list'
    paginate_by = 4
    ordering = ('-ranking', '-wage',)


class DisplayFilterOfferView(filter_views.FilterView):
    filterset_class = OfferFilter
    template_name = 'job_offer/offer_filter.html'



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


class OfferViewIndex(views.ListView):
    model = JobOffer
    template_name = 'index.html'
    context_object_name = 'offer_list'
    paginate_by = 4
    ordering = ('-ranking', '-wage',)
