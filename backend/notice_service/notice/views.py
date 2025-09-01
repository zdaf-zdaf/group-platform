from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from .models import Notice
from .serializers import NoticeSerializer
import logging
import time

logger = logging.getLogger('notice')

class ModerateThrottle(UserRateThrottle):
    """自定义限流策略"""
    scope = 'moderate'
    rate = '100/hour'  # 每小时100次请求

class HighPriorityThrottle(UserRateThrottle):
    """高优先级操作限流"""
    scope = 'high'
    rate = '10/minute'  # 每分钟10次请求

class NoticeViewSet(viewsets.ModelViewSet):
    serializer_class = NoticeSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ModerateThrottle]  # 默认限流策略

    def get_throttles(self):
        """根据操作类型应用不同限流策略"""
        if self.action in ['mark_as_read', 'mark_all_read']:
            # 高频操作应用更严格的限流
            return [HighPriorityThrottle()]
        return super().get_throttles()

    def get_queryset(self):
        user = self.request.user
        queryset = Notice.objects.all()
        
        # 按用户角色过滤
        if hasattr(user, 'role') and user.role == 'student':
            # 学生只能看到非置顶公告或已读公告
            # 获取当前用户ID
            user_id = user.id
            # 查询条件：非置顶公告 OR 已读公告
            queryset = queryset.filter(
                Q(is_top=False) | Q(reader_ids__contains=[user_id])
            )
        
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
                serializer = self.get_serializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True, context={'request': request})
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
            start_time = time.time()  # 记录开始时间

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

            # 记录处理时间
            duration = time.time() - start_time
            logger.info(f"成功为 {marked_count} 条公告添加已读标记，耗时 {duration:.2f} 秒")

            return Response({
                "status": "success",
                "marked_count": marked_count,
                "time_taken": f"{duration:.2f}秒"
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
            start_time = time.time()  # 记录开始时间

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

            # 记录处理时间
            duration = time.time() - start_time
            
            # 返回成功响应
            return Response({
                "status": "success",
                "read_count": len(notice.reader_ids),
                "time_taken": f"{duration:.4f}秒"
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
                f"用户 {request.user.username} 尝试更新公告（角色：{getattr(request.user, 'role', '未设置')}）")
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
                "detail": "无权限操作"
            }, status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)