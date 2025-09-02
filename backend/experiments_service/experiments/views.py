from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from .services import ExperimentService
from .docker_execute import DockerJudge
import logging
import json
from django.db import transaction

logger = logging.getLogger('experiment_app')

class ExperimentViewSet(viewsets.ModelViewSet):
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """创建实验（只允许教师操作）"""
        # 验证当前用户是否为教师
        if not ExperimentService.validate_teacher_role(request.user.id):
            return Response({"detail": "无权限操作"}, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

class CodeJudgeApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """代码评测API"""
        code = request.data.get('code')
        problem_id = request.data.get('problemId')
        
        try:
            problem = CodingProblem.objects.get(id=problem_id)
            problem_config = {
                "name": problem.description,
                "timeout": problem.timeout,
                "mem_limit": problem.mem_limit,
                "test_cases": problem.test_cases
            }
            
            judge = DockerJudge()
            result = judge.run_code(problem_config, code)
            
            # 保存提交记录
            submission = CodingSubmission.objects.create(
                coding_problem=problem,
                user_id=request.user.id,
                code=code,
                passed_count=result['passed'],
                total_count=result['total'],
                details=result['details']
            )
            
            return Response({'result': result}, status=status.HTTP_200_OK)
        except CodingProblem.DoesNotExist:
            return Response({'error': '题目不存在'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"代码评测失败: {str(e)}")
            return Response({'error': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SubmitExperimentApi(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        """提交实验答案"""
        try:
            data = request.data
            experiment_id = data.get('experiment_id')
            answers = data.get('answers', {})
            
            # 获取实验
            experiment = Experiment.objects.get(id=experiment_id)
            
            # 检查是否已过截止时间
            if timezone.now() > experiment.deadline and not experiment.allow_late_submission:
                return Response({'error': '已过截止时间，无法提交'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建提交记录
            submission = Submission.objects.create(
                experiment=experiment,
                user_id=request.user.id
            )
            
            # 处理选择题答案
            for choice in answers.get('choice', []):
                problem = ChoiceProblem.objects.get(id=choice['question_id'])
                selected = choice.get('selected')
                is_correct = int(selected) == int(problem.correct_answer)
                
                Answer.objects.create(
                    submission=submission,
                    content_type=ContentType.objects.get_for_model(ChoiceProblem),
                    object_id=problem.id,
                    answer_text=selected,
                    is_passed=is_correct
                )
            
            # 处理填空题答案
            for fill in answers.get('fill', []):
                problem = FillProblem.objects.get(id=fill['question_id'])
                answer_text = fill.get('answer', '').strip()
                is_correct = answer_text.lower() == problem.correct_answer.lower()
                
                Answer.objects.create(
                    submission=submission,
                    content_type=ContentType.objects.get_for_model(FillProblem),
                    object_id=problem.id,
                    answer_text=answer_text,
                    is_passed=is_correct
                )
            
            # 处理编程题答案
            judge = DockerJudge()
            for coding in answers.get('coding', []):
                problem = CodingProblem.objects.get(id=coding['question_id'])
                code = coding.get('code', '')
                problem_config = {
                    "name": problem.description,
                    "timeout": problem.timeout,
                    "mem_limit": problem.mem_limit,
                    "test_cases": problem.test_cases
                }
                
                result = judge.run_code(problem_config, code)
                passed = result['passed'] == result['total']
                
                # 创建编程题提交记录
                coding_submission = CodingSubmission.objects.create(
                    coding_problem=problem,
                    user_id=request.user.id,
                    code=code,
                    passed_count=result['passed'],
                    total_count=result['total'],
                    details=result['details']
                )
                
                # 创建答案记录
                Answer.objects.create(
                    submission=submission,
                    content_type=ContentType.objects.get_for_model(CodingProblem),
                    object_id=problem.id,
                    code=code,
                    is_passed=passed
                )
            
            # 更新提交状态
            all_passed = all(answer.is_passed for answer in submission.answers.all())
            submission.is_passed = all_passed
            submission.save()
            
            return Response({
                'success': True,
                'submission_id': submission.id,
                'is_passed': all_passed
            }, status=status.HTTP_200_OK)
        
        except Experiment.DoesNotExist:
            return Response({'error': '实验不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"提交实验失败: {str(e)}")
            return Response({'error': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)