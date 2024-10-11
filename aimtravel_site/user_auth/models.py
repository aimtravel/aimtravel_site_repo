import string
import random
from datetime import date

from autoslug import AutoSlugField
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils import timezone

from aimtravel_site.user_auth.managers import AppUserManager


def upload_to_path(instance, filename):
    return f'user/{instance.first_name}_{instance.last_name}/{filename}'


def get_date():
    today = date.today()
    return today


def generate_slug(instance):
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{instance.first_name}-{random_str}"


class AppUser(AbstractBaseUser, PermissionsMixin):

    class Meta:
        verbose_name = 'Потребителски профил'
        verbose_name_plural = 'Потребителски профили'

    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    
    Email and password are required. Other fields are optional.
    """

    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
    )

    first_name = models.CharField(
        max_length=20,
        unique=False,
        null=True,
        blank=False,
    )

    last_name = models.CharField(
        max_length=20,
        unique=False,
        null=True,
        blank=False,
    )

    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active. "
                  "Unselect this instead of deleting accounts."
    )

    date_joined = models.DateTimeField(
        default=timezone.now,
    )

    slug = AutoSlugField(unique=True, populate_from=generate_slug)

    user_picture = models.FileField(
        upload_to='user/pictures/',
        default='profile/default_profile_pic.jpg',
        verbose_name="Профилна снимка",
        blank=True,
        null=True,
    )

    def get_absolute_url(self):
        # This will return the URL to the user's profile using their slug
        return reverse('my-profile', kwargs={'slug': self.slug})

    USERNAME_FIELD = 'email'

    objects = AppUserManager()

    def __str__(self):
        return self.email

    # def get_full_name(self):
    #     """
    #     Return the first_name plus the last_name, with a space in between.
    #     """
    #     full_name = "%s %s" % (self.first_name, self.last_name)
    #     return full_name.strip()

    # def email_user(self, subject, message, from_email=None, **kwargs):
    #     """Send an email to this user."""
    #     send_mail(subject, message, from_email, [self.email], **kwargs)
