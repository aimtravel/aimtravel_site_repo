from django.contrib import admin

from aimtravel_site.user_profile.models import Students, Employee


@admin.register(Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'bg_personal_number', 'university']
    list_filter = ['university']
    sortable_by = ['university', 'first_name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_role', 'employee_first_name', 'employee_last_name']
    list_filter = ['employee_role']
