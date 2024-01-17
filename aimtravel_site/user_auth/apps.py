from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aimtravel_site.user_auth'
    verbose_name = "User Authentication"
