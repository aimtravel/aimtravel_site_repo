from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from aimtravel_site.web.models import JobOffer


@receiver(pre_delete, sender=JobOffer)
def delete_picture_file(sender, instance, **kwargs):
    instance.delete_picture_file()
