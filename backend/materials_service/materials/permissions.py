from rest_framework import permissions

# permissions.py
class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        role = getattr(request.user, 'role', None)
        is_staff = getattr(request.user, 'is_staff', False)
        is_superuser = getattr(request.user, 'is_superuser', False)
        return role == 'teacher' or is_staff or is_superuser
