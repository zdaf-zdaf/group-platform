import os
import logging
from urllib.parse import unquote
from urllib.parse import quote
from django.conf import settings
from rest_framework import viewsets, permissions, status,serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse, Http404
from .models import LearningMaterial
from .serializers import LearningMaterialSerializer
from .permissions import IsTeacherOrReadOnly  # 使用自定义权限


logger = logging.getLogger(__name__)

class LearningMaterialViewSet(viewsets.ModelViewSet):
    queryset = LearningMaterial.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = LearningMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return LearningMaterial.objects.filter(created_by=user)
        return LearningMaterial.objects.all()

    def create(self, request, *args, **kwargs):
        # 修复中文文件名处理
        if 'file' in request.FILES:
            file = request.FILES['file']
            # 正确解码中文文件名
            file.name = unquote(file.name)
            request.FILES['file'] = file

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        if not file:
            logger.error("未接收到文件")
            raise serializers.ValidationError({"file": "必须上传文件"})

        # 确保文件大小被正确保存
        serializer.save(
            created_by=self.request.user,
            size=file.size
        )
        logger.info(f"文件保存成功 - 文件名: {file.name}, 大小: {file.size}字节")

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if request.user != instance.created_by:
                logger.warning(f"用户 {request.user.id} 尝试删除无权限的资料 {instance.id}")
                return Response(
                    {"error": "无权删除此资料"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 删除物理文件
            file_path = instance.file.path
            if os.path.exists(file_path):
                os.remove(file_path)

            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"删除资料失败: {str(e)}")
            return Response(
                {"error": f"删除资料失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if request.user != instance.created_by:
                logger.warning(f"用户 {request.user.id} 尝试修改无权限的资料 {instance.id}")
                return Response(
                    {"error": "无权修改此资料"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 处理文件更新
            file = request.FILES.get('file')

            if not file:
                # 只更新其他字段
                serializer = self.get_serializer(
                    instance,
                    data=request.data,
                    partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)

            # 处理文件更新
            # 删除旧文件
            old_file = instance.file.path
            if os.path.exists(old_file):
                os.remove(old_file)
            # 更新文件大小
            instance.size = file.size

            return super().update(request, *args, **kwargs)

        except Exception as e:
            logger.error(f"更新资料失败: {str(e)}")
            return Response(
                {"error": f"更新资料失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        try:
            material = self.get_object()

            if not material.file:
                logger.error(f"资料 {pk} 无文件关联")
                return Response(
                    {"error": "文件不存在"},
                    status=status.HTTP_404_NOT_FOUND
                )

            if not material.file_exists:
                logger.error(f"资料 {pk} 文件不存在于存储系统")
                return Response(
                    {"error": "文件存储系统中不存在"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # 更新下载次数
            material.downloads += 1
            material.save()

            # 创建文件响应
            file_path = material.file.path

            # 修复：使用安全方式打开文件
            response = FileResponse(
                open(file_path, 'rb'),  # 使用二进制模式打开
                content_type='application/octet-stream'  # 通用二进制类型
            )

            # 修复文件名编码问题
            filename = os.path.basename(file_path)
            quoted_filename = quote(filename)  # 处理中文文件名

            # 设置下载头
            response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{quoted_filename}'

            # 设置文件大小
            response['Content-Length'] = os.path.getsize(file_path)

            logger.info(f"文件下载成功 - 资料ID: {pk}, 文件名: {filename}")
            return response

        except FileNotFoundError:
            logger.error(f"文件未找到 - 资料ID: {pk}")
            return Response(
                {"error": "文件未找到"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"文件下载失败 - 资料ID: {pk}, 错误: {str(e)}")
            return Response(
                {"error": f"文件下载失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )