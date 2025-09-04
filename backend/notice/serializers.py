from rest_framework import serializers
from .models import Notice
from experiments.models import Experiment
from django.contrib.auth import get_user_model

User = get_user_model()


class NoticeSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()
    experiment_info = serializers.SerializerMethodField()
    # 新增：当前用户是否已读
    is_read = serializers.SerializerMethodField()
    # 新增：总阅读用户数
    read_count = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'content', 'type', 'date', 'is_top',
            'author_name', 'formatted_date', 'experiment_info',
            'is_read', 'read_count'  # 新增字段
        ]
        read_only_fields = ['date', 'read_count', 'is_read']  # 设置为只读

    def get_author_name(self, obj):
        return obj.author.username if obj.author else "未知"

    def get_formatted_date(self, obj):
        return obj.date.strftime('%Y-%m-%d %H:%M') if obj.date else None

    def get_experiment_info(self, obj):
        if obj.experiment:
            return {
                'id': obj.experiment.id,
                'name': obj.experiment.name
            }
        return None

    def get_is_read(self, obj):
        """检查当前用户是否已读"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_read_by(request.user)
        return False

    def get_read_count(self, obj):
        """获取已读用户数量"""
        return obj.readers.count()

    def create(self, validated_data):
        """创建公告时自动设置作者"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)