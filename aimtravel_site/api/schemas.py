"""Response schemas for the public JSON API.

These deliberately do *not* mirror the models one-to-one. Several of the legacy
models store repeated content in flat numbered columns (``title1``..``title6``,
``video_1``..``video_5``, ``student_name_1``..``student_name_3``) because the
Django templates rendered a fixed number of slots. The React components map over
lists instead, so the numbered columns are collapsed into arrays here, and empty
slots are dropped. That keeps the "how many slots exist" detail in one place
rather than spread across the frontend.

Likewise the ``'Да'/'Не'`` and ``'True'/'False'`` CharField flags are exposed as
real booleans, so the generated TypeScript types get ``boolean`` instead of
magic strings.
"""
from datetime import date
from typing import List, Optional

from ninja import Schema


# --- field helpers -------------------------------------------------------


def media_url(field) -> Optional[str]:
    """Relative URL of a File/ImageField, or None when it has no file.

    Relative is enough because the SPA is served from the same origin as
    Django. Accessing ``.url`` on an empty FieldFile raises, hence the guard.
    """
    if not field:
        return None
    try:
        return field.url
    except ValueError:
        return None


def yes_no(value: Optional[str]) -> Optional[bool]:
    """Map the Bulgarian ``YES_NO`` choices onto a real boolean."""
    if value == 'Да':
        return True
    if value == 'Не':
        return False
    return None


def true_false(value: Optional[str]) -> bool:
    """Map the ``TRUE_FALSE`` choices (stored as the strings 'True'/'False')."""
    return value == 'True'


def _pairs(instance, title_attr: str, content_attr: str, count: int) -> List[dict]:
    """Collect ``title1``/``content1``..``titleN``/``contentN`` into a list.

    Slots where both halves are empty are skipped, so an editor who fills in
    only three of the six service slots gets three cards rather than three
    blank ones.
    """
    items = []
    for i in range(1, count + 1):
        title = getattr(instance, f'{title_attr}{i}', None)
        content = getattr(instance, f'{content_attr}{i}', None)
        if title or content:
            items.append({'title': title, 'content': content})
    return items


# --- shared building blocks ---------------------------------------------


class CallToAction(Schema):
    text: Optional[str] = None
    link: Optional[str] = None


class TextItem(Schema):
    title: Optional[str] = None
    content: Optional[str] = None


class VideoItem(Schema):
    url: Optional[str] = None
    image: Optional[str] = None


# --- home page sections --------------------------------------------------


class HeroSlide(Schema):
    """The four homepage sliders, normalised onto one shape.

    The legacy models disagree on field names for the same visual roles:
    MainSlider/SecondSlider use ``title1``/``title2`` while Third/ForthSlider
    use ``top_title``/``main_title``, and which one is the *large* heading
    flips between them. This schema settles on eyebrow/heading/body.
    """
    eyebrow: Optional[str] = None
    heading: Optional[str] = None
    body: Optional[str] = None
    cta: CallToAction

    @classmethod
    def from_main(cls, obj) -> Optional['HeroSlide']:
        # MainSlider: title1 is the large heading, title2 the small one.
        if obj is None:
            return None
        return cls(
            eyebrow=obj.title2,
            heading=obj.title1,
            body=None,
            cta=CallToAction(text=obj.button_text, link=obj.button_link),
        )

    @classmethod
    def from_second(cls, obj) -> Optional['HeroSlide']:
        # SecondSlider: title1 is the *small* heading, title2 the large one.
        if obj is None:
            return None
        return cls(
            eyebrow=obj.title1,
            heading=obj.title2,
            body=obj.content1,
            cta=CallToAction(text=obj.button_text, link=obj.button_link),
        )

    @classmethod
    def from_top_main(cls, obj) -> Optional['HeroSlide']:
        # Third/ForthSlider share top_title/main_title/content1.
        if obj is None:
            return None
        return cls(
            eyebrow=obj.top_title,
            heading=obj.main_title,
            body=obj.content1,
            cta=CallToAction(text=obj.button_text, link=obj.button_link),
        )


class AboutSectionOut(Schema):
    title: Optional[str] = None
    paragraphs: List[str]
    cta: CallToAction

    @classmethod
    def from_model(cls, obj) -> Optional['AboutSectionOut']:
        if obj is None:
            return None
        return cls(
            title=obj.title,
            paragraphs=[p for p in (obj.content1, obj.content2) if p],
            cta=CallToAction(text=obj.button_text, link=obj.button_link),
        )


class BannerSectionOut(Schema):
    """Shared shape for the CTA and pricing banner sections.

    Both store three stacked headings plus a body and a button.
    """
    eyebrow: Optional[str] = None
    heading: Optional[str] = None
    subheading: Optional[str] = None
    body: Optional[str] = None
    cta: CallToAction

    @classmethod
    def from_model(cls, obj) -> Optional['BannerSectionOut']:
        if obj is None:
            return None
        return cls(
            eyebrow=obj.title1,
            heading=obj.title2,
            subheading=obj.title3,
            body=obj.content1,
            cta=CallToAction(text=obj.button_text, link=obj.button_link),
        )


