from rest_framework.permissions import BasePermission
from rest_framework.permissions import AllowAny

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'teacher'

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'student'