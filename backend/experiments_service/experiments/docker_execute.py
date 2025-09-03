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
            # 创建临时容器 - 使用安全的方式执行代码
            container = self.client.containers.create(
                image=settings.DOCKER_JUDGE_IMAGE,
                command=["python", "-c", "import sys; exec(sys.stdin.read())"],
                environment={
                    'INPUT': problem_config.get('test_cases', '')
                },
                mem_limit=f"{problem_config.get('mem_limit', 256)}m",
                network_mode='none',
                stdin_open=True,  # 开启标准输入
            )
            
            # 启动容器
            container.start()
            
            # 通过标准输入发送代码
            socket = container.attach_socket(params={'stdin': 1, 'stream': 1})
            socket._sock.sendall(code.encode('utf-8'))
            socket._sock.sendall(b'\n')  # 确保代码被执行
            socket.close()
            
            # 等待容器执行完成
            try:
                result = container.wait(timeout=problem_config.get('timeout', 10))
                exit_code = result['StatusCode']
            except docker.errors.ContainerError as e:
                logger.error(f"容器执行错误: {str(e)}")
                exit_code = 1
            
            # 获取日志输出
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')
            
            # 清理容器
            container.remove(force=True)
            
            return {
                'status': 'success',
                'exit_code': exit_code,
                'output': logs
            }
        except Exception as e:
            logger.exception(f"执行代码失败: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }