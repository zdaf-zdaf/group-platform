from django.urls import path, include
from notice_app import urls as notice_urls

urlpatterns = [
    path('api/', include(notice_urls)),
    path('health/', lambda r: HttpResponse(status=200)),  # 健康检查
]