from django.contrib import admin

from aimtravel_site.taxes.models import *


# Register your models here.
@admin.register(Taxes)
class TaxesAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'family_name', 'phone_number']
    list_filter = ['user', 'first_name', 'family_name', 'working_year']
    sortable_by = ['user', 'first_name', 'last_name', 'email']
    # form = TaxesAdminForm
