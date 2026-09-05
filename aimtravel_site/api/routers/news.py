"""News and student stories."""
from django.shortcuts import get_object_or_404
from ninja import Router

from aimtravel_site.api import schemas
from aimtravel_site.api.pagination import paginate
from aimtravel_site.posting.models import MainFeedback, News

router = Router()

NEWS_PER_PAGE = 12


@router.get('/news', response=schemas.NewsPageOut, url_name='news')
def list_news(request, page: int = 1):
    news = News.objects.order_by('-date')
    return paginate(news, page, NEWS_PER_PAGE, schemas.NewsListOut.from_model)


@router.get('/news/{slug}', response=schemas.NewsDetailOut)
def news_detail(request, slug: str):
    item = get_object_or_404(News, slug=slug)
    return schemas.NewsDetailOut.from_model(item)


@router.get('/stories', response=list[schemas.StoryOut], url_name='stories')
def list_stories(request):
    stories = MainFeedback.objects.order_by('-id')
    return [schemas.StoryOut.from_model(s) for s in stories]
