from django.urls import path

from aimtravel_site.posting.views import *

urlpatterns = (
    path('news/', NewsView.as_view(), name='news'),
    path('story/', StoryView.as_view(), name='story'),
)
