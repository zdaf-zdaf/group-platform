from django.urls import path, include

urlpatterns = [
    path('api/notices/', include('notice.urls')),
]