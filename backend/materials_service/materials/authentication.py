from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.models import TokenUser

class StatelessUser(AnonymousUser):
    """
    一个临时的、无状态的用户对象，仅包含从JWT Token中获取的信息。
    """
    def __init__(self, token):
        self.token = token
        # 从Token claims中提取用户ID
        self.id = token.get('user_id')
        self.is_active = True
        self.is_staff = False
        self.is_superuser = False

    @property
    def is_authenticated(self):
        return True

class StatelessJWTAuthentication(JWTAuthentication):
    """
    一个自定义的JWT认证后端。
    在成功验证Token后，它不会查询数据库，而是返回一个StatelessUser对象。
    """
    def get_user(self, validated_token):
        # 不再查询数据库，而是直接用Token信息创建一个StatelessUser
        return StatelessUser(validated_token)
