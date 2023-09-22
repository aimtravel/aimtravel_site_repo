from django.shortcuts import get_object_or_404
from django.views import generic as views

from aimtravel_site.posting.models import *


# Create your views here.
class NewsView(views.ListView):
    model = News
    template_name = 'nav/news.html'
    context_object_name = 'news'
    paginate_by = 4
    ordering = ('-date',)


class StoryView(views.ListView):
    model = MainFeedback
    template_name = 'nav/students-story.html'
    context_object_name = 'story'
    paginate_by = 4
    ordering = ('-id',)
