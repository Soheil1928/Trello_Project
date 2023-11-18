from django.contrib import admin
from .models import Profile, Project, Board, Task, ProjectMembership


class ProjectMembershipInline(admin.StackedInline):
    model = ProjectMembership
    extra = 1

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    filter_horizontal = ['members']
    inlines = [ProjectMembershipInline]


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass