from django.contrib import admin

from aimtravel_site.taxes.models import Taxes


# Register your models here.
@admin.register(Taxes)
class TaxesAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'family_name', 'phone_number']
    list_filter = ['user', 'first_name', 'family_name', 'working_year']
    sortable_by = ['user', 'working_year', 'first_name']
    # form = TaxesAdminForm
