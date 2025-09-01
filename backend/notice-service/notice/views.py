from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Notice
from .serializers import NoticeSerializer
import logging

logger = logging.getLogger('notice')

class NoticeViewSet(viewsets.ModelViewSet):
    serializer_class = NoticeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Notice.objects.all()
        
        # 按用户角色过滤
        if hasattr(user, 'role') and user.role == 'student':
            # 学生只能看到非置顶公告或已读公告
            pass  # 根据业务需求实现
        
        return queryset.order_by('-is_top', '-date')

    def list(self, request, *args, **kwargs):
        """获取公告列表并添加用户是否已读标记"""
        try:
            queryset = self.filter_queryset(self.get_queryset())

            # 按置顶和时间排序
            queryset = queryset.order_by('-is_top', '-date')

            # 分页
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.exception("获取公告列表时发生异常")
            return Response({
                'detail': '获取公告列表失败，请稍后再试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """优化未读数量计算：减少数据库查询"""
        try:
            user = request.user

            # 只有学生能看到未读数量
            if not hasattr(user, 'role') or user.role != 'student':
                logger.info(f"非学生用户 {user.username} 尝试获取未读数量")
                return Response({"count": 0})

            # 计算用户未读公告数量
            unread_count = Notice.objects.exclude(reader_ids__contains=[user.id]).count()
            logger.info(f"学生用户 {user.username} 有 {unread_count} 条未读公告")
            return Response({"count": unread_count})
        except Exception as e:
            logger.exception(f"获取未读数量失败: {str(e)}")
            return Response({"count": 0}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """标记所有公告为已读 - 优化性能"""
        try:
            user = request.user

            # 只有学生能标记公告
            if not hasattr(user, 'role') or user.role != 'student':
                logger.warning(
                    f"非学生用户 {user.username} 尝试标记所有公告（角色：{getattr(user, 'role', '未知')}）")
                return Response({
                    "detail": "无权限操作"
                }, status=status.HTTP_403_FORBIDDEN)

            logger.info(f"学生用户 {user.username} 开始标记所有公告为已读")

            # 获取所有未读公告
            unread_notices = Notice.objects.exclude(reader_ids__contains=[user.id])
            marked_count = 0

            # 批量添加已读标记
            for notice in unread_notices:
                if user.id not in notice.reader_ids:
                    notice.reader_ids.append(user.id)
                    notice.save()
                    marked_count += 1

            logger.info(f"成功为 {marked_count} 条公告添加已读标记")

            return Response({
                "status": "success",
                "marked_count": marked_count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"标记所有公告为已读失败: {str(e)}")
            return Response({
                "detail": "服务器内部错误"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """标记单个公告为已读"""
        try:
            notice = self.get_object()
            user = request.user

            # 验证用户角色
            if not hasattr(user, 'role') or user.role != 'student':
                logger.warning(
                    f"非学生用户 {user.username} 尝试标记公告（角色：{getattr(user, 'role', '未知')}）")
                return Response(
                    {"detail": "只允许学生标记公告为已读"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 检查是否已读
            is_already_read = user.id in notice.reader_ids

            if is_already_read:
                logger.info(f"公告 {pk} 已由用户 {user.username} 阅读过")
            else:
                # 添加阅读标记
                notice.reader_ids.append(user.id)
                notice.save()
                logger.info(f"用户 {user.username} 标记公告 {pk} 为已读")

            # 返回成功响应
            return Response({
                "status": "success",
                "read_count": len(notice.reader_ids)
            })
        except Exception as e:
            logger.exception(f"标记公告 {pk} 为已读失败: {str(e)}")
            # 提供更详细的错误信息
            return Response({
                "detail": "标记失败，请稍后再试",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """创建公告（只允许教师操作）"""
        # 权限验证 - 使用role字段
        if not hasattr(request.user, 'role') or request.user.role != 'teacher':
            logger.warning(
                f"用户 {request.user.username} 尝试创建公告，但无权限（角色：{getattr(request.user, 'role', '未设置')}）")
            return Response({
                "detail": "无权限操作"
            }, status=status.HTTP_403_FORBIDDEN)

        return super().create(request)

    def update(self, request, *args, **kwargs):
        """更新公告（只允许教师操作）"""
        # 权限验证 - 使用role字段
        if not hasattr(request.user, 'role') or request.user.role != 'teacher':
            logger.warning(
                f"用户 {request.user.username} 尝试更新公告，极权（角色：{getattr(request.user, 'role', '未设置')}）")
            return Response({
                "detail": "无权限操作"
            }, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """删除公告（只允许教师操作）"""
        # 权限验证 - 使用role字段
        if not hasattr(request.user, 'role') or request.user.role != 'teacher':
            logger.warning(
                f"用户 {request.user.username} 尝试删除公告，但无权限（角色：{getattr(request.user, 'role', '未设置')}）")
            return Response({
                "detail": "极权操作"
            }, status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)