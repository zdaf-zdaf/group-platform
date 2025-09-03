from django.test import TestCase
from .models import Question, Comment

class QuestionModelTest(TestCase):
    def setUp(self):
        # 使用整数 ID 模拟用户
        self.user_id = 1
        self.q = Question.objects.create(title='T1', content='C1', author=self.user_id)

    def test_str_positive(self):
        self.assertEqual(str(self.q), 'T1')

    def test_str_negative(self):
        self.q.title = ''
        self.assertEqual(str(self.q), '')

class CommentModelTest(TestCase):
    def setUp(self):
        self.user_id = 2
        self.q = Question.objects.create(title='T2', content='C2', author=self.user_id)
        self.c = Comment.objects.create(question=self.q, content='Nice', author=self.user_id)

    def test_str_positive(self):
        expected = f"Comment by user {self.user_id} on {self.q.title}"
        self.assertEqual(str(self.c), expected)

    def test_str_negative_title_empty(self):
        self.q.title = ''
        expected = f"Comment by user {self.user_id} on "
        self.assertEqual(str(self.c), expected)
