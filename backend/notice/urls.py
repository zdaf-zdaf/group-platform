from django.urls import path
from .views import NoticeViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'notices', NoticeViewSet, basename='notice')

urlpatterns = [
    # 标准CRUD操作
    path('', NoticeViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='notice-list'),

    path('<int:pk>/', NoticeViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='notice-detail'),

    # 新增：阅读状态管理API
    path('<int:pk>/mark_as_read/', NoticeViewSet.as_view({
        'post': 'mark_as_read'
    }), name='notice-mark-read'),

    path('mark_all_read/', NoticeViewSet.as_view({
        'post': 'mark_all_read'
    }), name='mark-all-read'),

    path('unread_count/', NoticeViewSet.as_view({
        'get': 'unread_count'
    }), name='notice-unread-count'),
]