from django.contrib import admin
from aimtravel_site.main_page.models import *


@admin.register(MainSlider)
class MainSliderAdmin(admin.ModelAdmin):
    list_display = ['title1', 'title2', 'button_link',]


@admin.register(SecondSlider)
class SecondSliderAdmin(admin.ModelAdmin):
    list_display = ['title1', 'title2', 'content1', 'button_link',]


@admin.register(ThirdSlider)
class ThirdSliderAdmin(admin.ModelAdmin):
    list_display = ['top_title', 'main_title', 'content1', 'button_link',]


@admin.register(ForthSlider)
class ForthSliderAdmin(admin.ModelAdmin):
    list_display = ['top_title', 'main_title', 'content1', 'button_link',]


@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(CallToActionSection)
class CallToActionSectionAdmin(admin.ModelAdmin):
    list_display = ['title1']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['main_video']


@admin.register(MainPricingSection)
class MainPricingSectionAdmin(admin.ModelAdmin):
    list_display = ['title1']


@admin.register(MainServicesSection)
class MainServicesSectionAdmin(admin.ModelAdmin):
    list_display = ['title1']
