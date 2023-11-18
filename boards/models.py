from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    profile_name = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    image_profile = models.ImageField(blank=True, null=True)

    def __str__(self):
        return str(self.user)
    
    
class Project(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=False)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='owned_projects', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    members = models.ManyToManyField(Profile, through='ProjectMembership', through_fields=('project', 'member'))

    def __str__(self):
        return self.title


class ProjectMembership(models.Model):
    class Access(models.IntegerChoices):
        MEMBER = 1            # Can view and create and move only own items
        ADMIN = 2             # Can remove members and modify project settings.

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    member = models.ForeignKey(Profile, on_delete=models.CASCADE)
    access_level = models.IntegerField(choices=Access.choices, default=1)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.member.user.username} | {self.project.title}'


class Board(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=False)

    def __str__(self):
        return self.title


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'todo', 'todo'
        DOING = 'doing', 'doing'
        SUSPEND = 'suspend', 'suspend'
        DONE = 'done', 'done'

    title = models.CharField(max_length=255)
    description = models.TextField()
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, blank=True, null=True)
    start_date = models.DateTimeField(null=True, blank=True)
    finish_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    status_task = models.CharField(max_length=255, choices=Status.choices, default=Status.TODO)

    def __str__(self):
        return self.title
    

