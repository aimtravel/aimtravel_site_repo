from django.contrib import admin

from aimtravel_site.posting.models import News


# Register your models here.
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['news_title', 'date']
    list_filter = ['news_title', 'date']
    sortable_by = ['news_title', 'date']