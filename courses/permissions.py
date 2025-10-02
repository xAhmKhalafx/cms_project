from rest_framework.permissions import BasePermission

class IsLecturer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "lecturer_profile")
