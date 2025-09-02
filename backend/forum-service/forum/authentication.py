from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import jwt
from jwt import exceptions

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # 从请求头中获取认证令牌
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
            
        # 验证令牌格式
        if not auth_header.startswith('Bearer '):
            raise AuthenticationFailed('认证令牌格式错误')
            
        token = auth_header[7:]  # 去掉'Bearer '前缀
        
        try:
            # 使用JWT验证令牌
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except exceptions.ExpiredSignatureError:
            raise AuthenticationFailed('认证令牌已过期')
        except jwt.DecodeError:
            raise AuthenticationFailed('认证令牌无效')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('无效的认证令牌')
            
        # 从payload中获取用户信息
        user_id = payload.get('user_id')
        role = payload.get('role')
        
        if not user_id:
            raise AuthenticationFailed('认证令牌中缺少用户ID')
            
        # 将用户信息添加到请求对象中
        request.user_id = user_id
        request.is_admin = (role == 'teacher')  # 假设教师是管理员
        
        return (None, None)  # 返回None因为我们已经处理了认证