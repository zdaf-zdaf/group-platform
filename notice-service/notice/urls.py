from django.urls import path
from .views import NoticeViewSet

urlpatterns = [
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