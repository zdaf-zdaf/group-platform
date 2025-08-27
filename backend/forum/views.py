from django.shortcuts import render
from rest_framework import viewsets, generics, permissions
from .models import Question, Comment
from .serializers import QuestionSerializer, CommentSerializer
from rest_framework.response import Response
# Create your views here.
class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user and not request.user.is_superuser:
            return Response({"error": "您没有权限删除此问题"}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
    
class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        question_id = self.kwargs['question_id']
        question = generics.get_object_or_404(Question, pk=question_id)
        serializer.save(author=self.request.user, question=question)

class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user and not request.user.is_superuser:
            return Response({"error": "您没有权限删除此评论"}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
    
class ToggleStickyView(generics.UpdateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
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
        user = request.user
        if question.likes.filter(id=user.id).exists():
            question.likes.remove(user)
            liked = False
        else:
            question.likes.add(user)
            liked = True
        return Response({"liked": liked, "likes_count": question.likes.count()})