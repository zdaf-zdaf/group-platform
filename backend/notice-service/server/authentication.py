import logging
import jwt
from rest_framework import authentication
from rest_framework import exceptions

logger = logging.getLogger('authentication')  # 使用新日志器

class CustomJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # 获取授权头
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            logger.debug("未提供授权头")
            return None

        # 验证授权头格式
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            logger.debug(f"无效的授权头格式: {auth_header}")
            return None

        token = parts[1]
        logger.debug(f"验证令牌: {token}")

        try:
            # 验证令牌
            payload = jwt.decode(
                token,
                'django-insecure-9ekm#x74ns6(j*h)3+jb-v*sz7bho2edo%g)uktin)ugf-5!s%',
                algorithms=['HS256']
            )
            logger.debug(f"令牌有效: {payload}")
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.DecodeError:
            logger.warning("无效令牌")
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            logger.error(f"令牌验证失败: {str(e)}")
            raise exceptions.AuthenticationFailed(f'Token validation failed: {str(e)}')

        # 创建用户对象
        role = payload.get('role', 'student').lower()
        user_id = payload.get('user_id')
        
        logger.info(f"创建用户对象: ID={user_id}, 角色={role}")
        
        user = type('User', (object,), {
            'id': user_id,
            'role': role,
            'is_authenticated': True,
        })

        return (user, token)