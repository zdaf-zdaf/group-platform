# server/experiment/models.py
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from typing import Any


User = settings.AUTH_USER_MODEL

# 原 QuestionSet
class Experiment(models.Model):
    """实验模型"""
    title = models.CharField(max_length=200, verbose_name="实验标题")
    description = models.TextField(null=True, blank=True, verbose_name="实验描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    deadline = models.DateTimeField(null=True, blank=True, verbose_name="截止时间")  # 可选，参考原QuestionSet
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_experiments', verbose_name="教师")
    students = models.ManyToManyField(User, related_name='assigned_experiments', verbose_name="学生")
    allow_late_submission = models.BooleanField(default=False)
    late_submission_penalty = models.IntegerField(default=0) # 存储百分比值


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
        return f"填空题 #{self.id}"  # FillProblem

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
        return f"编程题 #{self.id}"  # CodingProblem

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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="提交用户"
    )
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
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
            models.Index(fields=['coding_problem', 'user']),
        ]

# 通用提交模型，关联 Experiment 和用户
class Submission(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='submissions', verbose_name="实验")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions', verbose_name="学生")
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_passed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} 提交的 {self.experiment.title}"

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['submitted_at']),
            models.Index(fields=['experiment', 'user']),
        ]

# 通用答案模型，使用 GenericForeignKey 关联不同题型
class Answer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers', verbose_name="提交记录")

    # 通用关联题目
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    question = GenericForeignKey('content_type', 'object_id')

    # 答案内容字段，分别支持选择/填空和编程题
    answer_text = models.TextField(blank=True, null=True, verbose_name="答案文本")  # 选择题/填空题
    code = models.TextField(blank=True, null=True, verbose_name="代码")  # 编程题
    file = models.FileField(upload_to='answer_files/', blank=True, null=True, verbose_name="上传文件")

    is_passed = models.BooleanField(default=False, verbose_name="是否通过")

    def __str__(self):
        return f"{self.submission.user} 的答案: {str(self.question)[:50]}"


class TestResult(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='test_results', verbose_name="答案")
    # 假设 test_case 依然用 JSON 格式存储，或者关联题目测试用例（此处简化为JSON）
    test_case_input = models.TextField(verbose_name="测试用例输入")
    expected_output = models.TextField(verbose_name="预期输出")
    actual_output = models.TextField(verbose_name="实际输出")
    is_passed = models.BooleanField(default=False, verbose_name="是否通过")

    def __str__(self):
        return f"测试结果: {'通过' if self.is_passed else '失败'}"