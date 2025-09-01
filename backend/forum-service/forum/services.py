import requests
from django.conf import settings

class UserService:
    @staticmethod
    def get_user_info(user_id):
        try:
            response = requests.get(
                f'{settings.USER_SERVICE_URL}/users/{user_id}',
                timeout=2
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
            
        # 如果服务不可用，返回基本用户信息
        return {
            "id": user_id,
            "username": f"user{user_id}",
            "avatar": "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
        }