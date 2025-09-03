from django.urls import path, include
from .views import (
    ExperimentViewSet,
    ChoiceProblemViewSet,
    FillProblemViewSet,
    CodingProblemViewSet,
    SubmissionViewSet,
    AnswerViewSet,
    ExperimentDetailView,
    CodingProblemDetailApi,
    CodeJudgeApi,
    SubmitExperimentApi
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'experiments', ExperimentViewSet, basename='experiment')
router.register(r'choice-problems', ChoiceProblemViewSet, basename='choice-problem')
router.register(r'fill-problems', FillProblemViewSet, basename='fill-problem')
router.register(r'coding-problems', CodingProblemViewSet, basename='coding-problem')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'answers', AnswerViewSet, basename='answer')

urlpatterns = [
    # 包含自动生成的ViewSet路由
    path('', include(router.urls)),
    
    # 实验详情视图
    path('experiments/<int:experiment_id>/problems/', ExperimentDetailView.as_view(), name='experiment_detail'),
    
    # 编程题详情视图
    path('experiments/<int:experiment_id>/coding/<int:problem_id>/', 
         CodingProblemDetailApi.as_view(), name='coding_problem_detail'),
    
    # 代码评测端点
    path('judge/', CodeJudgeApi.as_view(), name='code_judge'),
    
    # 实验提交端点
    path('submit-experiment/', SubmitExperimentApi.as_view(), name='submit_experiment'),
]