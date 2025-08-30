
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from user.views import (
    RegisterView,
    CustomTokenObtainPairView,
    TeacherTestView,
    StudentTestView,
    UserProfileUpdateView
)

urlpatterns = [
    path('api/auth/', include([
        path('register/', RegisterView.as_view(), name='register'),
        path('login/', CustomTokenObtainPairView.as_view(), name='login'),
        path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('user/profile/', UserProfileUpdateView.as_view(), name='user_profile_update'),
    ])),
    path('api/test/', include([
        path('teacher/', TeacherTestView.as_view(), name='teacher-test'),
        path('student/', StudentTestView.as_view(), name='student-test'),
    ])),
]
