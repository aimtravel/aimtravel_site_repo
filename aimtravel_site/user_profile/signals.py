# from django.contrib.auth import get_user_model
# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
#
# from aimtravel_site.user_profile.models import Students
#
# UserModel = get_user_model()
#
# """
# Below 'Signal' is placed to create 'Student' (regular user) instance.
# The model can be filled later by the student/employee/superuser.
# """
#
#
# @receiver(post_save, sender=UserModel)
# def create_profile(sender, instance, created, *args, **kwargs):
#     if created:
#         Students.objects.create(
#             user=instance,
#             email=instance.email,
#             first_name=instance.first_name,
#             last_name=instance.last_name,
#         )
