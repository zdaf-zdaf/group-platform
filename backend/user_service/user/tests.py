from django.test import TestCase
from .models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tom', email='t@a.com', password='pwd', role='student')

    def test_str_positive(self):
        s = str(self.user)
        self.assertIn('tom', s)
        self.assertIn('学生', s)

    def test_str_negative(self):
        # 修改用户名为空时，字符串仍可生成（包含空用户名）
        self.user.username = ''
        s = str(self.user)
        self.assertIsInstance(s, str)
