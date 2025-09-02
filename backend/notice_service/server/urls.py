from django.urls import path, include

urlpatterns = [
    path('api/notice/', include('notice.urls')),
]