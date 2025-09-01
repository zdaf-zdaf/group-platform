from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
import requests

class MicroserviceAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # 从请求头中获取认证令牌
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
            
        # 调用认证微服务验证令牌
        try:
            response = requests.get(
                'http://auth-service/verify-token',
                headers={'Authorization': auth_header}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                # 将用户信息添加到请求对象中
                request.user_id = user_data['id']
                request.is_admin = user_data.get('is_admin', False)
                return (None, None)  # 返回None因为我们已经处理了认证
            else:
                raise AuthenticationFailed('无效的认证令牌')
                
        except requests.RequestException:
            raise AuthenticationFailed('认证服务不可用')