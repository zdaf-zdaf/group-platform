from django.db import models

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
    
    # 使用ID替代外键
    author_id = models.IntegerField('作者ID')
    experiment_id = models.IntegerField('关联实验ID', null=True, blank=True)
    
    # 使用JSONField存储已读用户ID
    reader_ids = models.JSONField('已读用户ID列表', default=list)

    class Meta:
        ordering = ['-is_top', '-date']

    def __str__(self):
        return self.title

    def is_read_by(self, user_id):
        return user_id in self.reader_ids