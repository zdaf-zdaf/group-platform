import os
from rest_framework import serializers
from .models import LearningMaterial
from django.contrib.auth import get_user_model

User = get_user_model()


class LearningMaterialSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    # 改为整型字段，保持与模型一致，由网关/上游负责合法性校验
    question_set = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = LearningMaterial
        fields = [
            'id', 'title', 'description', 'type', 'file', 'file_url', 'file_name',
            'size', 'downloads', 'created_at', 'created_by', 'question_set'
        ]
        read_only_fields = ['size', 'downloads', 'created_at', 'created_by', 'file_name']

    def validate_file(self, value):
        if not value:
            raise serializers.ValidationError("必须上传文件")

        max_size = 200 * 1024 * 1024  # 100MB
        if value.size > max_size:
            raise serializers.ValidationError(f"文件大小不能超过{max_size / 1024 / 1024}MB")

        # 验证文件类型
        valid_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.jpg', '.png', '.mp4']
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError("不支持的文件类型")

        return value

    def get_file_url(self, obj):
        # 修复：生成相对 URL 而不是绝对 URL
        if obj.file and hasattr(obj.file, 'url'):
            return obj.file.url
        return None

    def get_file_name(self, obj):
        if obj.file:
            return os.path.basename(obj.file.name)
        return None