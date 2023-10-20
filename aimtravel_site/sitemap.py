from django.contrib import sitemaps
from .web.models import *
from .posting.models import *


class NewsSitemap(sitemaps.Sitemap):
    changefreq = 'weekly'  # Set the change frequency (optional)
    priority = 0.9  # Set the priority (optional)

    def items(self):
        return News.objects.all()


class MainFeedbackSitemap(sitemaps.Sitemap):
    changefreq = 'weekly'  # Set the change frequency (optional)
    priority = 0.9  # Set the priority (optional)

    def items(self):
        return MainFeedback.objects.all()


class VideoSitemap(sitemaps.Sitemap):
    changefreq = 'weekly'  # Set the change frequency (optional)
    priority = 0.9  # Set the priority (optional)

    def items(self):
        return Video.objects.all()


class FaqSitemap(sitemaps.Sitemap):
    changefreq = 'weekly'  # Set the change frequency (optional)
    priority = 0.9  # Set the priority (optional)

    def items(self):
        return Faq.objects.all()


class CitySitemap(sitemaps.Sitemap):
    changefreq = 'weekly'  # Set the change frequency (optional)
    priority = 0.9  # Set the priority (optional)

    def items(self):
        return City.objects.all()


class FeedbackSitemap(sitemaps.Sitemap):
    changefreq = 'weekly'  # Set the change frequency (optional)
    priority = 0.9  # Set the priority (optional)

    def items(self):
        return Feedback.objects.all()


class JobOfferSitemap(sitemaps.Sitemap):
    changefreq = 'weekly'  # Set the change frequency (optional)
    priority = 0.9  # Set the priority (optional)

    def items(self):
        return JobOffer.objects.all()

    def city(self, obj):
        return obj.city

    def feedback(self, obj):
        return obj.feedback

    def get_urls(self, page=1, site=None, protocol=None):
        urls = []
        for job_offer in self.items():
            url_info = {
                'city': self.city(job_offer),
                'feedback': self.feedback(job_offer),
                'changefreq': self.changefreq,
                'priority': self.priority,
            }
            urls.append(url_info)
        return urls

