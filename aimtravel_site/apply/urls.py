from django.urls import path

from . import views

app_name = "apply"

urlpatterns = [
    path("applications", views.ApplicationCreateView.as_view(), name="application-create"),
    path("applications/draft", views.DraftView.as_view(), name="application-draft"),
    path("lookup/<str:kind>", views.LookupView.as_view(), name="lookup"),
    path("apply/config", views.ConfigView.as_view(), name="config"),
    path("contracts/<uuid:public_id>/<str:token>/",
         views.ContractDownloadView.as_view(), name="contract-download"),
]
