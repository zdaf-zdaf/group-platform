from rest_framework.permissions import BasePermission

class IsTeacherOrReadOnly(BasePermission):
    """
    允许教师创建、修改和删除公告，学生只能查看
    """

    def has_permission(self, request, view):
        # 允许所有用户查看公告
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
            
        # 允许学生标记公告为已读
        if view.action in ['mark_as_read', 'mark_all_read']:
            return True

        # 只有教师可以创建、修改和删除公告
        return hasattr(request.user, 'role') and request.user.role == 'teacher'