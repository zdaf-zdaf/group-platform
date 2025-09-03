from rest_framework.permissions import BasePermission

class IsTeacherOrReadOnly(BasePermission):
    """
    允许教师创建、修改和删除实验，学生只能查看
    """

    def has_permission(self, request, view):
        # 允许所有用户查看实验
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
            
        # 检查用户角色是否为教师
        return hasattr(request.user, 'role') and request.user.role == 'teacher'