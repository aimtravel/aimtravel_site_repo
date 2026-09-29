from django.contrib.auth.views import PasswordChangeView
from django.views.generic import RedirectView
from django.urls import path
from aimtravel_site.user_auth.views import *


urlpatterns = (
    path('', SignInView.as_view(), name='sign in'),
    path('register/', RedirectView.as_view(pattern_name='sign in'), name='sign up'),
    path('portal/', StudentPortalView.as_view(), name='student portal'),
    path('sign-out/', SignOutView.as_view(), name='sign out'),
    path('change_password/',
         PasswordChangeView.as_view(template_name='user_auth/change-password.html', success_url='/'),
         name='change password'),
    path('password_reset/', password_reset_request, name='password_reset'),
    path('my_profile/<slug:slug>/', MyProfileView.as_view(), name='my-profile'),
    path('edit_profile/<int:pk>', EditUserProfileView.as_view(), name='edit user')
)
