from django.apps import AppConfig

class ServerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'server'
    
    def ready(self):
        # 在这里导入自定义认证类
        from . import authentication