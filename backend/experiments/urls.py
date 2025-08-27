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
    SubmitExperimentApi,
    AnswerCreateView

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
    # path('experiments/<int:experiment_id>/problems/', ExperimentProblemsApi.as_view(), name='experiment_problems'),
    path('experiments/<int:experiment_id>/problems/', ExperimentDetailView.as_view(), name='experiment_detail'),
    path('experiments/<int:experiment_id>/coding/<int:problem_id>/', CodingProblemDetailApi.as_view(), name='coding_problem_detail'),
    path('judge/', CodeJudgeApi.as_view(), name='code_judge'),
    path('answers/', AnswerCreateView.as_view(), name='answer-create'),
    # path('submit-experiment/', SubmitExperimentApi.as_view(), name='submit_experiment'),
]
