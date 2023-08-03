# import django_filters
# from django.db import models
# from django import forms
#
# from aimtravel_site.web.models import JobOffer
#
#
# class OfferFilter(django_filters.FilterSet):
#
#     class Meta:
#         model = JobOffer
#         fields = {
#             'job_position': ['exact'],
#             'city': ['exact'],
#             'wage': ['lt', 'gt'],
#             'ranking': ['exact'],
#         }
#         filter_overrides = {
#             models.CharField: {
#                 'filter_class': django_filters.CharFilter,
#                 'extra': lambda f: {
#                     'lookup_expr': 'icontains',
#                 },
#             },
#             models.BooleanField: {
#                 'filter_class': django_filters.BooleanFilter,
#                 'extra': lambda f: {
#                     'widget': forms.CheckboxInput,
#                 },
#             },
#         }