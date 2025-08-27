from django.contrib import admin
from django.conf import settings
from django.db import router
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from forum import views as forum_views
from experiments import views
from experiments.views import CodeJudgeApi, CodingProblemDetailApi
from materials.views import LearningMaterialViewSet
from user.views import (
    RegisterView,
    CustomTokenObtainPairView,
    StudentListView,
    TeacherTestView,
    StudentTestView,
    UserProfileUpdateView
)
from experiments.views import ExperimentViewSet, SubmissionViewSet, AnswerViewSet, StudentViewSet

router = DefaultRouter()
router.register(r'materials', LearningMaterialViewSet, basename='material')

urlpatterns = [
    path('admin/', admin.site.urls),
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
    path('api/students/', StudentListView.as_view(), name='student-list'),
    path('api/notices/', include('notice.urls')),
    path('api/', include([
        path('experiments/', include('experiments.urls')),
    ])),
    path('judge/', CodeJudgeApi.as_view(), name="judge"),
    path('experiment/<int:experiment_id>/', views.ExperimentDetailView.as_view(), name='experiment_detail'),
    # path('submission/status/<int:experiment_id>/', views.SubmissionStatusApi.as_view(), name='submission_status'),
    path('submit/experiment/', views.SubmitExperimentApi.as_view(), name='submit_experiment'),
    path('experiment/<int:experiment_id>/coding/<int:problem_id>/', CodingProblemDetailApi.as_view(), name='coding-problem-detail'),
    path('', include(router.urls)),
    path('api/forum/', include([
        path('questions/', forum_views.QuestionListCreateView.as_view(), name='question-list'),
        path('questions/<int:pk>/', forum_views.QuestionDetailView.as_view(), name='question-detail'),
        path('questions/<int:pk>/toggle-sticky/', forum_views.ToggleStickyView.as_view(), name='toggle-sticky'),
        path('questions/<int:pk>/toggle-like/', forum_views.ToggleLikeView.as_view(), name='toggle-like'),
        path('questions/<int:question_id>/comments/', forum_views.CommentCreateView.as_view(), name='comment-create'),
        path('comments/<int:pk>/', forum_views.CommentDeleteView.as_view(), name='comment-delete'),
    ])),

]

# 修复：正确处理中文字符路径服务
if settings.DEBUG:
    from django.urls import re_path
    from django.views.static import serve

    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]