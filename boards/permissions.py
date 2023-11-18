from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Project

class CanViewProfile(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.method in SAFE_METHODS or
                    request.user and request.user == obj.user)


class CanEditProject(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.method in SAFE_METHODS or
                    request.user.id == obj.owner.user.id)
    
    
class IsAdminOrMemberReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        project = Project.objects.get(pk=obj.project_id)
        if request.user.id == project.owner_id:
            return True
        else:
            return False