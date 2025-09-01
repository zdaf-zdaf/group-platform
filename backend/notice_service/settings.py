# 外部服务地址配置
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://user-service:8000')
EXPERIMENT_SERVICE_URL = os.environ.get('EXPERIMENT_SERVICE_URL', 'http://experiment-service:8000')

# 数据库配置（使用独立数据库）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('NOTICE_DB_NAME', 'notice_db'),
        'USER': os.environ.get('NOTICE_DB_USER', 'notice_user'),
        'PASSWORD': os.environ.get('NOTICE_DB_PASSWORD', 'password'),
        'HOST': os.environ.get('NOTICE_DB_HOST', 'localhost'),
        'PORT': os.environ.get('NOTICE_DB_PORT', '5432'),
    }
}