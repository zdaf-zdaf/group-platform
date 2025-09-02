from django.apps import AppConfig

class ServerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'server'
    
    def ready(self):
        # 延迟导入自定义认证类
        from . import authentication
        print("Custom authentication class loaded")