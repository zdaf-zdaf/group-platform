from django.contrib.auth.models import User
from django.test import TestCase
from notice.models import Notice
from rest_framework.test import APIClient
import jwt
from server import settings

class NoticeModelTest(TestCase):
    def setUp(self):
        # 创建普通用户，不带 role
        self.author = User.objects.create_user(
            username='author',
            password='pwd',
            email='a@a.com'
        )

        # 模拟 JWT，用于测试时传递用户ID和角色信息
        self.jwt_token = jwt.encode(
            {"user_id": self.author.id, "role": "teacher"},
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        # 初始化 DRF 测试客户端
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')

        # 创建测试 Notice 实例
        self.notice_positive = Notice.objects.create(
            title='Test Positive',
            content='This is a positive test notice.',
            author_id=self.author.id
        )
        self.notice_negative = Notice.objects.create(
            title='Test Negative',
            content='This is a negative test notice.',
            author_id=self.author.id
        )

    def test_is_read_by_positive(self):
        # 测试用户未读前 is_read_by 为 False
        self.assertFalse(self.notice_positive.is_read_by(self.author.id))
        # 模拟用户读取
        self.notice_positive.readers.add(self.author.id)
        self.assertTrue(self.notice_positive.is_read_by(self.author.id))

    def test_is_read_by_negative(self):
        # 另一个用户未读，返回 False
        other_user_id = self.author.id + 1
        self.assertFalse(self.notice_negative.is_read_by(other_user_id))

    def test_str_positive(self):
        self.assertEqual(str(self.notice_positive), f'Notice: {self.notice_positive.title}')

    def test_str_negative(self):
        self.assertEqual(str(self.notice_negative), f'Notice: {self.notice_negative.title}')
