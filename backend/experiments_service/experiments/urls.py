from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/experiments/', include('experiments.urls')),  # 只保留 experiments 自己的路由
]
