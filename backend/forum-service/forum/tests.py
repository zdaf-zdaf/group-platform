from django.test import TestCase
from .models import Question, Comment
from django.contrib.auth import get_user_model

# 使用Django内置的User模型作为替代
User = get_user_model()

class QuestionModelTest(TestCase):
    def setUp(self):
        # 创建本地用户（不依赖外部服务）
        self.user = User.objects.create_user(
            username='alice', 
            password='pwd', 
            email='a@b.com'
        )
        self.q = Question.objects.create(
            title='T1', 
            content='C1', 
            author=self.user
        )

    def test_str_positive(self):
        self.assertEqual(str(self.q), 'T1')

    def test_str_negative(self):
        self.q.title = ''
        self.assertEqual(str(self.q), '')


class CommentModelTest(TestCase):
    def setUp(self):
        # 创建本地用户（不依赖外部服务）
        self.user = User.objects.create_user(
            username='bob', 
            password='pwd', 
            email='b@b.com'
        )
        self.q = Question.objects.create(
            title='T2', 
            content='C2', 
            author=self.user
        )
        self.c = Comment.objects.create(
            question=self.q, 
            content='Nice', 
            author=self.user
        )

    def test_str_positive(self):
        expected = f"Comment by {self.user.username} on {self.q.title}"
        self.assertEqual(str(self.c), expected)

    def test_str_negative(self):
        # 用户名为空时返回中的用户名段为空
        self.user.username = ''
        self.user.save()  # 确保更新保存到数据库
        self.c.refresh_from_db()  # 刷新对象状态
        
        expected = f"Comment by  on {self.q.title}"
        self.assertEqual(str(self.c), expected)

    def test_str_negative_title_empty(self):
        self.q.title = ''
        self.q.save()  # 确保更新保存到数据库
        self.c.refresh_from_db()  # 刷新对象状态
        
        expected = f"Comment by {self.user.username} on "
        self.assertEqual(str(self.c), expected)