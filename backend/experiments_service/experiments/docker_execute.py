import docker
import logging
import time
from django.conf import settings

logger = logging.getLogger('docker_execute')

class DockerJudge:
    """使用Docker执行代码的判题器"""
    
    def __init__(self):
        self.client = docker.from_env()
    
    def run_code(self, problem_config, code):
        """执行代码并返回结果"""
        try:
            # 创建临时容器
            container = self.client.containers.run(
                image=settings.DOCKER_JUDGE_IMAGE,
                command=f"python -c '{code}'",
                environment={
                    'INPUT': problem_config.get('test_cases', '')
                },
                mem_limit=f"{problem_config.get('mem_limit', 256)}m",
                network_mode='none',
                detach=True
            )
            
            # 等待容器执行完成
            try:
                container.wait(timeout=problem_config.get('timeout', 10))
            except docker.errors.ContainerError as e:
                logger.error(f"容器执行错误: {str(e)}")
            
            # 获取日志输出
            logs = container.logs().decode('utf-8')
            
            # 清理容器
            container.remove()
            
            return {
                'status': 'success',
                'output': logs
            }
        except Exception as e:
            logger.exception(f"执行代码失败: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }