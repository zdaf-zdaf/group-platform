from django.test import TestCase
from unittest.mock import patch, MagicMock

from .docker_execute import DockerJudge
from .models import Experiment
from django.contrib.auth import get_user_model

User = get_user_model()

class ExperimentModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='testpass')
        self.experiment = Experiment.objects.create(title='Test Exp', teacher=self.teacher)

    def test_str_positive(self):
        self.assertEqual(str(self.experiment), 'Test Exp')

    def test_str_negative(self):
        self.experiment.title = ''
        self.assertEqual(str(self.experiment), '')


class DockerJudgeCompareOutputTest(TestCase):
    def setUp(self):
        self.judge = DockerJudge()

    def test_compare_output_positive(self):
        self.assertTrue(self.judge._compare_output('hello\n', 'hello'))

    def test_compare_output_negative(self):
        self.assertFalse(self.judge._compare_output('hello', 'world'))


class DockerJudgeRunCodeTest(TestCase):
    def setUp(self):
        self.judge = DockerJudge()

    @patch('experiments.docker_execute.DockerJudge._run_container', return_value='3')
    def test_run_code_positive(self, mock_run):
        problem = {
            'name': 'add',
            'timeout': 5,
            'mem_limit': 256,
            'test_cases': [
                {'input': '1 2', 'output': '3'},
                {'input': '10 -7', 'output': '3'},
            ]
        }
        code = 'print(eval("+".join(input().split())))'
        result = self.judge.run_code(problem, code)
        self.assertEqual(result['passed'], 2)
        self.assertEqual(result['total'], 2)
        self.assertTrue(all(d['is_passed'] for d in result['details']))

    @patch('experiments.docker_execute.DockerJudge._run_container')
    def test_run_code_negative(self, mock_run):
        # 第一条用例通过，第二条失败
        mock_run.side_effect = ['3', '4']
        problem = {
            'name': 'add',
            'timeout': 5,
            'mem_limit': 256,
            'test_cases': [
                {'input': '1 2', 'output': '3'},
                {'input': '10 -7', 'output': '3'},
            ]
        }
        code = 'print(eval("+".join(input().split())))'
        result = self.judge.run_code(problem, code)
        self.assertEqual(result['passed'], 1)
        self.assertEqual(result['total'], 2)
        self.assertEqual(result['details'][1]['actual'], '4')
        self.assertFalse(result['details'][1]['is_passed'])


class DockerJudgeRunContainerTest(TestCase):
    @patch('experiments.docker_execute.docker')
    def test_run_container_nonzero_exit(self, mock_docker):
        # 构造假的容器与行为
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client

        fake_sock = MagicMock()
        fake_container = MagicMock()
        fake_container.attach_socket.return_value = fake_sock
        fake_container.wait.return_value = {'StatusCode': 1}
        fake_container.logs.side_effect = [b'', b'Runtime error']  # stdout, stderr

        mock_client.containers.run.return_value = fake_container

        judge = DockerJudge()
        out = judge._run_container(code='print(1)', timeout=1, mem_limit=64, input_str='')
        self.assertIn('错误，退出码 1', out)
        fake_container.remove.assert_called_once()

    @patch('experiments.docker_execute.docker')
    def test_run_container_zero_exit_positive(self, mock_docker):
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client

        fake_sock = MagicMock()
        fake_container = MagicMock()
        fake_container.attach_socket.return_value = fake_sock
        fake_container.wait.return_value = {'StatusCode': 0}
        fake_container.logs.side_effect = [b'OK\n', b'']  # stdout, stderr
        mock_client.containers.run.return_value = fake_container

        judge = DockerJudge()
        out = judge._run_container(code='print("OK")', timeout=1, mem_limit=64, input_str='')
        self.assertEqual(out, 'OK')
        fake_container.remove.assert_called_once()
