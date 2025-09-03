#!/usr/bin/env python
import os
import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('manage.py')

def main():
    logger.debug("Starting Django management command")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
    
    try:
        logger.debug("Importing Django core")
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        logger.error("ImportError: Couldn't import Django")
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # 调试：打印当前工作目录和文件列表
    logger.debug("Current working directory: %s", os.getcwd())
    logger.debug("Directory contents: %s", os.listdir(os.getcwd()))
    
    # 调试：尝试导入 experiments 应用
    try:
        logger.debug("Attempting to import experiments app")
        import experiments
        logger.debug("Successfully imported experiments app")
    except ImportError as e:
        logger.error("Failed to import experiments app: %s", str(e))
    
    logger.debug("Executing command: %s", sys.argv)
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    logger.debug("manage.py starting")
    try:
        main()
    except Exception as e:
        logger.exception("Unhandled exception in manage.py")
        raise