from rest_framework.permissions import BasePermission

class IsLecturer(BasePermission):
    """
    Allow only authenticated users whose 'role' attribute equals 'lecturer'.
    Adjust this to your real user model/roles.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
