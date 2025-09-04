from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.views.static import serve
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

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

# 如果 forum 没有完全拆分，可以做一个假的 namespace 占位
try:
    from forum import views as forum_views
except ImportError:
    from django.views import View
    from django.http import JsonResponse

    class DummyView(View):
        def get(self, request, *args, **kwargs):
            return JsonResponse({"msg": "stub forum"})

    class forum_views:
        QuestionListCreateView = DummyView
        QuestionDetailView = DummyView
        ToggleStickyView = DummyView
        ToggleLikeView = DummyView
        CommentCreateView = DummyView
        CommentDeleteView = DummyView


def health_check(request):
    return JsonResponse({"status": "ok"})


router = DefaultRouter()
router.register(r'materials', LearningMaterialViewSet, basename='material')
router.register(r'experiments', views.ExperimentViewSet, basename='experiment')

urlpatterns = [
    path("health/", health_check),   # 健康检查接口
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

    # 实验系统相关
    path('judge/', CodeJudgeApi.as_view(), name="judge"),
    path('experiment/<int:experiment_id>/', views.ExperimentViewSet.as_view({'get': 'retrieve'}), name='experiment_detail'),
    path('submit/experiment/', views.ExperimentViewSet.as_view({'post': 'create'}), name='submit_experiment'),
    path('experiment/<int:experiment_id>/coding/<int:problem_id>/', CodingProblemDetailApi.as_view(), name='coding-problem-detail'),

    # 论坛相关
    path('api/forum/', include([
        path('questions/', forum_views.QuestionListCreateView.as_view(), name='question-list'),
        path('questions/<int:pk>/', forum_views.QuestionDetailView.as_view(), name='question-detail'),
        path('questions/<int:pk>/toggle-sticky/', forum_views.ToggleStickyView.as_view(), name='toggle-sticky'),
        path('questions/<int:pk>/toggle-like/', forum_views.ToggleLikeView.as_view(), name='toggle-like'),
        path('questions/<int:question_id>/comments/', forum_views.CommentCreateView.as_view(), name='comment-create'),
        path('comments/<int:pk>/', forum_views.CommentDeleteView.as_view(), name='comment-delete'),
    ])),

    path('', include(router.urls)),
]

# 开发模式下静态文件
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
