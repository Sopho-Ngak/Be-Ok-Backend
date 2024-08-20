# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from patients.models import DependentProfilePicture, Dependent


# @receiver(post_save, sender=Dependent)
# def create_dependent_profile_picture(sender, instance, created, **kwargs):
#     if created:
#         DependentProfilePicture.objects.get_or_create(dependent=instance)