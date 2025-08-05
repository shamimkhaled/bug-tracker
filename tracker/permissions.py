from rest_framework import permissions
from django.db.models import Q

class IsOwnerOrReadOnly(permissions.BasePermission):
 
    def has_object_permission(self, request, view, obj):
        
        # Read permissions for any request,
        # Write permissions only to the owner.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class IsProjectMemberOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        
        # For Bug objects, check project access
        if hasattr(obj, 'project'):
            project = obj.project
            return (
                project.owner == request.user or
                obj.assigned_to == request.user or
                obj.created_by == request.user
            )
        return False