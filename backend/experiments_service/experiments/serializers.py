from rest_framework import serializers
from .models import *
from .clients import UserServiceClient

class UserBriefSerializer(serializers.Serializer):
    """用户简要信息序列化器"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        return obj.get('name', obj['username'])

class ChoiceProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceProblem
        fields = '__all__'

class FillProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FillProblem
        fields = '__all__'

class CodingProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingProblem
        fields = '__all__'

class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    question_type = serializers.SerializerMethodField()
    question_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Answer
        fields = '__all__'
    
    def get_user(self, obj):
        """通过用户服务获取用户信息"""
        client = UserServiceClient()
        return client.get_user_info(obj.submission.user_id)
    
    def get_question_type(self, obj):
        """获取题目类型"""
        model_name = obj.content_type.model_class().__name__
        return {
            'ChoiceProblem': 'choice',
            'FillProblem': 'fill',
            'CodingProblem': 'coding'
        }.get(model_name, 'unknown')
    
    def get_question_info(self, obj):
        """获取题目信息"""
        return {
            'id': obj.object_id,
            'description': obj.question.description if hasattr(obj.question, 'description') else ''
        }

class SubmissionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Submission
        fields = '__all__'
    
    def get_user(self, obj):
        """通过用户服务获取用户信息"""
        client = UserServiceClient()
        return client.get_user_info(obj.user_id)

class ExperimentSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()
    choice_problems = ChoiceProblemSerializer(many=True, read_only=True)
    fill_problems = FillProblemSerializer(many=True, read_only=True)
    coding_problems = CodingProblemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Experiment
        fields = '__all__'
    
    def get_teacher(self, obj):
        """通过用户服务获取教师信息"""
        client = UserServiceClient()
        return client.get_user_info(obj.teacher_id)
    
    def get_students(self, obj):
        """通过用户服务获取学生列表"""
        # 注意：原模型中的students字段已改为存储ID列表
        # 需要修改模型添加students_ids字段
        client = UserServiceClient()
        return [client.get_user_info(user_id) for user_id in obj.students_ids]