"""
Signal handlers for accounts app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a User is created.
    Only creates profile if the user has a college assigned.
    """
    if created and instance.college_id:
        # Check if profile already exists
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(
                user=instance,
                college=instance.college
            )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile when User is saved (if profile exists).
    """
    if hasattr(instance, 'profile') and instance.profile:
        # Update college if it changed
        if instance.college_id and instance.profile.college_id != instance.college_id:
            instance.profile.college = instance.college
            instance.profile.save()
