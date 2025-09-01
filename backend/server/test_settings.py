# server/test_settings.py
from .settings import *

# 允许所有主机访问
ALLOWED_HOSTS = ['*']

# 禁用CSRF保护（仅用于测试环境）
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = []

# 保留必要的中间件，包括认证中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 保留认证中间件
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 配置简单的认证后端（允许所有请求通过）
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.AllowAllUsersModelBackend',
]

# 禁用所有权限检查
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
}

# 配置简单的密码验证
AUTH_PASSWORD_VALIDATORS = []

# 启用调试模式
DEBUG = True