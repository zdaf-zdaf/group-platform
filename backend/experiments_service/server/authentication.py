import jwt
from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings

class CustomJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # 获取授权头
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        # 验证授权头格式
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None

        token = parts[1]

        try:
            # 使用JWT配置中的签名密钥
            payload = jwt.decode(
                token,
                settings.SIMPLE_JWT['SIGNING_KEY'],
                algorithms=[settings.SIMPLE_JWT['ALGORITHM']]
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Token validation failed: {str(e)}')

        # 创建用户对象 - 从JWT令牌中提取用户信息
        user = type('User', (object,), {
            'id': payload.get(settings.SIMPLE_JWT['USER_ID_CLAIM']),
            'role': payload.get('role', 'student'),
            'is_authenticated': True,
        })

        return (user, token)