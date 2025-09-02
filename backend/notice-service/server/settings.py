import os
from pathlib import Path
from datetime import timedelta

# 从 authentication.py 导入自定义认证类
from server.authentication import CustomJWTAuthentication

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-公告服务安全密钥'
DEBUG = True
ALLOWED_HOSTS = ['*']
USE_TZ = True
TIME_ZONE = 'Asia/Shanghai'

# Application definition
INSTALLED_APPS = [
    'server.apps.ServerConfig',  # 添加应用配置
    'notice.apps.NoticeConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'server.urls'

# 添加 TEMPLATES 配置 - 这是解决 admin.E403 错误的关键
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'server.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'notice_db',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'host.docker.internal',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# 允许使用环境变量在容器/部署环境中覆盖数据库配置
DB_ENGINE = os.getenv('DB_ENGINE')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

if any([DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
    DATABASES['default'] = {
        'ENGINE': DB_ENGINE or DATABASES['default']['ENGINE'],
        'NAME': DB_NAME or DATABASES['default']['NAME'],
        'USER': DB_USER or DATABASES['default']['USER'],
        'PASSWORD': DB_PASSWORD or DATABASES['default']['PASSWORD'],
        'HOST': DB_HOST or DATABASES['default']['HOST'],
        'PORT': DB_PORT or DATABASES['default']['PORT'],
        'OPTIONS': DATABASES['default'].get('OPTIONS', {'charset': 'utf8mb4'})
    }

# REST Framework 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'server.authentication.CustomJWTAuthentication',  # 使用字符串引用
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'EXCEPTION_HANDLER': 'server.settings.custom_exception_handler'
}

# CORS 设置
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# JWT 配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'django-insecure-9ekm#x74ns6(j*h)3+jb-v*sz7bho2edo%g)uktin)ugf-5!s%',  # 使用用户服务的 SECRET_KEY
    'VERIFYING_KEY': None,
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}
AUTH_USER_MODEL = None

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'  # 改为中文界面
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # 修改为 staticfiles
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # 添加静态文件目录

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 200  # 200MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 200  # 200MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.TemporaryFileUploadHandler"
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 会话设置
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 3600 * 2  # 2小时，与JWT一致
SESSION_COOKIE_SECURE = False  # 开发时设为False，生产环境应为True
SESSION_COOKIE_HTTPONLY = True

# 日志设置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose'
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'notice': {  # 修改为公告应用的日志
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# 自定义异常处理
def custom_exception_handler(exc, context):
    """
    自定义DRF异常处理，提供更友好的错误信息
    """
    from rest_framework.views import exception_handler

    # 调用默认异常处理
    response = exception_handler(exc, context)

    if response is not None:
        # 自定义错误响应格式
        custom_data = {
            'error': True,
            'message': str(exc),
            'code': response.status_code,
            'details': {}
        }

        # 添加额外错误详情
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                custom_data['details'] = exc.detail
            elif isinstance(exc.detail, list):
                custom_data['message'] = '; '.join(exc.detail)

        response.data = custom_data

    return response