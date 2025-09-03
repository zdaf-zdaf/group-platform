from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User  # 引入 Django 内置 User 模型

class Question(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 改为 ForeignKey
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.JSONField(default=list)  # 存储喜欢该问题的用户ID列表
    is_sticky = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-is_sticky', '-created_at']
    
    def __str__(self):
        # 显示作者用户名而不是 ID
        return self.title if self.title else ''


class Comment(models.Model):
    question = models.ForeignKey(Question, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 改为 ForeignKey
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        # 显示作者用户名，标题为空也不会报错
        question_title = self.question.title if self.question.title else ''
        return f"Comment by {self.author.username} on {question_title}"
