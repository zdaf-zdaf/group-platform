from django.db import models
from django.utils import timezone
from user.models import User
# Create your models here.

class Question(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_questions', blank=True)
    is_sticky = models.BooleanField(default=False)
    class Meta:
        ordering = ['-is_sticky', '-created_at']
    def __str__(self):
        return self.title

class Comment(models.Model):
    question = models.ForeignKey(Question, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.question.title}"