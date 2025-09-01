# backend/materials_service/materials/serializers.py

import os
from rest_framework import serializers
from .models import LearningMaterial

# 不再需要导入 User 模型

class LearningMaterialSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    
    # 关键修改：将 uploader_username 作为只读字段暴露
    uploader_username = serializers.CharField(read_only=True)
    
    question_set = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = LearningMaterial
        fields = [
            'id', 'title', 'description', 'type', 'file', 'file_url', 'file_name',
            'size', 'downloads', 'created_at', 'uploader_username', 'question_set'
        ]
        # 移除 read_only_fields 中的 created_by，因为该字段已不存在
        read_only_fields = ['size', 'downloads', 'created_at', 'file_name']

    def validate_file(self, value):
        if not value:
            raise serializers.ValidationError("必须上传文件")
        # ... (其他验证保持不变)
        return value

    def get_file_url(self, obj):
        if obj.file and hasattr(obj.file, 'url'):
            return obj.file.url
        return None

    def get_file_name(self, obj):
        if obj.file:
            return os.path.basename(obj.file.name)
        return None