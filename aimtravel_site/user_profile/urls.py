from django.urls import path, include

from aimtravel_site.user_profile.views import EditUserProfileView, UserProfileView, EmployeeProfileView, \
    EditEmployeeProfileView, AllUsersView

urlpatterns = (
    path('profile/', include([
        path('edit/<int:pk>/', EditUserProfileView.as_view(), name='edit profile'),
        path('details/<int:pk>/', UserProfileView.as_view(), name='details profile'),
        path('listed/', AllUsersView.as_view(), name='list profiles'),
    ])),
    path('employee/', include([
        path('details/<int:pk>/', EmployeeProfileView.as_view(), name='employee profile details'),
        path('edit/<int:pk>/', EditEmployeeProfileView.as_view(), name='employee profile edit')
    ])),
)

from .signals import *
