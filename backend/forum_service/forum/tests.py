# 微服务版本 tests.py 修改（兼容 author = IntegerField）
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Question, Comment

User = get_user_model()

class QuestionModelTest(TestCase):
    def setUp(self):
        # 创建模拟用户
        self.user = User.objects.create_user(username='user1', password='pwd')
        # 使用 user.id 作为 author 字段
        self.q = Question.objects.create(title='T1', content='C1', author=self.user.id)

    def test_str_positive(self):
        self.assertEqual(str(self.q), 'T1')

    def test_str_negative(self):
        self.q.title = ''
        self.assertEqual(str(self.q), '')

class CommentModelTest(TestCase):
    def setUp(self):
        # 创建模拟用户
        self.user = User.objects.create_user(username='user2', password='pwd')
        # 创建 Question
        self.q = Question.objects.create(title='T2', content='C2', author=self.user.id)
        # 创建 Comment
        self.c = Comment.objects.create(question=self.q, content='Nice', author=self.user.id)

    def test_str_positive(self):
        # 获取 username
        username = User.objects.get(id=self.c.author).username
        expected = f"Comment by {username} on {self.q.title}"
        self.assertEqual(str(self.c), expected)

    def test_str_negative_title_empty(self):
        self.q.title = ''
        username = User.objects.get(id=self.c.author).username
        expected = f"Comment by {username} on "
        self.assertEqual(str(self.c), expected)
