import jwt
from rest_framework import authentication
from rest_framework import exceptions

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
            # 验证令牌
            payload = jwt.decode(
                token,
                'django-insecure-9ekm#x74ns6(j*h)3+jb-v*sz7bho2edo%g)uktin)ugf-5!s%',
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Token validation failed: {str(e)}')

        # 创建用户对象
        user = type('User', (object,), {
            'id': payload.get('user_id'),
            'role': payload.get('role', 'student'),
            'is_authenticated': True,
        })

        return (user, token)