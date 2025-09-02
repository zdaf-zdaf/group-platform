import jwt
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings

class CustomJWTAuthentication:
    """
    完全自定义的JWT认证类，不依赖Django用户模型
    """
    def authenticate(self, request):
        # 获取授权头
        header = self.get_header(request)
        if header is None:
            return None

        # 获取令牌
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        # 验证令牌
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

    def get_header(self, request):
        """
        从请求头获取Authorization头
        """
        header = request.META.get('HTTP_AUTHORIZATION')
        return header

    def get_raw_token(self, header):
        """
        从Authorization头中提取原始令牌
        """
        parts = header.split()
        if len(parts) == 0:
            return None

        if parts[0] not in ['Bearer', 'bearer']:
            return None

        if len(parts) != 2:
            return None

        return parts[1]

    def get_validated_token(self, raw_token):
        """
        验证并解码JWT令牌
        """
        try:
            # 使用与用户服务相同的密钥验证令牌
            return jwt.decode(
                raw_token,
                'django-insecure-9ekm#x74ns6(j*h)3+jb-v*sz7bho2edo%g)uktin)ugf-5!s%',
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            raise InvalidToken('Token has expired')
        except jwt.DecodeError:
            raise InvalidToken('Token is invalid')
        except Exception as e:
            raise InvalidToken(f'Token validation failed: {str(e)}')

    def get_user(self, validated_token):
        """
        从令牌中提取用户信息
        """
        try:
            user_id = validated_token.get('user_id')
            role = validated_token.get('role', 'student')
            
            # 创建简单的用户对象
            user = type('User', (object,), {
                'id': user_id,
                'role': role,
                'is_authenticated': True,
                'is_active': True
            })
            return user
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')