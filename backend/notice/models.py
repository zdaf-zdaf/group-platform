from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from experiments.models import Experiment

User = get_user_model()


class Notice(models.Model):
    NOTICE_TYPES = (
        (1, '安全公告'),
        (2, '课程通知'),
        (3, '设备维护'),
        (4, '实验发布'),
    )

    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    type = models.SmallIntegerField('类型', choices=NOTICE_TYPES, default=2)
    date = models.DateTimeField('发布时间', auto_now_add=True)
    is_top = models.BooleanField('是否置顶', default=False)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notices',
        verbose_name='作者'
    )
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notices',
        verbose_name='关联实验'
    )
    # 新增：记录阅读过该公告的用户
    readers = models.ManyToManyField(
        User,
        related_name='read_notices',
        blank=True,
        verbose_name='已读用户'
    )

    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告管理'
        ordering = ['-is_top', '-date']

    def __str__(self):
        return self.title

    # 新增：检查用户是否已读此公告
    def is_read_by(self, user):
        return self.readers.filter(id=user.id).exists()