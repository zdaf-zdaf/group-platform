#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging

# 配置日志 - 可选，但有助于调试
logging.basicConfig(
    level=logging.INFO,  # 生产环境可以考虑使用 INFO 而不是 DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('django_manage')

def main():
    """Run administrative tasks."""
    logger.info("Starting Django management command")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        logger.error("Couldn't import Django: %s", exc)
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # 调试信息 - 可选
    if os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true':
        logger.debug("Current working directory: %s", os.getcwd())
        logger.debug("Directory contents: %s", os.listdir(os.getcwd()))
    
    logger.info("Executing command: %s", sys.argv)
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.exception("Unhandled exception in manage.py")
        raise