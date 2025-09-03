from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import AccessToken

class IsTeacherOrReadOnly(BasePermission):
    """
    允许教师创建、修改和删除实验，学生只能查看
    通过JWT令牌获取用户角色信息
    """

    def has_permission(self, request, view):
        # 允许所有用户查看实验
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
            
        # 从JWT令牌中获取用户角色
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                access_token = AccessToken(token)
                user_role = access_token.get('role', '')
                return user_role == 'teacher'
            except Exception:
                return False
                
        return False