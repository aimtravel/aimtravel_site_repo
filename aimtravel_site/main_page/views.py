from django.shortcuts import render
from django.views import generic as views
from django.core.paginator import Paginator

from aimtravel_site.posting.models import *
from aimtravel_site.web.models import *
from aimtravel_site.main_page.models import *

# Create your views here.


class CombinedView(views.ListView):
    template_name = 'index.html'
    context_object_name = 'combined_data'
    paginate_by = 4

    def get_main_slider(self):
        return MainSlider.objects.latest('id')

    def get_second_slider(self):
        return SecondSlider.objects.latest('id')

    def get_third_slider(self):
        return ThirdSlider.objects.latest('id')

    def get_forth_slider(self):
        return ForthSlider.objects.latest('id')

    def get_main_services(self):
        return MainServicesSection.objects.latest('id')

    def get_main_pricing(self):
        return MainPricingSection.objects.latest('id')

    def get_last_news(self):
        return News.objects.latest('date')

    def get_main_feedback(self):
        return MainFeedback.objects.order_by('-id')[:3]

    def get_videos(self):
        return Video.objects.latest('id')

    def get_prices(self):
        return Prices.objects.latest('id')

    def get_about(self):
        return AboutSection.objects.latest('id')

    def get_cta(self):
        return CallToActionSection.objects.latest('id')

    def get(self, request):
        page_number = self.request.GET.get('page')
        offer_queryset = JobOffer.objects.order_by(
            '-ranking',
            '-last_seats',
            '-new_offer',
            '-wage',
            'job_position',
            'sold_out_offer'
        )
        offer_paginator = Paginator(offer_queryset, self.paginate_by)
        offer_page = offer_paginator.get_page(page_number)

        # Get the first 4 News items
        news_queryset = News.objects.order_by('-date')[:4]

        main_slider = self.get_main_slider()
        second_slider = self.get_second_slider()
        third_slider = self.get_third_slider()
        forth_slider = self.get_forth_slider()
        main_services = self.get_main_services()
        main_pricing = self.get_main_pricing()
        last_news_item = self.get_last_news()
        main_feedback = self.get_main_feedback()
        video = self.get_videos()
        prices = self.get_prices()
        about = self.get_about()
        cta = self.get_cta()

        context = {
            'main_slider': main_slider,
            'second_slider': second_slider,
            'third_slider': third_slider,
            'forth_slider': forth_slider,
            'main_pricing': main_pricing,
            'main_services': main_services,
            'about': about,
            'cta': cta,
            'offer_list': offer_page,
            'last_4_news': news_queryset,
            'very_last_news': last_news_item,
            'main_feedback': main_feedback,
            'video': video,
            'prices': prices,
        }

        return render(request, self.template_name, context)


def main_page(request):
    return render(request, template_name='nav/contacts.html')
