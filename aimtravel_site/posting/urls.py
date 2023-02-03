from django.urls import path

from aimtravel_site.posting.views import NewsView

urlpatterns = (
    path('news/', NewsView.as_view(), name='news'),
)
