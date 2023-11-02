from django.contrib import admin

from aimtravel_site.web.models import JobOffer, Prices, AdditionalServices, Company, City, Feedback


def duplicate_selected(modeladmin, request, queryset):
    for obj in queryset:
        obj.pk = None  # Set the primary key to None to create a new instance
        obj.save()


duplicate_selected.short_description = "Duplicate selected entries"


# Register your models here.
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['feedback_name', 'student_name_1', 'student_name_2', 'student_name_3']
    list_filter = ['feedback_name']
    search_fields = ['feedback_name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'fact1', 'fact2', 'fact3', 'city_pic']
    list_filter = ['name', 'state']
    search_fields = ['name', 'state']
    sortable_by = ['name', 'state']


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    actions = [duplicate_selected]
    list_display = ['job_position', 'employer_name', 'wage', 'city', 'ranking']
    list_filter = ['new_offer', 'sold_out_offer', 'city', 'ranking']
    search_fields = ['job_position', 'employer_name', 'wage', 'city', 'ranking']
    sortable_by = ['job_position', 'employer_name', 'wage', 'city', 'ranking']


@admin.register(Prices)
class PricesAdmin(admin.ModelAdmin):
    list_filter = ['actual_self_arrange']


@admin.register(AdditionalServices)
class AdditionalServicesAdmin(admin.ModelAdmin):
    list_display = ['service_type', 'service_price']
    list_filter = ['service_price']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['employer_name', 'employer_city', 'employer_state']
    list_filter = ['employer_name']



