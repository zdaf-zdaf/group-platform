from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', '学生'),
        ('teacher', '教师'),
    )
    role = models.CharField(_('角色'), choices=ROLE_CHOICES, max_length=20, default='student')
    username = models.CharField(max_length=50, unique=True, blank=False)
    password = models.CharField(max_length=1024, blank=False)
    student_id = models.CharField(_('学号'), max_length=20, unique=True, null=True, blank=True)
    faculty = models.CharField(_('学院'), max_length=50, null=True, blank=True)
    email = models.EmailField(_('邮箱'), unique=True, blank=False)

    REQUIRED_FIELDS = ['email', 'role']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        db_table = 'user'
        verbose_name = _('用户')
        verbose_name_plural = _('用户')