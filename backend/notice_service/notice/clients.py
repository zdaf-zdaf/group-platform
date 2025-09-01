import requests
import logging
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger('notice_app')

class BaseAPIClient:
    def __init__(self, service_url):
        self.service_url = service_url
        self.headers = {'Content-Type': 'application/json'}

    def set_jwt_token(self, token):
        self.headers['Authorization'] = f'Bearer {token}'
        
    def _get(self, endpoint, params=None):
        url = f"{self.service_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"请求失败: {str(e)}")
            return None
            
    def _post(self, endpoint, data):
        url = f"{self.service_url}{endpoint}"
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"请求失败: {str(e)}")
            return None

class UserServiceClient(BaseAPIClient):
    def __init__(self):
        super().__init__(settings.USER_SERVICE_URL)
        
    def get_user_info(self, user_id):
        return self._get(f"/api/users/{user_id}/brief/")
    
    def validate_teacher_role(self, user_id):
        user_info = self.get_user_info(user_id)
        return user_info and user_info.get('role') == 'teacher'

class ExperimentServiceClient(BaseAPIClient):
    def __init__(self):
        super().__init__(settings.EXPERIMENT_SERVICE_URL)
        
    def get_experiment_info(self, experiment_id):
        return self._get(f"/api/experiments/{experiment_id}/brief/")