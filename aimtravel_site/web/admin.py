from django.contrib import admin

from aimtravel_site.web.models import JobOffer, Prices, AdditionalServices, Company, City, Feedback


# Register your models here.
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['feedback_name', 'student_name_1', 'student_name_2', 'student_name_3']
    list_filter = ['feedback_name']
    search_fields = ['feedback_name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'fact1', 'fact2', 'fact3', 'city_pic']
    list_filter = ['name']
    search_fields = ['name']
    sortable_by = ['name']


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ['job_position', 'employer_name', 'wage', 'city', 'state']
    list_filter = ['state']
    search_fields = ['job_position', 'employer_name', 'wage', 'city', 'state']
    sortable_by = ['job_position', 'employer_name', 'wage', 'city', 'state']


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