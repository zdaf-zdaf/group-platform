import logging
import time
import requests
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from .clients import UserServiceClient, ExperimentServiceClient
from .exceptions import ExternalServiceTimeout, ExternalServiceError

logger = logging.getLogger('notice_app')

class NoticeService:
    """公告服务业务逻辑层，包含重试机制和降级策略"""
    
    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAY_BASE = 0.5  # 秒
    TIMEOUT = 5  # 秒
    
    @classmethod
    def _call_with_retry(cls, client_call, *args, **kwargs):
        """带重试机制的服务调用封装"""
        for attempt in range(1, cls.MAX_RETRIES + 1):
            try:
                # 设置超时时间
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = cls.TIMEOUT
                
                result = client_call(*args, **kwargs)
                
                # 检查结果是否有效
                if result is None:
                    logger.warning(f"服务调用返回空值 (尝试 #{attempt}/{cls.MAX_RETRIES})")
                    raise ExternalServiceError("服务调用返回空值")
                    
                return result
                
            except (requests.Timeout, requests.ConnectionError) as e:
                logger.warning(f"服务调用超时/连接错误 (尝试 #{attempt}/{cls.MAX_RETRIES}): {str(e)}")
                if attempt < cls.MAX_RETRIES:
                    delay = cls.RETRY_DELAY_BASE * (2 ** (attempt - 1))  # 指数退避
                    time.sleep(delay)
                else:
                    raise ExternalServiceTimeout(f"服务调用失败: 最终超时") from e
                    
            except Exception as e:
                logger.error(f"服务调用错误 (尝试 #{attempt}/{cls.MAX_RETRIES}): {str(e)}")
                if attempt < cls.MAX_RETRIES:
                    time.sleep(cls.RETRY_DELAY_BASE * attempt)
                else:
                    raise ExternalServiceError(f"服务调用失败: {str(e)}") from e
    
    @classmethod
    def _get_token(cls, request):
        """安全获取并返回JWT token"""
        try:
            if request and hasattr(request, 'user'):
                token = AccessToken.for_user(request.user)
                return str(token)
        except Exception as e:
            logger.error(f"获取JWT token失败: {str(e)}")
        return None
    
    @classmethod
    def get_author_name(cls, author_id, request=None):
        """通过用户服务获取作者名称，带重试机制"""
        client = UserServiceClient()
        token = cls._get_token(request)
        if token:
            client.set_jwt_token(token)
        
        try:
            # 带重试机制的调用
            user_info = cls._call_with_retry(client.get_user_info, author_id)
            
            if user_info and isinstance(user_info, dict):
                return user_info.get('username', '未知用户')
                
            logger.warning(f"用户服务返回无效响应: {type(user_info)}")
            return "未知用户"
            
        except (ExternalServiceTimeout, ExternalServiceError) as e:
            logger.error(f"获取作者名称失败: {str(e)}")
            return "未知用户 (服务不可用)"
    
    @classmethod
    def get_experiment_info(cls, experiment_id, request=None):
        """通过实验服务获取实验信息，带重试机制"""
        if not experiment_id:
            return None
            
        client = ExperimentServiceClient()
        token = cls._get_token(request)
        if token:
            client.set_jwt_token(token)
        
        try:
            # 带重试机制的调用
            exp_info = cls._call_with_retry(client.get_experiment_info, experiment_id)
            
            if exp_info and isinstance(exp_info, dict):
                return exp_info
                
            logger.warning(f"实验服务返回无效响应: {type(exp_info)}")
            return {'id': experiment_id, 'name': '未知实验'}
            
        except (ExternalServiceTimeout, ExternalServiceError) as e:
            logger.error(f"获取实验信息失败: {str(e)}")
            return {
                'id': experiment_id, 
                'name': '服务不可用',
                'error': str(e),
                'status': 'unavailable'
            }
    
    @classmethod
    def validate_teacher_role(cls, user_id, request=None):
        """验证用户是否为教师角色，带重试机制"""
        client = UserServiceClient()
        token = cls._get_token(request)
        if token:
            client.set_jwt_token(token)
        
        try:
            # 带重试机制的调用
            is_teacher = cls._call_with_retry(client.validate_teacher_role, user_id)
            
            if isinstance(is_teacher, bool):
                return is_teacher
                
            logger.warning(f"角色验证服务返回无效响应: {type(is_teacher)}")
            return False  # 安全失败，拒绝访问
            
        except (ExternalServiceTimeout, ExternalServiceError) as e:
            logger.error(f"角色验证失败: {str(e)}")
            # 根据安全策略，在服务不可用时可以设置为严格模式或宽松模式
            # 严格模式：返回False拒绝访问；宽松模式：返回True允许访问
            # 根据业务需求选择，这里选择严格模式
            if settings.STRICT_MODE_ON_SERVICE_FAILURE:
                logger.warning("服务不可用 - 采用严格模式: 拒绝所有操作")
                return False
            else:
                logger.warning("服务不可用 - 采用宽松模式: 允许操作")
                return True