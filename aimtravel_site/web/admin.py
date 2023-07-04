from django.contrib import admin

from aimtravel_site.web.models import JobOffer, Prices, AdditionalServices, Company


# Register your models here.
@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ['job_position', 'employer_name', 'wage', 'city', 'state']
    list_filter = ['state']


@admin.register(Prices)
class PricesAdmin(admin.ModelAdmin):
    list_display = ['pricing_type', 'price']
    list_filter = ['pricing_type']


@admin.register(AdditionalServices)
class AdditionalServicesAdmin(admin.ModelAdmin):
    list_display = ['service_type', 'service_price']
    list_filter = ['service_price']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['employer_name', 'employer_city', 'employer_state']
    list_filter = ['employer_name']