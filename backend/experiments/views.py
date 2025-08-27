# experiments\views.py
import json

from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
from django.http import JsonResponse
from django.conf import settings
from .models import (Experiment, ChoiceProblem, FillProblem, CodingProblem,
    Submission, Answer, CodingSubmission, TestResult)
from .serializers import (
    ExperimentSerializer,
    ChoiceProblemSerializer,
    FillProblemSerializer,
    CodingProblemSerializer,
    SubmissionSerializer,
    AnswerSerializer, TestResultSerializer,
    StudentSerializer)
from django.contrib.auth import get_user_model
from .docker_execute import DockerJudge
from datetime import datetime
from django.db import transaction  # 替换原来的 import transaction

User = get_user_model()

# ------------------- 基础 API 接口 -------------------

class AnswerCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            print("【提交答案】请求数据:", request.data)

            # 判断是否是批量数据
            is_many = isinstance(request.data, list)
            serializer = AnswerSerializer(data=request.data, many=is_many)
            serializer.is_valid(raise_exception=True)

            instances = serializer.save()
            response_serializer = AnswerSerializer(instances, many=is_many)

            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("【提交答案】创建失败:", str(e))
            return Response({"non_field_errors": [str(e)]}, status=status.HTTP_400_BAD_REQUEST)
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            print("【提交答案】请求数据:", request.data)

            # 判断是否是批量提交
            many = isinstance(request.data, list)
            serializer = AnswerSerializer(data=request.data, many=many)

            serializer.is_valid(raise_exception=True)
            instances = serializer.save()

            # 批量提交返回多个答案结果
            response_serializer = AnswerSerializer(instances, many=many)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("【提交答案】创建失败:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        print("数据类型:", type(request.data), "内容:", request.data)


class CodingProblemDetailApi(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, experiment_id, problem_id):
        try:
            experiment = Experiment.objects.get(id=experiment_id)
            problem = CodingProblem.objects.get(id=problem_id, experiment=experiment)
            serializer = CodingProblemSerializer(problem)
            return JsonResponse(serializer.data, status=200)
        except Experiment.DoesNotExist:
            return JsonResponse({'error': '实验不存在'}, status=404)
        except CodingProblem.DoesNotExist:
            return JsonResponse({'error': '编程题不存在'}, status=404)

class CodeJudgeApi(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code = request.data.get('code')
        problem_id = request.data.get('problemId')
        print("接收到的 problemId:", problem_id)
        try:
            problem = CodingProblem.objects.get(id=problem_id)
            problem_config = {
                "name": problem.description,
                "timeout": problem.timeout,
                "mem_limit": problem.mem_limit,
                "test_cases": problem.test_cases
            }
            judge = DockerJudge()
            print("开始调用 DockerJudge.run_code")
            print("当前用户:", request.user)
            print("是否认证:", request.user.is_authenticated)

            result = judge.run_code(problem_config, code)
            print("DockerJudge.run_code 执行完成，结果:", result)

            submission = CodingSubmission.objects.create(
                coding_problem=problem,
                user=request.user,  # 绑定当前用户
                code=code,
                passed_count=result['passed'],
                total_count=result['total'],
                details=result['details']
            )

            problem.last_submission_status = {
                "submission_id": submission.id,
                "passed": result['passed'],
                "total": result['total'],
                "timestamp": submission.created_at.isoformat(),
            }
            problem.save()

            return JsonResponse({'result': result}, status=200)
        except CodingProblem.DoesNotExist:
            return JsonResponse({'error': '题目不存在'}, status=400)

class SubmitExperimentApi(APIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        try:
            data = request.data
            experiment_id = data.get('experiment_id')
            answers = data.get('answers') or {}

            if not experiment_id:
                return JsonResponse({'success': False, 'message': '缺少 experiment_id'}, status=400)

            experiment = Experiment.objects.get(id=experiment_id)
            user = request.user
            judge = DockerJudge()

            # 准备存储判题结果和 answer 数据
            choice_results, fill_results, coding_results = [], [], []
            total_score = 0  # ✅ 初始化总分

            # === 创建提交记录 ===
            submission = Submission.objects.create(
                experiment=experiment,
                user=user
            )

            # === 判题并保存选择题 ===
            for choice in answers.get('choice', []):
                problem = ChoiceProblem.objects.get(id=choice['question_id'])
                selected = choice.get('selected')
                is_correct = int(selected) == int(problem.correct_answer)
                # ✅ 累加分数
                if is_correct:
                    total_score += problem.score

                choice_results.append({
                    'question_id': problem.id,
                    'selected': selected,
                    'correct_answer': problem.correct_answer,
                    'is_correct': is_correct,
                    'score': problem.score  # ✅ 返回每题分数
                })
                Answer.objects.create(
                    submission=submission,
                    content_type=ContentType.objects.get_for_model(ChoiceProblem),
                    object_id=problem.id,
                    answer_text=selected,
                    is_passed=is_correct
                )

            # === 判题并保存填空题 ===
            for fill in answers.get('fill', []):
                problem = FillProblem.objects.get(id=fill['question_id'])
                answer_text = fill.get('answer', '').strip()
                is_correct = answer_text.lower() == problem.correct_answer.lower()

                if is_correct:
                    total_score += problem.score

                fill_results.append({
                    'question_id': problem.id,
                    'answer': answer_text,
                    'correct_answer': problem.correct_answer,
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

            # === 判题并保存编程题 ===
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

                # 保存 CodingSubmission
                CodingSubmission.objects.create(
                    coding_problem=problem,
                    code=code,
                    passed_count=result['passed'],
                    total_count=result['total'],
                    details=result['details'],
                    user=user
                )

                # 保存 Answer
                passed = result['passed'] == result['total']
                if passed:
                    total_score += problem.score

                coding_results.append({
                    'question_id': problem.id,
                    'passed': result['passed'],
                    'total': result['total'],
                    'is_correct': passed,
                    'score': problem.score
                })
                print("Test case details:", result['details'])
                # 创建 Answer 记录
                answer = Answer.objects.create(
                    submission=submission,
                    content_type=ContentType.objects.get_for_model(CodingProblem),
                    object_id=problem.id,
                    code=code,
                    is_passed=passed
                )

                # 创建 TestResult 记录
                for case in result['details']:
                    TestResult.objects.create(
                        answer=answer,
                        test_case_input=case.get('input', ''),
                        expected_output=case.get('expected', ''),
                        actual_output=case.get('actual', ''),
                        is_passed=case.get('is_passed', False)
                    )

            # === 更新最终是否通过状态 ===
            submission.is_passed = (
                all(c['is_correct'] for c in choice_results) and
                all(f['is_correct'] for f in fill_results) and
                all(c['is_correct'] for c in coding_results)
            )
            submission.save()

            return JsonResponse({
                'success': True,
                'submission_id': submission.id,
                'total_score': total_score,  # ✅ 返回总分
                'results': {
                    'choice': choice_results,
                    'fill': fill_results,
                    'coding': coding_results
                }
            }, status=200)

        except (Experiment.DoesNotExist, ChoiceProblem.DoesNotExist,
                FillProblem.DoesNotExist, CodingProblem.DoesNotExist) as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': str(e)}, status=500)


# ------------------- DRF ViewSet 接口 -------------------
# 原QuestionSetPreviewView
class ExperimentSetPreviewView(viewsets.ModelViewSet):
    """仅创建空题组返回ID"""
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user, title="临时题组")

# 原QuestionSetViewSet
class ExperimentViewSet(viewsets.ModelViewSet):
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # 自动设置教师为当前用户
        experiment = serializer.save(teacher=self.request.user)
        # 处理 students 字段，确保传入的是学生 ID 列表
        students = self.request.data.get('students', [])
        if students:
            experiment.students.set(students)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.teacher:
            return Response({"error": "无权删除"}, status=403)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.teacher:
            return Response({"error": "无权修改"}, status=403)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        question_set = self.get_object()
        submissions = question_set.submissions.all()
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

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
                q['type'] = 'blank'
            for q in coding_data:
                q['type'] = 'code'

            questions = sorted(choice_data + fill_data + coding_data, key=lambda q: q.get('order', 0))
            return Response({'questions': questions})
        except Experiment.DoesNotExist:
            return Response({'error': '实验不存在'}, status=404)

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
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Submission.objects.all()
    '''
        user = self.request.user
        if user.role == 'TEACHER':
            return Submission.objects.filter(experiment__teacher=user).select_related('user', 'experiment')
        return Submission.objects.filter(user=user).select_related('experiment')
    '''
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
                question_id=question_id,
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

    @action(detail=True, methods=['patch'])
    def review_answers(self, request, pk=None):
        submission = self.get_object()
        answers_data = request.data.get('answers', [])

        if not isinstance(answers_data, list):
            return Response({'error': 'answers 必须是列表'}, status=status.HTTP_400_BAD_REQUEST)

        # 批改结果更新
        updated_count = 0
        for ans_data in answers_data:
            ans_id = ans_data.get('id')
            is_passed = ans_data.get('is_passed')

            if ans_id is None or is_passed is None:
                continue

            try:
                answer = Answer.objects.get(id=ans_id, submission=submission)
                answer.is_passed = is_passed
                answer.save()
                updated_count += 1
            except Answer.DoesNotExist:
                continue

        return Response({'message': f'成功更新 {updated_count} 条批改结果'}, status=status.HTTP_200_OK)

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer = serializer.save()  # 调用 AnswerSerializer 的 create()
        return Response(self.get_serializer(answer).data, status=status.HTTP_201_CREATED)

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

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(role='STUDENT')
    serializer_class = StudentSerializer
    permission_classes = [permissions.AllowAny]

# views.py 中新增
class ExperimentDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, experiment_id):
        try:
            timezone.activate(settings.TIME_ZONE)
            experiment = Experiment.objects.get(id=experiment_id)
            current_user = request.user

            user_filter = {'user': current_user} if current_user.is_authenticated else {'user__isnull': True}

            choice_problems = ChoiceProblem.objects.filter(experiment=experiment)
            fill_problems = FillProblem.objects.filter(experiment=experiment)
            coding_problems = CodingProblem.objects.filter(experiment=experiment)

            # 获取 Choice
            choice_data = [
                {
                    "id": q.id,
                    "title": q.description,
                    "options": q.options,
                    "type": "choice"
                } for q in choice_problems
            ]

            # 获取 Fill
            fill_data = [
                {
                    "id": q.id,
                    "title": q.description,
                    "type": "blank"
                } for q in fill_problems
            ]

            # 获取 Coding（含最近3次提交）
            coding_data = []
            for coding_problem in coding_problems:
                submissions = coding_problem.submissions.filter(**user_filter).order_by('-created_at')[:3]
                submission_list = [{
                    "id": sub.id,
                    "passed": sub.passed_count,
                    "total": sub.total_count,
                    "created_at": timezone.localtime(sub.created_at).strftime('%Y-%m-%d %H:%M:%S'),
                    "code": sub.code
                } for sub in submissions]

                coding_data.append({
                    "id": coding_problem.id,
                    "title": getattr(coding_problem, "title", ""),
                    "description": coding_problem.description,
                    "type": "code",
                    "submissions": submission_list,
                    "last_status": coding_problem.last_submission_status
                })

            all_questions = sorted(choice_data + fill_data + coding_data, key=lambda q: q.get('order', 0))

            return JsonResponse({
                "experiment": {
                    "id": experiment.id,
                    "title": experiment.title,
                    "description": experiment.description,
                    "start_time": experiment.start_time,
                    "deadline": experiment.deadline,
                    "allow_late_submission": experiment.allow_late_submission,
                    "late_submission_penalty": experiment.late_submission_penalty,
                    "students": list(experiment.students.values_list('id', flat=True))
                },
                "questions": all_questions
            }, status=200)
        except Experiment.DoesNotExist:
            return JsonResponse({'error': '实验不存在'}, status=404)

    def put(self, request, experiment_id):
        experiment_data = request.data.get('experiment', {})
        # 更新实验集并处理题目
        start_time = parse_datetime(experiment_data['start_time'])
        deadline = parse_datetime(experiment_data['deadline'])
        if is_naive(start_time):
            start_time = make_aware(start_time)
        if is_naive(deadline):
            deadline = make_aware(deadline)
        try:

            experiment = Experiment.objects.get(id=experiment_id)
            experiment.title = experiment_data.get("title")
            experiment.description = experiment_data.get("description", "")
            experiment.start_time = start_time
            experiment.deadline = deadline
            experiment.allow_late_submission = experiment_data.get('allow_late_submission', False)
            experiment.late_submission_penalty = experiment_data.get('late_submission_penalty', 0)
            experiment.save()

            # 处理学生数据
            students = experiment_data.get('selectedStudents', [])
            experiment.students.set(students)

            # 删除现有题目并重新创建
            experiment.choice_problems.all().delete()
            experiment.fill_problems.all().delete()
            experiment.coding_problems.all().delete()

            # 处理题目数据
            for question_data in experiment_data.get('questions', []):
                if question_data['type'] == 'choice':
                    ChoiceProblem.objects.create(
                        experiment=experiment,
                        description=question_data.get('description', ''),
                        options=question_data.get('options', []),
                        correct_answer=question_data.get('correct_answer', ''),
                        score=question_data.get('score', 0),
                        order=question_data.get('order', 0)
                    )
                elif question_data['type'] == 'fill':
                    FillProblem.objects.create(
                        experiment=experiment,
                        description=question_data.get('description', ''),
                        correct_answer=question_data.get('correct_answer', ''),
                        score=question_data.get('score', 0),
                        order=question_data.get('order', 0)
                    )
                elif question_data['type'] == 'coding':
                    CodingProblem.objects.create(
                        experiment=experiment,
                        description=question_data.get('description', ''),
                        test_cases=question_data.get('test_cases', []),
                        timeout=question_data.get('timeout', 1),
                        mem_limit=question_data.get('mem_limit', 128),
                        score=question_data.get('score', 0),
                        order=question_data.get('order', 0)
                    )
            return JsonResponse({'message': '实验集更新成功'}, status=200)
        except Experiment.DoesNotExist:
            return JsonResponse({'error': '实验不存在'}, status=404)
        except Exception as e:
            # 输出异常信息到日志，帮助定位错误
            print(f"Error updating experiment: {e}")
            return JsonResponse({'error': str(e)}, status=400)


