# forum/tests.py 最终版
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Question, Comment

User = get_user_model()


class QuestionModelTest(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(username='user1', password='pwd', email='u1@example.com')
        # 创建测试问题
        self.q = Question.objects.create(title='T1', content='C1', author=self.user)

    def test_str_positive(self):
        """测试 Question 的 __str__ 返回正确标题"""
        self.assertEqual(str(self.q), 'T1')

    def test_str_negative(self):
        """测试标题为空时 __str__ 返回空字符串"""
        self.q.title = ''
        self.assertEqual(str(self.q), '')


class CommentModelTest(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(username='user2', password='pwd', email='u2@example.com')
        # 创建测试问题
        self.q = Question.objects.create(title='T2', content='C2', author=self.user)
        # 创建测试评论
        self.c = Comment.objects.create(question=self.q, content='Nice', author=self.user)

    def test_str_positive(self):
        """测试 Comment 的 __str__ 返回格式 'Comment by <username> on <question.title>'"""
        expected = f"Comment by {self.user.username} on {self.q.title}"
        self.assertEqual(str(self.c), expected)

    def test_str_negative_title_empty(self):
        """当 Question 标题为空时，Comment __str__ 返回格式 'Comment by <username> on '"""
        self.q.title = ''
        expected = f"Comment by {self.user.username} on "
        self.assertEqual(str(self.c), expected)
