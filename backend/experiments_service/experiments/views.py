import logging
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .models import (
    Experiment, ChoiceProblem, FillProblem, CodingProblem,
    Submission, Answer, CodingSubmission, TestResult
)
from .serializers import (
    ExperimentSerializer, ChoiceProblemSerializer, FillProblemSerializer,
    CodingProblemSerializer, SubmissionSerializer, AnswerSerializer,
    TestResultSerializer
)
from .docker_execute import DockerJudge

logger = logging.getLogger('experiment')

class ExperimentViewSet(viewsets.ModelViewSet):
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        logger.debug(f"创建实验请求 - 用户ID: {user.id}, 角色: {getattr(user, 'role', '未定义')}")
        
        if not hasattr(user, 'role') or user.role != 'teacher':
            logger.warning(f"权限拒绝 - 用户 {user.id} 角色不是教师")
            return Response({"detail": "只有教师可以创建实验"}, status=status.HTTP_403_FORBIDDEN)
        

    def get_queryset(self):
        # 从JWT令牌中获取用户信息
        user = self.request.user
        
        # 根据用户角色过滤实验
        if hasattr(user, 'role') and user.role == 'teacher':
            # 教师可以看到自己创建的所有实验
            return Experiment.objects.filter(teacher_id=user.id)
        else:
            # 学生只能看到分配给自己的实验
            return Experiment.objects.filter(student_ids__contains=[user.id])
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id != instance.teacher_id:
            return Response({"error": "无权删除"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id != instance.teacher_id:
            return Response({"error": "无权修改"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        experiment = self.get_object()
        submissions = Submission.objects.filter(experiment=experiment)
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def problems(self, request, pk=None):
        try:
            experiment = self.get_object()
            choice_problems = ChoiceProblem.objects.filter(experiment=experiment)
            fill_problems = FillProblem.objects.filter(experiment=experiment)
            coding_problems = CodingProblem.objects.filter(experiment=experiment)

            choice_data = ChoiceProblemSerializer(choice_problems, many=True).data
            fill_data = FillProblemSerializer(fill_problems, many=True).data
            coding_data = CodingProblemSerializer(coding_problems, many=True).data

            for q in choice_data:
                q['type'] = 'choice'
            for q in fill_data:
                q['type'] = 'fill'
            for q in coding_data:
                q['type'] = 'coding'

            questions = sorted(choice_data + fill_data + coding_data, key=lambda q: q.get('order', 0))
            return Response({'questions': questions})
        except Experiment.DoesNotExist:
            return Response({'error': '实验不存在'}, status=status.HTTP_404_NOT_FOUND)

class ChoiceProblemViewSet(viewsets.ModelViewSet):
    queryset = ChoiceProblem.objects.all()
    serializer_class = ChoiceProblemSerializer
    permission_classes = [permissions.IsAuthenticated]

class FillProblemViewSet(viewsets.ModelViewSet):
    queryset = FillProblem.objects.all()
    serializer_class = FillProblemSerializer
    permission_classes = [permissions.IsAuthenticated]

class CodingProblemViewSet(viewsets.ModelViewSet):
    queryset = CodingProblem.objects.all()
    serializer_class = CodingProblemSerializer
    permission_classes = [permissions.IsAuthenticated]

class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'teacher':
            return Submission.objects.filter(experiment__teacher_id=user.id)
        return Submission.objects.filter(user_id=user.id)
    
    @action(detail=True, methods=['post'])
    def submit_answers(self, request, pk=None):
        submission = self.get_object()
        answers_data = request.data.get('answers', [])
        
        # 检查是否已过截止时间
        if timezone.now() > submission.experiment.deadline:
            return Response({'error': '已过截止时间，无法提交'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 处理每个答案
        for answer_data in answers_data:
            question_id = answer_data.get('question_id')
            answer_text = answer_data.get('answer_text')
            code = answer_data.get('code')
            
            answer, created = Answer.objects.get_or_create(
                submission=submission,
                content_type=ContentType.objects.get_for_model(ChoiceProblem),
                object_id=question_id,
                defaults={
                    'answer_text': answer_text,
                    'code': code
                }
            )
            
            if not created:
                answer.answer_text = answer_text
                answer.code = code
                answer.save()
        
        return Response({'message': '答案提交成功'})

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # 判断是否是批量数据
        is_many = isinstance(request.data, list)
        serializer = AnswerSerializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        instances = serializer.save()
        response_serializer = AnswerSerializer(instances, many=is_many)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        answer = self.get_object()
        is_passed = request.data.get('is_passed', False)

        answer.is_passed = is_passed
        answer.save()

        # 更新提交状态
        submission = answer.submission
        all_answers_passed = submission.answers.exclude(is_passed=True).count() == 0
        submission.is_passed = all_answers_passed
        submission.save()

        return Response({'message': '批改结果已保存'})

class ExperimentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, experiment_id):
        try:
            experiment = get_object_or_404(Experiment, id=experiment_id)
            user = request.user
            
            # 检查用户是否有权限访问该实验
            if user.role == 'student' and user.id not in experiment.student_ids:
                return Response({'error': '无权访问此实验'}, status=status.HTTP_403_FORBIDDEN)
            
            # 获取实验详情
            serializer = ExperimentSerializer(experiment)
            return Response(serializer.data)
        except Experiment.DoesNotExist:
            return Response({'error': '实验不存在'}, status=status.HTTP_404_NOT_FOUND)

class CodingProblemDetailApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, experiment_id, problem_id):
        try:
            experiment = get_object_or_404(Experiment, id=experiment_id)
            problem = get_object_or_404(CodingProblem, id=problem_id, experiment=experiment)
            
            # 检查用户是否有权限访问
            user = request.user
            if user.role == 'student' and user.id not in experiment.student_ids:
                return Response({'error': '无权访问此题目'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = CodingProblemSerializer(problem)
            return Response(serializer.data)
        except (Experiment.DoesNotExist, CodingProblem.DoesNotExist):
            return Response({'error': '题目不存在'}, status=status.HTTP_404_NOT_FOUND)

class CodeJudgeApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # 从JWT令牌中获取用户信息
        user = request.user
        
        code = request.data.get('code')
        problem_id = request.data.get('problemId')
        
        try:
            problem = CodingProblem.objects.get(id=problem_id)
            
            # 检查用户是否有权限访问该题目
            if user.role == 'student' and user.id not in problem.experiment.student_ids:
                return Response({'error': '无权访问此题目'}, status=status.HTTP_403_FORBIDDEN)
            
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
                user_id=user.id,
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
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        # 从JWT令牌中获取用户信息
        user = request.user
        
        try:
            data = request.data
            experiment_id = data.get('experiment_id')
            answers = data.get('answers', {})
            
            # 获取实验
            experiment = Experiment.objects.get(id=experiment_id)
            
            # 检查用户是否有权限提交
            if user.role == 'student' and user.id not in experiment.student_ids:
                return Response({'error': '无权提交此实验'}, status=status.HTTP_403_FORBIDDEN)
            
            # 检查是否已过截止时间
            if timezone.now() > experiment.deadline and not experiment.allow_late_submission:
                return Response({'error': '已过截止时间，无法提交'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建提交记录
            submission = Submission.objects.create(
                experiment=experiment,
                user_id=user.id
            )
            
            total_score = 0
            choice_results = []
            fill_results = []
            coding_results = []  # 初始化编程题结果列表
            
            # 处理选择题答案
            for choice in answers.get('choice', []):
                problem = ChoiceProblem.objects.get(id=choice['question_id'])
                selected = choice.get('selected')
                is_correct = int(selected) == int(problem.correct_answer)
                
                if is_correct:
                    total_score += problem.score
                
                choice_results.append({
                    'question_id': problem.id,
                    'selected': selected,
                    'is_correct': is_correct,
                    'score': problem.score
                })
                
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
                
                if is_correct:
                    total_score += problem.score
                
                fill_results.append({
                    'question_id': problem.id,
                    'answer': answer_text,
                    'is_correct': is_correct,
                    'score': problem.score
                })
                
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
                
                if passed:
                    total_score += problem.score
                
                # 创建编程题提交记录
                coding_submission = CodingSubmission.objects.create(
                    coding_problem=problem,
                    user_id=user.id,
                    code=code,
                    passed_count=result['passed'],
                    total_count=result['total'],
                    details=result['details']
                )
                
                # 创建答案记录
                answer = Answer.objects.create(
                    submission=submission,
                    content_type=ContentType.objects.get_for_model(CodingProblem),
                    object_id=problem.id,
                    code=code,
                    is_passed=passed
                )
                
                # 创建测试结果记录
                for case in result['details']:
                    TestResult.objects.create(
                        answer=answer,
                        test_case_input=case.get('input', ''),
                        expected_output=case.get('expected', ''),
                        actual_output=case.get('actual', ''),
                        is_passed=case.get('is_passed', False)
                    )
                
                # 将结果添加到编程题结果列表
                coding_results.append({
                    'question_id': problem.id,
                    'passed': result['passed'],
                    'total': result['total'],
                    'is_passed': passed,
                    'score': problem.score
                })
            
            # 更新提交状态
            all_passed = all(
                [r['is_correct'] for r in choice_results] +
                [r['is_correct'] for r in fill_results] +
                [r['is_passed'] for r in coding_results]
            )
            submission.is_passed = all_passed
            submission.save()
            
            return Response({
                'success': True,
                'submission_id': submission.id,
                'is_passed': all_passed,
                'total_score': total_score,
                'results': {
                    'choice': choice_results,
                    'fill': fill_results,
                    'coding': coding_results
                }
            }, status=status.HTTP_200_OK)
        
        except Experiment.DoesNotExist:
            return Response({'error': '实验不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"提交实验失败: {str(e)}")
            return Response({'error': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)