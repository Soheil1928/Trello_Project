from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Project, ProjectMembership


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance, profile_name=instance.username)
        user_profile.save()


@receiver(post_save, sender=Project)
def create_project(sender, instance, created, **kwargs):
    if created:
        ProjectMembership.objects.create(member=instance.owner, project=instance, access_level=2)