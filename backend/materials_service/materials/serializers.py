# backend/materials_service/materials/serializers.py

from rest_framework import serializers
from .models import LearningMaterial
import os

class LearningMaterialSerializer(serializers.ModelSerializer):
    # 这些字段用于API响应（读操作），它们是动态生成的
    file_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    uploader_username = serializers.CharField(read_only=True)
    question_set = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = LearningMaterial
        # 'fields' 列表现在只包含用于读取的字段
        fields = [
            'id', 
            'title', 
            'description', 
            'type', 
            'file_url', 
            'file_name',
            'size', 
            'downloads', 
            'created_at', 
            'uploader_username',
            'question_set',
        ]
        read_only_fields = ['size', 'downloads', 'created_at', 'uploader_username']

    def get_file_name(self, obj):
        if obj.file:
            return os.path.basename(obj.file.name)
        return None

    def get_file_url(self, obj):
        if obj.file:
            # 返回一个相对URL
            return obj.file.url
        return None

    def create(self, validated_data):
        # 从上下文中获取 request 对象
        request = self.context['request']
        user = request.user
        
        # 直接从 request.FILES 中获取上传的文件
        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            raise serializers.ValidationError({'file': 'No file was submitted.'})

        # 关键修复：安全地从 validated_data 中移除 uploader_username 和 size，以防止冲突
        validated_data.pop('uploader_username', None)
        validated_data.pop('size', None)

        # 'file' 不在 validated_data 中，我们手动处理它
        material = LearningMaterial.objects.create(
            uploader_username=user.username, 
            file=uploaded_file,
            size=uploaded_file.size,
            **validated_data
        )
        return material
