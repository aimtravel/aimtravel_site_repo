from django.urls import path
from aimtravel_site.main_page.views import *


urlpatterns = (
    path('', CombinedView.as_view(), name='index'),
)
