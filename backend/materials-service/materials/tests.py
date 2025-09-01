# 单元测试
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model
from experiments.models import Experiment
from .models import LearningMaterial
import os

User = get_user_model()

TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'test_media')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class LearningMaterialModelTest(TestCase):
    def setUp(self):
        os.makedirs(TEST_MEDIA_ROOT, exist_ok=True)
        self.user = User.objects.create_user(username='u1', password='pwd', email='u1@t.com')
        self.experiment = Experiment.objects.create(title='Exp1', teacher=self.user)

    def tearDown(self):
        # 清理测试文件夹
        if os.path.exists(TEST_MEDIA_ROOT):
            for root, dirs, files in os.walk(TEST_MEDIA_ROOT, topdown=False):
                for name in files:
                    try:
                        os.remove(os.path.join(root, name))
                    except Exception:
                        pass
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except Exception:
                        pass

    def test_str_positive(self):
        lm = LearningMaterial.objects.create(
            title='Doc1', description='d', type='pdf',
            file=SimpleUploadedFile('a.pdf', b'12345', content_type='application/pdf'),
            created_by=self.user, question_set=self.experiment
        )
        self.assertEqual(str(lm), 'Doc1')

    def test_str_negative(self):
        lm = LearningMaterial.objects.create(
            title='', description='d', type='pdf',
            file=SimpleUploadedFile('z.pdf', b'1', content_type='application/pdf'),
            created_by=self.user, question_set=self.experiment
        )
        self.assertEqual(str(lm), '')

    def test_file_exists_negative(self):
        lm = LearningMaterial.objects.create(
            title='Doc2', description='d', type='pdf',
            file=SimpleUploadedFile('b.pdf', b'abc', content_type='application/pdf'),
            created_by=self.user, question_set=self.experiment
        )
        # 刚创建文件应存在
        self.assertTrue(lm.file_exists)
        # 删除底层文件后属性返回 False
        path = lm.file.path
        os.remove(path)
        self.assertFalse(lm.file_exists)

    def test_save_sets_size_positive(self):
        content = b'hello world'
        lm = LearningMaterial(
            title='Doc3', description='d', type='pdf',
            file=SimpleUploadedFile('c.pdf', content, content_type='application/pdf'),
            created_by=self.user, question_set=self.experiment
        )
        lm.save()
        self.assertEqual(lm.size, len(content))

    def test_save_size_not_overwrite_negative(self):
        # 如果预先设置 size，不应被覆盖
        content = b'xxxx'
        lm = LearningMaterial(
            title='Doc4', description='d', type='pdf',
            file=SimpleUploadedFile('d.pdf', content, content_type='application/pdf'),
            created_by=self.user, question_set=self.experiment, size=999
        )
        lm.save()
        self.assertEqual(lm.size, 999)
