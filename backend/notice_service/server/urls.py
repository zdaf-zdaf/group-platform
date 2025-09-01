from django.urls import path, include
from django.http import JsonResponse
from django.db import connections
from notice_app import urls as notice_urls
from django.views.decorators.http import require_GET

@require_GET
def health_check(request):
    """健康检查端点 - 验证服务是否运行"""
    return JsonResponse({
        'status': 'OK',
        'service': 'notice-service',
        'version': '1.0.0'
    })

@require_GET
def ready_check(request):
    """就绪检查端点 - 验证服务是否准备好接收流量"""
    try:
        # 检查数据库连接
        db_conn = connections['default']
        db_conn.ensure_connection()
        
        # 检查外部服务连通性
        from . import settings
        services = {
            'user_service': settings.USER_SERVICE_URL,
            'experiment_service': settings.EXPERIMENT_SERVICE_URL
        }
        
        status = {'database': 'connected'}
        
        # 返回完整就绪状态
        return JsonResponse({
            'status': 'READY',
            'database': 'connected',
            'services': services
        })
    except Exception as e:
        return JsonResponse({
            'status': 'NOT_READY',
            'error': str(e)
        }, status=503)

@require_GET
def prometheus_metrics(request):
    """Prometheus 监控端点"""
    from django_prometheus.exports import ExportToDjangoView
    return ExportToDjangoView(request)

urlpatterns = [
    # 公告服务API
    path('api/', include(notice_urls)),
    
    # 健康检查端点
    path('health/', health_check, name='health-check'),
    
    # 就绪检查端点
    path('ready/', ready_check, name='ready-check'),
    
    # Prometheus 监控端点
    path('metrics/', prometheus_metrics, name='prometheus-metrics'),
    
    # 根路径重定向到健康检查
    path('', health_check),
]