"""Shared pagination envelope for list endpoints."""
from django.core.paginator import Paginator

from aimtravel_site.api.schemas import Page


def paginate(queryset, page_number, per_page, build_item):
    """Page ``queryset`` and serialise each row with ``build_item``.

    Mirrors the behaviour of Django's ``Paginator.get_page``, which clamps
    out-of-range and non-numeric page numbers instead of raising.
    """
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)
    return {
        'items': [build_item(obj) for obj in page_obj],
        'page': Page(
            count=paginator.count,
            page=page_obj.number,
            num_pages=paginator.num_pages,
            has_next=page_obj.has_next(),
            has_previous=page_obj.has_previous(),
        ),
    }
