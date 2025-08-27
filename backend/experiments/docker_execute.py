# server/experiment_judge/docker_execute.py
import time
import docker

import socket as std_socket

class DockerJudge:
    """使用Docker容器执行代码评测"""

    def __init__(self):
        self.client = docker.from_env()

    def run_code(self, problem: dict, code: str) -> dict:
        """执行代码评测

        :param problem: 题目配置
            {
                "name": "add",
                "timeout": 10,
                "mem_limit": 512,
                "test_cases": [{"input": "...", "output": "..."}]
            }
        :param code: 提交的代码
        :return: 评测结果字典
        """
        passed = 0
        details = []

        for tc in problem["test_cases"]:
            # 运行容器执行测试用例
            result = self._run_container(
                code,
                problem["timeout"],
                problem["mem_limit"],
                tc["input"]
            )

            # 比较输出结果
            is_passed = self._compare_output(result, tc["output"])
            details.append({
                "input": tc["input"],
                "expected": tc["output"],
                "actual": result,
                "is_passed": is_passed
            })

            if is_passed:
                passed += 1

        return {
            "passed": passed,
            "total": len(problem["test_cases"]),
            "details": details
        }

    def _run_container(self, code: str, timeout: int, mem_limit: int, input_str: str) -> str:
        container = None
        try:
            container = self.client.containers.run(
                image='python:3.9-slim',
                command=['python', '-u', '-c', code],  # -u 禁用缓冲
                stdin_open=True,
                stdout=True,
                stderr=True,
                detach=True,
                mem_limit=f'{mem_limit}m',
                network_mode='none',
            )

            # attach_socket 返回 socket-like 对象，直接操作即可
            sock = container.attach_socket(params={'stdin': 1, 'stream': 1})

            if input_str:
                sock.sendall(input_str.encode('utf-8') + b'\n')

            sock.close()

            exit_code = container.wait()['StatusCode']

            stdout = container.logs(stdout=True, stderr=False).decode('utf-8')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8')

            if exit_code != 0:
                return f"错误，退出码 {exit_code}：{stderr.strip()}"

            return stdout.strip()

        finally:
            if container:
                container.remove(force=True)

    def _compare_output(self, actual: str, expected: str) -> bool:
        """比较实际输出和预期输出"""
        return actual.rstrip() == expected.rstrip()