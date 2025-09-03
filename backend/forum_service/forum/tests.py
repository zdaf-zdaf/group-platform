from django.test import TestCase
from django.contrib.auth.models import User
from .models import Question, Comment

class QuestionModelTest(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(username='user1', password='testpass')
        # 创建 Question 对象
        self.q = Question.objects.create(title='T1', content='C1', author=self.user)

    def test_str_positive(self):
        # 标题存在时，__str__ 返回标题
        self.assertEqual(str(self.q), 'T1')

    def test_str_negative(self):
        # 标题为空时，__str__ 返回空字符串
        self.q.title = ''
        self.assertEqual(str(self.q), '')


class CommentModelTest(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(username='user2', password='testpass')
        # 创建 Question 对象
        self.q = Question.objects.create(title='T2', content='C2', author=self.user)
        # 创建 Comment 对象
        self.c = Comment.objects.create(question=self.q, content='Nice', author=self.user)

    def test_str_positive(self):
        # __str__ 返回 'Comment by <username> on <question.title>'
        expected = f"Comment by {self.user.username} on {self.q.title}"
        self.assertEqual(str(self.c), expected)

    def test_str_negative_title_empty(self):
        # 当 Question 标题为空时，__str__ 返回 'Comment by <username> on '
        self.q.title = ''
        expected = f"Comment by {self.user.username} on "
        self.assertEqual(str(self.c), expected)
