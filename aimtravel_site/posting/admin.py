from django.contrib import admin

from aimtravel_site.posting.models import *


# Register your models here.
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['news_title', 'date']
    list_filter = ['news_title', 'date']
    sortable_by = ['news_title', 'date']


@admin.register(MainFeedback)
class MainFeedbackAdmin(admin.ModelAdmin):
    list_display = ['feedback_1_title', 'feedback_2_title', 'feedback_3_title']
    search_fields = ['feedback_1_title', 'feedback_2_title', 'feedback_3_title']


@admin.register(AdditionalFeedback)
class AdditionalFeedbackAdmin(admin.ModelAdmin):
    list_display = ['feedback_1_title', 'feedback_2_title', 'feedback_3_title']
    search_fields = ['feedback_1_title', 'feedback_2_title', 'feedback_3_title']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['main_video']
