# backend/materials_service/materials/views.py

import os
import logging
from urllib.parse import quote
from django.http import FileResponse
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import LearningMaterial
from .serializers import LearningMaterialSerializer
from .permissions import IsTeacher  # 导入我们自定义的 IsTeacher 权限

logger = logging.getLogger(__name__)

class LearningMaterialViewSet(viewsets.ModelViewSet):
    queryset = LearningMaterial.objects.all()
    serializer_class = LearningMaterialSerializer
    parser_classes = (MultiPartParser, FormParser)

    # 1. 使用 DRF 标准的权限控制方法
    def get_permissions(self):
        """
        根据不同的操作 (action) 返回不同的权限。
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # 对于写操作 (创建, 更新, 删除)，要求用户必须是教师。
            # IsTeacher 会检查 Token 中的 role 是否为 'teacher'。
            permission_classes = [IsTeacher]
        else:
            # 对于读操作 (list, retrieve, download)，只要求用户已登录。
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    # 2. 改造 perform_create 以适应微服务
    def perform_create(self, serializer):
        """
        在创建资料时，自动记录上传者的用户名。
        """
        # 从 JWT Token 中获取用户名，而不是 user 对象
        uploader_username = self.request.user.username
        serializer.save(
            uploader_username=uploader_username,
            size=self.request.FILES.get('file').size
        )
        logger.info(f"文件保存成功 - 上传者: {uploader_username}")

    # 3. 改造 perform_update
    def perform_update(self, serializer):
        # 在更新时，也保存文件大小
        data = {'size': self.request.FILES.get('file').size} if self.request.FILES.get('file') else {}
        serializer.save(**data)

    # 4. 改造 destroy
    def perform_destroy(self, instance):
        # 删除关联的物理文件
        try:
            file_path = instance.file.path
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"物理文件已删除: {file_path}")
        except Exception as e:
            logger.error(f"删除物理文件失败: {str(e)}")
        instance.delete()

    # 5. 统一权限检查逻辑
    def check_object_permissions(self, request, obj):
        """
        在获取单个对象时，检查对象级别的权限。
        确保只有创建者本人才能修改或删除。
        """
        super().check_object_permissions(request, obj)
        # 对于写操作，额外检查用户名是否匹配
        if self.action in ['update', 'partial_update', 'destroy']:
            if obj.uploader_username != request.user.username:
                self.permission_denied(
                    request, message='你无权修改或删除他人创建的资料。'
                )

    # 6. 下载文件的 action (保持不变，但现在受 get_permissions 控制)
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        try:
            material = self.get_object()
            file_path = material.file.path

            if not os.path.exists(file_path):
                return Response({"error": "文件不存在"}, status=status.HTTP_404_NOT_FOUND)

            material.downloads += 1
            material.save()

            response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
            filename = os.path.basename(file_path)
            quoted_filename = quote(filename)
            response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{quoted_filename}'
            response['Content-Length'] = os.path.getsize(file_path)
            
            logger.info(f"文件下载成功 - 资料ID: {pk}, 文件名: {filename}")
            return response
        except Exception as e:
            logger.error(f"文件下载失败 - 资料ID: {pk}, 错误: {str(e)}")
            return Response({"error": f"文件下载失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
