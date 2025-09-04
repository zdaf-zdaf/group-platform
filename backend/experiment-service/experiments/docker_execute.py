import time
import docker
import socket as std_socket

class DockerJudge:
    """使用Docker容器执行代码评测"""

    def __init__(self):
        self.client = docker.from_env()

    def run_code(self, problem: dict, code: str) -> dict:
        passed = 0
        details = []
        try:
            for tc in problem["test_cases"]:
                try:
                    result = self._run_container(
                        code,
                        problem["timeout"],
                        problem["mem_limit"],
                        tc["input"]
                    )
                except Exception as e:
                    result = f"Error while running code in Docker: {str(e)}"

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
        except Exception as e:
            return {
                "passed": 0,
                "total": len(problem["test_cases"]),
                "details": [],
                "error": f"Error while fetching server API version: {str(e)}"
            }

    def _run_container(self, code: str, timeout: int, mem_limit: int, input_str: str) -> str:
        container = None
        try:
            container = self.client.containers.run(
                image='python:3.9-slim',
                command=['python', '-u', '-c', code],
                stdin_open=True,
                stdout=True,
                stderr=True,
                detach=True,
                mem_limit=f'{mem_limit}m',
                network_mode='none',
            )

            try:
                sock = container.attach_socket(params={'stdin': 1, 'stream': 1})
                if input_str:
                    sock.sendall(input_str.encode('utf-8') + b'\n')
                sock.close()
            except AttributeError as e:
                return f"Error: SocketIO attribute error: {str(e)}"
            except Exception as e:
                return f"Error: SocketIO or attach_socket error: {str(e)}"

            exit_code = container.wait()['StatusCode']

            stdout = container.logs(stdout=True, stderr=False).decode('utf-8')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8')

            if exit_code != 0:
                return f"错误，退出码 {exit_code}：{stderr.strip()}"

            return stdout.strip()

        except docker.errors.DockerException as e:
            return f"Error: Docker API error: {str(e)}"
        except Exception as e:
            return f"Error: Unexpected error: {str(e)}"
        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

    def _compare_output(self, actual: str, expected: str) -> bool:
        return actual.rstrip() == expected.rstrip()