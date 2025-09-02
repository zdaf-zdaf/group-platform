from rest_framework.permissions import BasePermission

class IsTeacher(BasePermission):
    """
    检查 Token 中的角色是否为 'teacher'
    """
    def has_permission(self, request, view):
        # 当 JWT 认证成功后，Token 的载荷(payload)会保存在 request.auth 中
        # request.user 是一个 SimpleLazyObject，代表一个临时的、不在数据库中的用户
        if not request.user or not request.auth:
            return False
        
        # 从 Token 的载荷中获取 role 字段，并判断是否为 'teacher'
        return request.auth.get('role') == 'teacher'