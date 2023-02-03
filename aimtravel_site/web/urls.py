from django.urls import path, include

from aimtravel_site.web.views import *

urlpatterns = (
    path('', OfferViewIndex.as_view(), name='index'),
    path('contacts/', contacts, name='contacts'),
    path('admin_panel/', admin_panel, name='admin panel'),
    path('wat_usa/', include([
        path('why_usa/', why_usa_tab, name='why usa'),
        path('who/', who_tab, name='who'),
        path('how/', how_tab, name='how'),
        path('price/', price_tab, name='price'),
        path('needed_docs', needed_docs, name='needed documents'),
    ])),
    path('taxes/', taxes, name='taxes'),
    path('offer/', include([
        path('add/', CreateOfferView.as_view(), name='add offer'),
        path('all/', DisplayOfferView.as_view(), name='offers'),
        path('all_filter/', DisplayFilterOfferView.as_view(), name='offers_filter'),
        path('edit/<int:pk>/', EditOfferView.as_view(), name='edit offer'),
        path('delete/<int:pk>/', DeleteOfferView.as_view(), name='delete offer'),
        path('details/<int:pk>/', DetailsOfferView.as_view(), name='details offer'),
    ])),
    path('prices/', include([
        path('add/', CreatePriceView.as_view(), name='add price'),
        path('all/', DisplayPricesView.as_view(), name='prices'),
        path('edit/<int:pk>/', EditPriceView.as_view(), name='edit price'),
        path('delete/<int:pk>/', DeletePriceView.as_view(), name='delete price'),
        path('details/<int:pk>/', DetailsPriceView.as_view(), name='details price'),
    ])),
    path('services/', include([
        path('all/', DisplayAdditionalServicesView.as_view(), name='services'),
        path('add/', CreateServiceView.as_view(), name='add service'),
        path('edit/<int:pk>/', EditServiceView.as_view(), name='edit service'),
        path('delete/<int:pk>/', DeleteServiceView.as_view(), name='delete service'),
        path('details/<int:pk>/', DetailsServiceView.as_view(), name='details service'),
    ])),
    path('team/', AllEmployeeView.as_view(), name='team'),
    path('employer/', include([
        path('all/', AllCompanyView.as_view(), name='employers'),
        path('add/', CreateCompanyView.as_view(), name='add employer'),
        path('edit/<int:pk>/', EditCompanyView.as_view(), name='edit employer'),
        path('details/<int:pk>/', CompanyDetailView.as_view(), name='employer details'),
        path('delete/<int:pk>/', DeleteCompanyView.as_view(), name='delete employer'),
    ])),
)
