"""
Django settings for notice_service project.
"""

import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-notice-service-secret-key')

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'  # 默认关闭调试模式

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# 应用定义
INSTALLED_APPS = [
    'django_prometheus',  # 添加Prometheus监控支持
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'notice_app',
]

# 中间件
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',  # Prometheus
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 添加静态文件处理
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',  # Prometheus
]

ROOT_URLCONF = 'notice_project.urls'

# 模板设置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 添加模板目录
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'notice_project.wsgi.application'

# 数据库配置
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'notice_db')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'notice_user')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'password')

DATABASES = {
    'default': {
        'ENGINE': 'django_prometheus.db.backends.postgresql',  # Prometheus监控
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': POSTGRES_PORT,
    }
}

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 10},  # 强密码策略
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # 优化静态文件处理
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# 媒体文件
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST框架配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',  # 所有API需要认证
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'moderate': '100/hour',  # 常规操作限流
        'high': '10/minute',     # 高频操作限流
    },
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',  # 仅提供JSON格式
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',  # 仅支持JSON输入
    ),
    'EXCEPTION_HANDLER': 'notice_project.settings.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,  # 默认分页大小
}

# JWT配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),         # 访问令牌有效期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),           # 刷新令牌有效期
    'ROTATE_REFRESH_TOKENS': True,                          # 刷新令牌时返回新令牌
    'BLACKLIST_AFTER_ROTATION': True,                       # 加入黑名单
    'UPDATE_LAST_LOGIN': True,                              # 更新最后登录时间
    'ALGORITHM': 'HS256',                                   # 加密算法
    'SIGNING_KEY': SECRET_KEY,                              # 使用主秘钥
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),                       # 认证头类型
    'USER_ID_FIELD': 'id',                                  # 用户ID字段
    'USER_ID_CLAIM': 'user_id',                             # 用户ID声明
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# CORS跨域设置
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # 生产环境必须关闭

# 仅允许指定域名访问
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",  # 替换为实际前端域名
]

# 允许的请求方法
CORS_ALLOW_METHODS = [
    'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT'
]

# 允许的请求头
CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
    'x-csrftoken',
    'x-requested-with',
]

# 仅当DEBUG=True时允许所有来源（用于开发环境）
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = []

# CSRF设置
CSRF_COOKIE_SECURE = not DEBUG  # 生产环境开启HTTPS Only
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()  # 同步设置

# 安全相关设置
if not DEBUG:
    # 生产环境强制使用HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1年HSTS
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/notice_service.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'notice_app': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# 外部服务配置
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://user-service:8000')
EXPERIMENT_SERVICE_URL = os.environ.get('EXPERIMENT_SERVICE_URL', 'http://experiment-service:8000')

# 健康检查配置
HEALTH_CHECK_ENDPOINT = os.environ.get('HEALTH_CHECK_ENDPOINT', '/api/health/')

# Prometheus监控配置
PROMETHEUS_EXPORT_MIGRATIONS = True

# 自定义异常处理
def custom_exception_handler(exc, context):
    """
    自定义DRF异常处理，提供更友好的错误信息
    在生产环境中避免返回敏感信息
    """
    from rest_framework.views import exception_handler
    response = exception_handler(exc, context)

    if response is not None:
        if DEBUG:
            # 调试模式下返回详细错误信息
            error_details = str(exc)
            error_type = type(exc).__name__
        else:
            # 生产环境返回通用错误信息
            error_details = 'Internal Server Error'
            error_type = 'ServerError'
            
            # 特定错误类型友好提示
            if response.status_code == 400:
                error_details = 'Invalid request parameters'
            elif response.status_code == 401:
                error_details = 'Authentication required'
            elif response.status_code == 403:
                error_details = 'Permission denied'
            elif response.status_code == 404:
                error_details = 'Resource not found'
            elif response.status_code == 500:
                error_details = 'Internal server error'

        custom_data = {
            'error': True,
            'code': response.status_code,
            'type': error_type,
            'message': error_details,
        }

        # 在调试模式下添加额外细节
        if DEBUG and hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                custom_data['details'] = exc.detail
            elif isinstance(exc.detail, list):
                custom_data['details'] = {'errors': exc.detail}

        response.data = custom_data

    return response