"""aimtravel_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf.urls import handler404, handler500
from django.contrib.sitemaps import views as sitemaps_views

from aimtravel_site import settings
from aimtravel_site.api.api import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('', include('aimtravel_site.web.urls')),
    path('', include('aimtravel_site.main_page.urls')),
    path('user_auth/', include('aimtravel_site.user_auth.urls')),
    path('user_profile/', include('aimtravel_site.user_profile.urls')),
    path('post/', include('aimtravel_site.posting.urls')),
    path('taxes/', include('aimtravel_site.taxes.urls')),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="password/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'),
         name='password_reset_complete'),
    path("ckeditor5/", include('django_ckeditor_5.urls')),

]

handler404 = 'aimtravel_site.web.views.error_404'
handler500 = 'aimtravel_site.web.views.error_500'
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