class VideoSectionOut(Schema):
    main: Optional[VideoItem] = None
    items: List[VideoItem]
    cta: CallToAction

    @classmethod
    def from_model(cls, obj) -> Optional['VideoSectionOut']:
        if obj is None:
            return None
        items = []
        for i in range(1, 6):
            url = getattr(obj, f'video_{i}', None)
            image = media_url(getattr(obj, f'video_{i}_image', None))
            if url or image:
                items.append(VideoItem(url=url, image=image))
        main = None
        if obj.main_video or obj.main_video_image:
            main = VideoItem(
                url=obj.main_video,
                image=media_url(obj.main_video_image),
            )
        return cls(
            main=main,
            items=items,
            cta=CallToAction(text=obj.button_text, link=obj.button_link),
        )


class ServicesSectionOut(Schema):
    items: List[TextItem]

    @classmethod
    def from_model(cls, obj) -> Optional['ServicesSectionOut']:
        if obj is None:
            return None
        return cls(items=[TextItem(**p) for p in _pairs(obj, 'title', 'content', 6)])


# --- catalogue content ---------------------------------------------------


class CityOut(Schema):
    name: Optional[str] = None
    state: Optional[str] = None
    facts: List[str]
    picture: Optional[str] = None

    @classmethod
    def from_model(cls, obj) -> Optional['CityOut']:
        if obj is None:
            return None
        return cls(
            name=obj.name,
            state=obj.state,
            facts=[f for f in (obj.fact1, obj.fact2, obj.fact3) if f],
            picture=media_url(obj.city_pic),
        )


class StudentQuoteOut(Schema):
    name: Optional[str] = None
    picture: Optional[str] = None
    text: Optional[str] = None


class FeedbackOut(Schema):
    name: Optional[str] = None
    quotes: List[StudentQuoteOut]

    @classmethod
    def from_model(cls, obj) -> Optional['FeedbackOut']:
        if obj is None:
            return None
        quotes = []
        for i in range(1, 4):
            student = getattr(obj, f'student_name_{i}', None)
            text = getattr(obj, f'feedback_{i}', None)
            picture = media_url(getattr(obj, f'student_pic_{i}', None))
            if student or text or picture:
                quotes.append(
                    StudentQuoteOut(name=student, picture=picture, text=text)
                )
        return cls(name=obj.feedback_name, quotes=quotes)


class JobOfferOut(Schema):
    id: int
    employer_name: Optional[str] = None
    job_position: Optional[str] = None
    city: Optional[CityOut] = None
    wage: Optional[float] = None
    minimum_hours: Optional[float] = None
    housing: Optional[str] = None
    english_level: Optional[str] = None
    suitable_for: Optional[str] = None
    begin_date: Optional[date] = None
    end_date: Optional[date] = None
    picture: Optional[str] = None
    ranking: Optional[int] = None

    # YES_NO flags, exposed as booleans.
    tips: Optional[bool] = None
    bonus: Optional[bool] = None
    overtime: Optional[bool] = None
    groups: Optional[bool] = None
    couples: Optional[bool] = None

    # TRUE_FALSE badge flags.
    is_new: bool
    is_sold_out: bool
    has_last_seats: bool

    @classmethod
    def from_model(cls, obj) -> 'JobOfferOut':
        return cls(
            id=obj.id,
            employer_name=obj.employer_name,
            job_position=obj.job_position,
            city=CityOut.from_model(obj.city),
            wage=obj.wage,
            minimum_hours=obj.minimum_hours,
            housing=obj.housing,
            english_level=obj.english_level,
            suitable_for=obj.suitable_for,
            begin_date=obj.begin_date,
            end_date=obj.end_date,
            picture=media_url(obj.offer_pic),
            ranking=obj.ranking,
            tips=yes_no(obj.tips),
            bonus=yes_no(obj.bonus),
            overtime=yes_no(obj.overtime),
            groups=yes_no(obj.groups),
            couples=yes_no(obj.couples),
            is_new=true_false(obj.new_offer),
            is_sold_out=true_false(obj.sold_out_offer),
            has_last_seats=true_false(obj.last_seats),
        )


class JobOfferDetailOut(JobOfferOut):
    job_description: Optional[str] = None
    feedback: Optional[FeedbackOut] = None

    @classmethod
    def from_model(cls, obj) -> 'JobOfferDetailOut':
        base = JobOfferOut.from_model(obj).model_dump()
        return cls(
            **base,
            job_description=obj.job_description,
            feedback=FeedbackOut.from_model(obj.feedback),
        )


class PriceTier(Schema):
    actual: Optional[float] = None
    discounted: Optional[float] = None


