"""Job offer listing, filtering and detail.

Behavioural change from ``web.views.JobOfferListView``: that view stored the
selected filters in the **session**, so the visible result set depended on
hidden server-side state and could not be linked or bookmarked. Here the
filters are ordinary query parameters, which makes the endpoint stateless,
cacheable and shareable. The frontend keeps them in the URL.
"""
from typing import List, Optional

from django.shortcuts import get_object_or_404
from ninja import Query, Router

from aimtravel_site.api import schemas
from aimtravel_site.api.pagination import paginate
from aimtravel_site.web.models import JobOffer

router = Router()

# Preserved verbatim from JobOfferListView so the default order of the board
# does not change under the rebuild.
OFFER_ORDERING = (
    '-ranking',
    '-last_seats',
    '-new_offer',
    '-wage',
    'job_position',
    'sold_out_offer',
)

SORT_OPTIONS = {
    'new': ('-new_offer',),
    'decrease_wage': ('-wage',),
    'increase_wage': ('wage',),
    'last_offer': ('-last_seats',),
    'popular': ('-ranking',),
}

OFFERS_PER_PAGE = 12


@router.get('/offers', response=schemas.JobOfferPageOut, url_name='offers')
def list_offers(
    request,
    state: Optional[List[str]] = Query(None),
    city: Optional[List[str]] = Query(None),
    job_position: Optional[List[str]] = Query(None),
    suitable_for: Optional[List[str]] = Query(None),
    wage: Optional[List[float]] = Query(None),
    housing: Optional[List[str]] = Query(None),
    sort_by: Optional[str] = None,
    page: int = 1,
):
    offers = JobOffer.objects.select_related('city')

    if state:
        offers = offers.filter(city__state__in=state)
    if city:
        # City is a FK with to_field='name', so the column holds city names.
        offers = offers.filter(city__in=city)
    if job_position:
        offers = offers.filter(job_position__in=job_position)
    if suitable_for:
        offers = offers.filter(suitable_for__in=suitable_for)
    if wage:
        offers = offers.filter(wage__in=wage)
    if housing:
        offers = offers.filter(housing__in=housing)

    offers = offers.order_by(*SORT_OPTIONS.get(sort_by, OFFER_ORDERING))

    return paginate(
        offers, page, OFFERS_PER_PAGE, schemas.JobOfferOut.from_model
    )


@router.get('/offers/filters', response=schemas.OfferFiltersOut)
def offer_filters(request):
    """Distinct values available in each filter, for building the filter panel.

    Nulls are stripped so the UI never renders an empty checkbox.
    """

    def distinct(field):
        values = JobOffer.objects.values_list(field, flat=True).distinct()
        return sorted(v for v in values if v not in (None, ''))

    return schemas.OfferFiltersOut(
        states=distinct('city__state'),
        cities=distinct('city'),
        job_positions=distinct('job_position'),
        suitable_for=distinct('suitable_for'),
        wages=distinct('wage'),
        housing=distinct('housing'),
        sort_options=sorted(SORT_OPTIONS),
    )


@router.get('/offers/{int:offer_id}', response=schemas.JobOfferDetailOut)
def offer_detail(request, offer_id: int):
    offer = get_object_or_404(
        JobOffer.objects.select_related('city', 'feedback'), pk=offer_id
    )
    return schemas.JobOfferDetailOut.from_model(offer)
