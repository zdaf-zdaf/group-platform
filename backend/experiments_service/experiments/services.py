import logging
import time
from .clients import UserServiceClient
from .exceptions import ExternalServiceError, ExternalServiceTimeout

logger = logging.getLogger('experiment_app')

class ExperimentService:
    """实验业务服务层"""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 0.5  # 秒
    
    @staticmethod
    def get_user_info(user_id):
        """获取用户信息（带重试）"""
        client = UserServiceClient()
        for attempt in range(1, ExperimentService.MAX_RETRIES + 1):
            try:
                user_info = client.get_user_info(user_id)
                if user_info:
                    return user_info
            except Exception as e:
                logger.warning(f"获取用户信息尝试 {attempt} 失败: {str(e)}")
                if attempt < ExperimentService.MAX_RETRIES:
                    time.sleep(ExperimentService.RETRY_DELAY * attempt)
                else:
                    raise ExternalServiceError(f"获取用户信息失败: {str(e)}")
        return None
    
    @staticmethod
    def validate_teacher_role(user_id):
        """验证教师角色（带重试）"""
        client = UserServiceClient()
        for attempt in range(1, ExperimentService.MAX_RETRIES + 1):
            try:
                is_teacher = client.validate_teacher_role(user_id)
                return is_teacher
            except Exception as e:
                logger.warning(f"验证教师角色尝试 {attempt} 失败: {str(e)}")
                if attempt < ExperimentService.MAX_RETRIES:
                    time.sleep(ExperimentService.RETRY_DELAY * attempt)
                else:
                    raise ExternalServiceError(f"验证教师角色失败: {str(e)}")
        return False