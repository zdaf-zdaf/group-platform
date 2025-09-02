import jwt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        自定义用户获取方法，不依赖数据库用户
        """
        try:
            user_id = validated_token.get(api_settings.USER_ID_CLAIM)
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