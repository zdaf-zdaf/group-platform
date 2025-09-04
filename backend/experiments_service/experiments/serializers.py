# experiment/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Experiment, ChoiceProblem, FillProblem, CodingProblem,
    Submission, Answer, CodingSubmission, TestResult
)
from django.contrib.contenttypes.models import ContentType


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        read_only_fields = ('id',)

class StudentSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'name']
    
    def get_name(self, obj):
        return f"{obj.last_name}{obj.first_name}" if obj.last_name else obj.username

class ChoiceProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceProblem
        fields = '__all__'


class FillProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FillProblem
        fields = '__all__'


class CodingProblemSerializer(serializers.ModelSerializer):
    test_cases = serializers.JSONField()
    class Meta:
        model = CodingProblem
        fields = [
            'description', 'test_cases', 'timeout',
            'mem_limit', 'experiment', 'score', 'order' ,
            "id"    # 移除 'id'
        ]
        extra_kwargs = {
            'id': {'read_only': True}  # 明确标记id为只读
        }


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ['id', 'test_case_input', 'expected_output','actual_output', 'is_passed']


class AnswerSerializer(serializers.ModelSerializer):
    submission_id = serializers.IntegerField(write_only=True)
    question_type = serializers.CharField(write_only=True)
    question_id = serializers.IntegerField(write_only=True)

    # 只读字段
    question_type_display = serializers.SerializerMethodField(read_only=True)
    prompt = serializers.SerializerMethodField()
    correct_answer = serializers.SerializerMethodField()
    student_answer = serializers.SerializerMethodField()
    test_results = TestResultSerializer(many=True, read_only=True)
    file = serializers.FileField(allow_null=True, required=False)

    class Meta:
        model = Answer
        fields = [
            'id',"submission", "submission_id",  'question_type', 'question_type_display',
            'question_id', 'prompt', 'correct_answer', 'student_answer',
            'answer_text', 'code', 'file', 'is_passed', 'test_results'
        ]

    def validate_question_type(self, value):
        if value not in ['choice', 'fill', 'coding']:
            raise serializers.ValidationError("题目类型必须是 'choice'、'fill' 或 'coding'")
        return value

    def create(self, validated_data):
        submission_id = validated_data.pop('submission_id')
        question_type = validated_data.pop('question_type')
        question_id = validated_data.pop('question_id')
        try:
            submission = Submission.objects.get(id=submission_id)
        except Submission.DoesNotExist:
            raise serializers.ValidationError({'submission_id': '提交记录不存在'})
        model_map = {
            'choice': ChoiceProblem,
            'fill': FillProblem,
            'coding': CodingProblem
        }

        model_class = model_map.get(question_type)
        if not model_class:
            raise serializers.ValidationError({'question_type': '不支持的题型'})

        try:
            content_type = ContentType.objects.get_for_model(model_class)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError({'content_type': '找不到对应的 ContentType'})

        answer = Answer.objects.create(
            submission=submission,
            content_type=content_type,
            object_id=question_id,
            **validated_data
        )
        return answer

    # 以下是只读展示字段处理
    def get_question_type_display(self, obj):
        model_name = obj.content_type.model_class().__name__
        return {
            'ChoiceProblem': '选择题',
            'FillProblem': '填空题',
            'CodingProblem': '编程题'
        }.get(model_name, '未知题型')

    def get_prompt(self, obj):
        return getattr(obj.question, 'description', '')

    def get_correct_answer(self, obj):
        model_name = obj.content_type.model_class().__name__
        if model_name in ['ChoiceProblem', 'FillProblem']:
            return getattr(obj.question, 'correct_answer', '')
        return None

    def get_student_answer(self, obj):
        model_name = obj.content_type.model_class().__name__
        if model_name in ['ChoiceProblem', 'FillProblem']:
            return obj.answer_text
        elif model_name == 'CodingProblem':
            return obj.code
        return None



class CodingSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingSubmission
        fields = '__all__'

# 原QuestionSetSerializer
class ExperimentSerializer(serializers.ModelSerializer):
    choice_problems = ChoiceProblemSerializer(many=True, read_only=True)
    fill_problems = FillProblemSerializer(many=True, read_only=True)
    coding_problems = CodingProblemSerializer(many=True, read_only=True)
    students = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role__iexact='student'), many=True)
    teacher = UserSerializer(read_only=True)
    has_submission = serializers.SerializerMethodField()
    start_time = serializers.DateTimeField()
    deadline = serializers.DateTimeField()
    allow_late_submission = serializers.BooleanField(default=False)
    late_submission_penalty = serializers.IntegerField(default=0)  # 存储百分比值
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Experiment
        fields = [
            'id', 'title', 'start_time', 'deadline', 'created_at',
            'teacher', 'students',
            'choice_problems', 'fill_problems', 'coding_problems',
            'has_submission',
            'allow_late_submission', 'late_submission_penalty',
            'description',
        ]

    def get_has_submission(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Submission.objects.filter(experiment=obj, user=user).exists()


class SubmissionSerializer(serializers.ModelSerializer):
    studentId = serializers.IntegerField(source='user.id', read_only=True)
    studentName = serializers.CharField(source='user.username', read_only=True)
    setId = serializers.IntegerField(source='experiment.id', read_only=True)
    setTitle = serializers.CharField(source='experiment.title', read_only=True)
    deadline = serializers.DateTimeField(source='experiment.deadline', read_only=True)
    submittedAt = serializers.DateTimeField(source='submitted_at', read_only=True)
    passed = serializers.BooleanField(source='is_passed', read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    class Meta:
        model = Submission
        # 去掉 answers 和原来的 student、experiment 字段，替换为自定义的简化字段
        fields = ['id', 'studentId', 'studentName', 'setId', 'setTitle', 'deadline', 'submittedAt', 'passed', 'answers']

