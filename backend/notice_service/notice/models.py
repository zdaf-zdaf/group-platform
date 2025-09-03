from django.db import models
from django.utils import timezone

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
    author_id = models.IntegerField('作者ID')  # 改为普通字段存储
    experiment_id = models.IntegerField('关联实验ID', null=True, blank=True)  # 改为普通字段存储
    readers = models.JSONField('已读用户ID列表', default=list)  # 存储用户ID列表

    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告管理'
        ordering = ['-is_top', '-date']

    def __str__(self):
        return self.title

    # 检查用户是否已读此公告
    def is_read_by(self, user_id):
        return user_id in self.readers