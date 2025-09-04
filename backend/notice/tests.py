from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Notice

User = get_user_model()


class NoticeModelTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='pwd', email='a@a.com', role='teacher')
        self.reader = User.objects.create_user(username='reader', password='pwd', email='r@a.com', role='student')
        self.notice = Notice.objects.create(title='N1', content='C', author=self.author)

    def test_str_positive(self):
        self.assertEqual(str(self.notice), 'N1')

    def test_str_negative(self):
        self.notice.title = ''
        self.assertEqual(str(self.notice), '')

    def test_is_read_by_positive(self):
        self.notice.readers.add(self.reader)
        self.assertTrue(self.notice.is_read_by(self.reader))

    def test_is_read_by_negative(self):
        other = User.objects.create_user(username='other', password='pwd', email='o@a.com', role='student')
        self.assertFalse(self.notice.is_read_by(other))
