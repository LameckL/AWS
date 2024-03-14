from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.main.models import User, Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a profile for the user when a new user is created.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Save the profile whenever the user is saved.
    """
    instance.profile.save()
