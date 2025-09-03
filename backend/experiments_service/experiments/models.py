from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Experiment(models.Model):
    """实验模型 - 微服务版本"""
    title = models.CharField(max_length=200, verbose_name="实验标题")
    description = models.TextField(null=True, blank=True, verbose_name="实验描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    deadline = models.DateTimeField(null=True, blank=True, verbose_name="截止时间")
    
    # 遵循建议1: 只存author_id，不依赖User模型
    teacher_id = models.IntegerField(verbose_name="教师ID")
    
    # 使用JSONField存储学生ID列表，而不是ManyToMany关系
    student_ids = models.JSONField(default=list, verbose_name="学生ID列表")
    
    allow_late_submission = models.BooleanField(default=False)
    late_submission_penalty = models.IntegerField(default=0)  # 存储百分比值

    def __str__(self):
        return self.title

    class Meta:
        db_table = "experiment_experiment"


class ChoiceProblem(models.Model):
    """选择题模型"""
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='choice_problems',
        verbose_name="所属实验"
    )
    description = models.TextField(blank=True, verbose_name="问题描述")
    options = models.JSONField(verbose_name="选项列表")
    correct_answer = models.CharField(max_length=1, verbose_name="正确答案")
    score = models.PositiveIntegerField(default=10, verbose_name="题目分值")
    order = models.PositiveIntegerField(default=0, verbose_name="题目顺序")

    def __str__(self):
        return f"选择题 #{self.id}"

    class Meta:
        db_table = "experiment_choice_problem"
        ordering = ['order']


class FillProblem(models.Model):
    """填空题模型"""
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='fill_problems',
        verbose_name="所属实验"
    )
    description = models.TextField(blank=True, verbose_name="问题描述")
    correct_answer = models.CharField(max_length=200, verbose_name="正确答案")
    score = models.PositiveIntegerField(default=10, verbose_name="题目分值")
    order = models.PositiveIntegerField(default=0, verbose_name="题目顺序")

    def __str__(self):
        return f"填空题 #{self.id}"

    class Meta:
        db_table = "experiment_fill_problem"
        ordering = ['order']


class CodingProblem(models.Model):
    """编程题模型"""
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='coding_problems',
        verbose_name="所属实验"
    )
    description = models.TextField(verbose_name="题目描述")
    test_cases = models.JSONField(verbose_name="测试用例列表")
    timeout = models.IntegerField(default=10, verbose_name="超时时间(秒)")
    mem_limit = models.IntegerField(default=512, verbose_name="内存限制(MB)")
    last_submission_status = models.JSONField(null=True, blank=True)
    score = models.PositiveIntegerField(default=10, verbose_name="题目分值")
    order = models.PositiveIntegerField(default=0, verbose_name="题目顺序")

    def __str__(self):
        return f"编程题 #{self.id}"

    class Meta:
        db_table = "experiment_coding_problem"
        ordering = ['order']


class CodingSubmission(models.Model):
    """提交记录模型"""
    coding_problem = models.ForeignKey(
        CodingProblem,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name="对应编程题"
    )
    
    # 遵循建议1: 只存user_id，不依赖User模型
    user_id = models.IntegerField(verbose_name="提交用户ID")
    
    code = models.TextField(verbose_name="提交代码")
    passed_count = models.IntegerField(verbose_name="通过用例数")
    total_count = models.IntegerField(verbose_name="总用例数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="提交时间")
    details = models.JSONField(blank=True, null=True, verbose_name="详细测试结果")

    def __str__(self):
        return f"提交ID: {self.id}"

    class Meta:
        db_table = "experiment_coding_submission"
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['coding_problem', 'user_id']),
        ]


class Submission(models.Model):
    """提交模型"""
    experiment = models.ForeignKey(
        Experiment, 
        on_delete=models.CASCADE, 
        related_name='submissions', 
        verbose_name="实验"
    )
    
    # 遵循建议1: 只存user_id，不依赖User模型
    user_id = models.IntegerField(verbose_name="学生ID")
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_passed = models.BooleanField(default=False)

    def __str__(self):
        return f"用户 {self.user_id} 提交的 {self.experiment.title}"

    class Meta:
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['submitted_at']),
            models.Index(fields=['experiment', 'user_id']),
        ]


class Answer(models.Model):
    """答案模型"""
    submission = models.ForeignKey(
        Submission, 
        on_delete=models.CASCADE, 
        related_name='answers', 
        verbose_name="提交记录"
    )

    # 通用关联题目
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    question = GenericForeignKey('content_type', 'object_id')

    # 答案内容字段
    answer_text = models.TextField(blank=True, null=True, verbose_name="答案文本")
    code = models.TextField(blank=True, null=True, verbose_name="代码")
    file = models.FileField(upload_to='answer_files/', blank=True, null=True, verbose_name="上传文件")

    is_passed = models.BooleanField(default=False, verbose_name="是否通过")

    def __str__(self):
        return f"用户 {self.submission.user_id} 的答案"


class TestResult(models.Model):
    """测试结果模型"""
    answer = models.ForeignKey(
        Answer, 
        on_delete=models.CASCADE, 
        related_name='test_results', 
        verbose_name="答案"
    )
    test_case_input = models.TextField(verbose_name="测试用例输入")
    expected_output = models.TextField(verbose_name="预期输出")
    actual_output = models.TextField(verbose_name="实际输出")
    is_passed = models.BooleanField(default=False, verbose_name="是否通过")

    def __str__(self):
        return f"测试结果: {'通过' if self.is_passed else '失败'}"