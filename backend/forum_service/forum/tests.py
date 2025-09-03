# 微服务版本 tests.py 修改
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Question, Comment

User = get_user_model()


class QuestionModelTest(TestCase):
    def setUp(self):
        # 创建真实用户对象
        self.user = User.objects.create_user(username='user1', password='pwd', email='u1@example.com')
        self.q = Question.objects.create(title='T1', content='C1', author=self.user)

    def test_str_positive(self):
        self.assertEqual(str(self.q), 'T1')

    def test_str_negative(self):
        self.q.title = ''
        self.assertEqual(str(self.q), '')


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user2', password='pwd', email='u2@example.com')
        self.q = Question.objects.create(title='T2', content='C2', author=self.user)
        self.c = Comment.objects.create(question=self.q, content='Nice', author=self.user)

    def test_str_positive(self):
        expected = f"Comment by {self.user.username} on {self.q.title}"
        self.assertEqual(str(self.c), expected)

    def test_str_negative_title_empty(self):
        self.q.title = ''
        expected = f"Comment by {self.user.username} on "
        self.assertEqual(str(self.c), expected)
