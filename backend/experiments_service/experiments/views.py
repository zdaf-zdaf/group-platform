from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Experiment
from .serializers import ExperimentSerializer


# 实验管理
class ExperimentViewSet(viewsets.ModelViewSet):
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer


# ====== 补充的 Stub 类（避免 ImportError） ======
class CodeJudgeApi(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"msg": "stub CodeJudgeApi GET"})

    def post(self, request, *args, **kwargs):
        return Response({"msg": "stub CodeJudgeApi POST"})


class CodingProblemDetailApi(APIView):
    def get(self, request, experiment_id=None, problem_id=None, *args, **kwargs):
        return Response({
            "msg": "stub CodingProblemDetailApi GET",
            "experiment_id": experiment_id,
            "problem_id": problem_id
        })

    def post(self, request, experiment_id=None, problem_id=None, *args, **kwargs):
        return Response({
            "msg": "stub CodingProblemDetailApi POST",
            "experiment_id": experiment_id,
            "problem_id": problem_id
        })


# 额外的占位 ViewSet，避免 urls.py 引用时报错
class SubmissionViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response([])


class AnswerViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response([])


class StudentViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response([])
