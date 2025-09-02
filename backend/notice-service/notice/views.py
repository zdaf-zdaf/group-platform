import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Notice
from .serializers import NoticeSerializer
from .permissions import IsTeacherOrReadOnly
from django.db.models import Q

logger = logging.getLogger('notice')

class NoticeViewSet(viewsets.ModelViewSet):
    serializer_class = NoticeSerializer
    permission_classes = [IsTeacherOrReadOnly] 

    def get_queryset(self):
        queryset = Notice.objects.all()
        
        # 按置顶和时间排序
        return queryset.order_by('-is_top', '-date')

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        try:
            user = request.user

            # 检查用户角色 - 改为小写 'student'
            if not hasattr(user, 'role') or user.role != 'student':
                return Response({"count": 0}, status=status.HTTP_200_OK)
                
            # 计算用户未读公告数量
            unread_count = Notice.objects.exclude(readers__contains=[user.id]).count()
            return Response({"count": unread_count})
        except Exception as e:
            logger.exception(f"获取未读数量失败: {str(e)}")
            return Response({"count": 0}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        try:
            user = request.user

             # 验证用户角色 - 改为小写 'student'
            if not hasattr(user, 'role') or user.role != 'student':
                return Response({"detail": "无权限操作"}, status=status.HTTP_403_FORBIDDEN)
                
            # 获取所有未读公告
            unread_notices = Notice.objects.exclude(readers__contains=[user.id])
            marked_count = 0
            
            # 批量更新
            for notice in unread_notices:
                if user.id not in notice.readers:
                    notice.readers.append(user.id)
                    notice.save()
                    marked_count += 1

            return Response({
                "status": "success",
                "marked_count": marked_count
            })
        except Exception as e:
            logger.exception(f"标记所有公告为已读失败: {str(e)}")
            return Response({"detail": "服务器内部错误"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        try:
            notice = self.get_object()
            user = request.user
            
            logger.info(f"标记公告请求: 用户ID={user.id}, 角色={user.role}, 公告ID={pk}")
            
            # 验证用户角色 - 确保使用小写 'student'
            if not hasattr(user, 'role'):
                logger.warning("用户对象缺少role属性")
                return Response(
                    {"detail": "用户信息不完整"},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # 修改这里：检查用户角色是否为 'student'
            if user.role != 'student':
                logger.warning(f"用户角色不是student: {user.role}")
                return Response(
                    {"detail": "只允许学生标记公告为已读"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 检查是否已读
            if user.id not in notice.readers:
                logger.info(f"用户 {user.id} 首次阅读公告 {pk}")
                # 添加阅读标记
                notice.readers.append(user.id)
                notice.save()
                logger.info(f"用户 {user.id} 标记公告 {pk} 为已读")
            else:
                logger.info(f"用户 {user.id} 已阅读过公告 {pk}")

            # 返回成功响应
            return Response({
                "status": "success",
                "read_count": len(notice.readers)
            })
        except Exception as e:
            logger.exception(f"标记公告 {pk} 为已读失败: {str(e)}")
            return Response({
                "detail": "标记失败，请稍后再试",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def create(self, request, *args, **kwargs):
        # 手动设置作者ID
        request.data['author_id'] = request.user.id
        return super().create(request, *args, **kwargs)