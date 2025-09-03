from django.db import models
from django.utils import timezone

class Question(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.IntegerField()  # 改为使用用户ID而不是外键
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.JSONField(default=list)  # 存储喜欢该问题的用户ID列表
    is_sticky = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-is_sticky', '-created_at']
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    question = models.ForeignKey(Question, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    author = models.IntegerField()  # 改为使用用户ID而不是外键
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by user {self.author_id} on {self.question.title}"