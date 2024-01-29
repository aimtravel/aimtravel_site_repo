from django.urls import path

from aimtravel_site.taxes.views import *

urlpatterns = (
    path('', TaxMainView.as_view(), name='taxes'),
    path('all/', AdminTaxEntryListView.as_view(), name='all-taxes'),
    path('admin-edit-tax/<int:pk>/', SuperuserEditTaxView.as_view(), name='admin-edit-taxes'),
    path('admin-delete-tax/<int:pk>/', SuperuserDeleteTaxView.as_view(), name='admin-delete-taxes'),
    path('admin-export-tax/', ExportTaxesView.as_view(), name='admin-export-taxes'),

    path('pre-add-tax/', pre_add_tax, name='pre add tax'),
    path('add-tax/', AddTaxesView.as_view(), name='add tax'),
    path('edit-tax/<int:pk>/', EditTaxesView.as_view(), name='edit tax'),
    path('detail-tax/<int:pk>/', DetailsTaxView.as_view(), name='detail tax'),
    path('generate_pdf/<int:tax_id>/', generate_pdf, name='generate_pdf'),
)

from .signals import *
