"""Homepage aggregate endpoint.

Replaces the context built by ``main_page.views.CombinedView``.
"""
from ninja import Router

from aimtravel_site.api import schemas
from aimtravel_site.api.routers.offers import OFFER_ORDERING
from aimtravel_site.main_page.models import (
    AboutSection,
    CallToActionSection,
    ForthSlider,
    MainPricingSection,
    MainServicesSection,
    MainSlider,
    SecondSlider,
    ThirdSlider,
    Video,
)
from aimtravel_site.posting.models import MainFeedback, News
from aimtravel_site.web.models import JobOffer, Prices

router = Router()

FEATURED_OFFER_COUNT = 4
LATEST_NEWS_COUNT = 4
STORY_COUNT = 3


def _latest(model):
    """Most recent row, or None.

    The legacy views used ``.latest('id')``, which raises ``DoesNotExist`` on an
    empty table and 500s the whole page. A section with no content should just
    be absent from the response instead.
    """
    return model.objects.order_by('-id').first()


@router.get('/home', response=schemas.HomeOut, url_name='home')
def home(request):
    offers = (
        JobOffer.objects.select_related('city')
        .order_by(*OFFER_ORDERING)[:FEATURED_OFFER_COUNT]
    )
    news = News.objects.order_by('-date')[:LATEST_NEWS_COUNT]
    stories = MainFeedback.objects.order_by('-id')[:STORY_COUNT]

    return schemas.HomeOut(
        main_slider=schemas.HeroSlide.from_main(_latest(MainSlider)),
        second_slider=schemas.HeroSlide.from_second(_latest(SecondSlider)),
        third_slider=schemas.HeroSlide.from_top_main(_latest(ThirdSlider)),
        forth_slider=schemas.HeroSlide.from_top_main(_latest(ForthSlider)),
        about=schemas.AboutSectionOut.from_model(_latest(AboutSection)),
        cta=schemas.BannerSectionOut.from_model(_latest(CallToActionSection)),
        pricing_banner=schemas.BannerSectionOut.from_model(
            _latest(MainPricingSection)
        ),
        services=schemas.ServicesSectionOut.from_model(
            _latest(MainServicesSection)
        ),
        videos=schemas.VideoSectionOut.from_model(_latest(Video)),
        prices=schemas.PricesOut.from_model(_latest(Prices)),
        featured_offers=[schemas.JobOfferOut.from_model(o) for o in offers],
        latest_news=[schemas.NewsListOut.from_model(n) for n in news],
        stories=[schemas.StoryOut.from_model(s) for s in stories],
    )
