import requests
import logging
from django.conf import settings
import time

logger = logging.getLogger('experiment_app')

class BaseAPIClient:
    def __init__(self, service_url):
        self.service_url = service_url
        self.timeout = 5
        self.headers = {'Content-Type': 'application/json'}
    
    def _get(self, endpoint, params=None):
        url = f"{self.service_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"请求失败: {str(e)}")
            return None

class UserServiceClient(BaseAPIClient):
    def __init__(self):
        super().__init__(settings.USER_SERVICE_URL)
    
    def get_user_info(self, user_id):
        """获取用户信息"""
        return self._get(f"/api/users/{user_id}/brief/")
    
    def validate_teacher_role(self, user_id):
        """验证用户是否为教师"""
        user_info = self.get_user_info(user_id)
        return user_info and user_info.get('role') == 'teacher'