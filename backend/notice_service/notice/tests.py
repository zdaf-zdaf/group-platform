from django.contrib.auth.models import User
from django.test import TestCase
from notice.models import Notice
from rest_framework.test import APIClient
import jwt
from server import settings

class NoticeModelTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            password='pwd',
            email='a@a.com'
        )

        self.jwt_token = jwt.encode(
            {"user_id": self.author.id, "role": "teacher"},
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')

        self.notice_positive = Notice.objects.create(
            title='Test Positive',
            content='This is a positive test notice.',
            author_id=self.author.id,
            readers=[]  # 假设 readers 是 list 类型
        )
        self.notice_negative = Notice.objects.create(
            title='Test Negative',
            content='This is a negative test notice.',
            author_id=self.author.id,
            readers=[]
        )

    def test_is_read_by_positive(self):
        # 用户未读前
        self.assertFalse(self.notice_positive.is_read_by(self.author.id))
        # 用户读取后
        self.notice_positive.readers.append(self.author.id)
        self.notice_positive.save()
        self.assertTrue(self.notice_positive.is_read_by(self.author.id))

    def test_is_read_by_negative(self):
        other_user_id = self.author.id + 1
        self.assertFalse(self.notice_negative.is_read_by(other_user_id))

    def test_str_positive(self):
        self.assertEqual(str(self.notice_positive), self.notice_positive.title)

    def test_str_negative(self):
        self.assertEqual(str(self.notice_negative), self.notice_negative.title)