class PricesOut(Schema):
    """The pricing table. ``actual_*`` is the list price, ``discounted_*`` the
    promotional one; the template rendered both with a strikethrough."""
    id: int
    self_arrange: PriceTier
    standard: PriceTier
    premium: PriceTier
    sevis: Optional[float] = None
    visa_interview: Optional[float] = None
    plane_ticket_lowest: Optional[float] = None
    plane_ticket_highest: Optional[float] = None
    sign_up_fees: Optional[float] = None
    amount_of_discount: Optional[int] = None
    valid_until: Optional[str] = None

    @classmethod
    def from_model(cls, obj) -> Optional['PricesOut']:
        if obj is None:
            return None
        day, month, year = (
            obj.validity_date_day,
            obj.validity_date_month,
            obj.validity_date_year,
        )
        valid_until = ' '.join(str(p) for p in (day, month, year) if p) or None
        return cls(
            id=obj.id,
            self_arrange=PriceTier(
                actual=obj.actual_self_arrange,
                discounted=obj.discounted_self_arrange,
            ),
            standard=PriceTier(
                actual=obj.actual_standard,
                discounted=obj.discounted_standard,
            ),
            premium=PriceTier(
                actual=obj.actual_premium,
                discounted=obj.discounted_premium,
            ),
            sevis=obj.sevis,
            visa_interview=obj.visa_interview,
            plane_ticket_lowest=obj.plane_ticket_lowest,
            plane_ticket_highest=obj.plane_ticket_highest,
            sign_up_fees=obj.sign_up_fees,
            amount_of_discount=obj.amount_of_discount,
            valid_until=valid_until,
        )


class AdditionalServiceOut(Schema):
    id: int
    service_type: Optional[str] = None
    service_description: Optional[str] = None
    service_price: Optional[float] = None


class CompanyOut(Schema):
    id: int
    employer_name: Optional[str] = None
    employer_city: Optional[str] = None
    employer_state: Optional[str] = None
    employer_history: Optional[str] = None
    employer_photo: Optional[str] = None


class EmployeeOut(Schema):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    @classmethod
    def from_model(cls, obj) -> 'EmployeeOut':
        return cls(
            id=obj.id,
            first_name=obj.employee_first_name,
            last_name=obj.employee_last_name,
            role=obj.employee_role,
            email=obj.employee_email,
            phone=obj.employee_phone,
        )


class CurrentUserOut(Schema):
    """Who the session cookie belongs to, or an anonymous marker."""
    is_authenticated: bool
    id: Optional[int] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_staff: bool = False
    is_superuser: bool = False
    picture: Optional[str] = None


class FaqOut(Schema):
    id: int
    question: Optional[str] = None
    answer: Optional[str] = None

    @classmethod
    def from_model(cls, obj) -> 'FaqOut':
        return cls(id=obj.id, question=obj.faq_title, answer=obj.faq_description)


# --- news / stories ------------------------------------------------------


class NewsListOut(Schema):
    """List view of a news item - no body, so index pages stay small."""
    id: int
    slug: str
    title: Optional[str] = None
    date: Optional[date] = None
    image: Optional[str] = None
    external_url: Optional[str] = None

    @classmethod
    def from_model(cls, obj) -> 'NewsListOut':
        return cls(
            id=obj.id,
            slug=obj.slug,
            title=obj.news_title,
            date=obj.date,
            image=media_url(obj.news_image),
            external_url=obj.news_url,
        )


class NewsDetailOut(NewsListOut):
    # CKEditor 5 output. Trusted (staff-authored) HTML - the React side renders
    # it via dangerouslySetInnerHTML, so it must stay staff-only to write.
    content_html: Optional[str] = None

    @classmethod
    def from_model(cls, obj) -> 'NewsDetailOut':
        return cls(
            **NewsListOut.from_model(obj).model_dump(),
            content_html=obj.news_content,
        )


class StoryOut(Schema):
    id: int
    title: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None

    @classmethod
    def from_model(cls, obj) -> 'StoryOut':
        return cls(
            id=obj.id,
            title=obj.feedback_1_title,
            content=obj.feedback_1_content,
            image=media_url(obj.feedback_1_image),
        )


# --- pagination ----------------------------------------------------------


class Page(Schema):
    """Pagination envelope shared by every list endpoint."""
    count: int
    page: int
    num_pages: int
    has_next: bool
    has_previous: bool


class JobOfferPageOut(Schema):
    items: List[JobOfferOut]
    page: Page


class OfferFiltersOut(Schema):
    """Distinct values present in the offer board, for the filter panel."""
    states: List[str]
    cities: List[str]
    job_positions: List[str]
    suitable_for: List[str]
    wages: List[float]
    housing: List[str]
    sort_options: List[str]


class NewsPageOut(Schema):
    items: List[NewsListOut]
    page: Page


# --- home aggregate ------------------------------------------------------


class HomeOut(Schema):
    """Everything the legacy ``CombinedView`` put in the index template.

    Served as one request so the homepage does not fan out into a dozen
    round-trips on first paint.
    """
    main_slider: Optional[HeroSlide] = None
    second_slider: Optional[HeroSlide] = None
    third_slider: Optional[HeroSlide] = None
    forth_slider: Optional[HeroSlide] = None
    about: Optional[AboutSectionOut] = None
    cta: Optional[BannerSectionOut] = None
    pricing_banner: Optional[BannerSectionOut] = None
    services: Optional[ServicesSectionOut] = None
    videos: Optional[VideoSectionOut] = None
    prices: Optional[PricesOut] = None
    featured_offers: List[JobOfferOut]
    latest_news: List[NewsListOut]
    stories: List[StoryOut]
