from django.db import models
from django.contrib.auth import get_user_model  # 导入 get_user_model
from experiments.models import Experiment

# 获取用户模型
User = get_user_model()

class LearningMaterial(models.Model):
    MATERIAL_TYPES = (
        ('pdf', 'PDF文档'),
        ('video', '视频教程'),
        ('doc', '文档资料'),
        ('image', '图表素材'),
        ('code', '代码示例'),
        ('slide', '幻灯片'),
    )

    @property
    def file_exists(self):
        return self.file and self.file.storage.exists(self.file.name)

    title = models.CharField(max_length=200, verbose_name="资料标题")
    description = models.TextField(verbose_name="资料描述")
    type = models.CharField(max_length=10, choices=MATERIAL_TYPES, verbose_name="资料类型")
    file = models.FileField(upload_to='materials/%Y/%m/%d/', verbose_name="资料文件")
    size = models.BigIntegerField(verbose_name="文件大小(字节)", default=0)
    downloads = models.PositiveIntegerField(default=0, verbose_name="下载次数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    created_by = models.ForeignKey(
        User,  # 使用定义好的User变量
        on_delete=models.CASCADE,
        verbose_name="上传者",
        related_name='uploaded_materials'
    )
    # 关联题组（可选）
    question_set = models.ForeignKey(
        Experiment, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materials',
        verbose_name="关联题组"
    )

    class Meta:
        verbose_name = "学习资料"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file and not self.size:  # 自动计算文件大小
            self.size = self.file.size
        super().save(*args, **kwargs)