from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from .models import Question, Comment
from .serializers import QuestionSerializer, CommentSerializer
from rest_framework.response import Response

class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # 从请求中获取用户ID（假设已通过认证中间件添加）
        serializer.save(author_id=self.request.user_id)

class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # 检查用户是否有权限删除（作者或管理员）
        if instance.author_id != request.user_id and not request.is_admin:
            return Response({"error": "您没有权限删除此问题"}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)

class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        question_id = self.kwargs['question_id']
        question = generics.get_object_or_404(Question, pk=question_id)
        serializer.save(author_id=self.request.user_id, question=question)

class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # 检查用户是否有权限删除（作者或管理员）
        if instance.author_id != request.user_id and not request.is_admin:
            return Response({"error": "您没有权限删除此评论"}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)

class ToggleStickyView(generics.UpdateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        # 检查用户是否有权限置顶（管理员）
        if not request.is_admin:
            return Response({"error": "您没有权限执行此操作"}, status=status.HTTP_403_FORBIDDEN)
            
        question = self.get_object()
        question.is_sticky = not question.is_sticky
        question.save()
        return Response({"is_sticky": question.is_sticky})

class ToggleLikeView(generics.UpdateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        question = self.get_object()
        user_id = request.user_id
        
        if user_id in question.likes:
            question.likes.remove(user_id)
            liked = False
        else:
            question.likes.append(user_id)
            liked = True
            
        question.save()
        return Response({"liked": liked, "likes_count": len(question.likes)})