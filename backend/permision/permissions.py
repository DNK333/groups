from rest_framework.permissions import BasePermission

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="Teacher").exists()
        )
        
        
class IsArticleOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user