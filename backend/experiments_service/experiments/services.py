import logging
import requests
from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import PermissionDenied

logger = logging.getLogger('experiment')

class UserServiceClient:
    """用户服务客户端"""
    
    def __init__(self):
        self.base_url = settings.USER_SERVICE_URL
        self.token = settings.USER_SERVICE_TOKEN
    
    def get_user_info(self, user_id):
        """获取用户信息"""
        cache_key = f'user_{user_id}'
        user_info = cache.get(cache_key)
        
        if user_info:
            return user_info
            
        try:
            response = requests.get(
                f'{self.base_url}/api/users/{user_id}/',
                headers={'Authorization': f'Bearer {self.token}'},
                timeout=3
            )
            
            if response.status_code == 200:
                user_info = response.json()
                cache.set(cache_key, user_info, 300)  # 缓存5分钟
                return user_info
            else:
                logger.error(f"获取用户信息失败: {response.status_code}")
                return None
        except requests.RequestException as e:
            logger.exception(f"调用用户服务失败: {str(e)}")
            return None
    
    def validate_teacher_role(self, user_id):
        """验证用户是否为教师"""
        user_info = self.get_user_info(user_id)
        if not user_info:
            return False
            
        return user_info.get('role') == 'teacher'