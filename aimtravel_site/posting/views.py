from django.shortcuts import get_object_or_404
from django.views import generic as views

from aimtravel_site.posting.models import News


# Create your views here.
class NewsView(views.ListView):
    model = News
    template_name = 'nav/news.html'
    context_object_name = 'news'
    paginate_by = 4
    ordering = ('-date',)
