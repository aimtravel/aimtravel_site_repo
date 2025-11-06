from django.urls import path

from aimtravel_site.posting.views import *

urlpatterns = (
    path('news/', NewsView.as_view(), name='news'),
    path('news/<slug:slug>/', NewsDetailView.as_view(), name='news_detail'),
    path('story/', StoryView.as_view(), name='story'),
)
