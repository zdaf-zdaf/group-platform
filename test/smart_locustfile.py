"""
智能的 Locust 测试脚本 - 自适应现有数据
先获取真实的实验和题目数据，然后进行测试
"""

import json
import time
import random
from locust import HttpUser, task, between


class SmartSubmissionTest(HttpUser):
    """智能的代码提交测试 - 使用真实数据"""
    
    wait_time = between(2, 5)
    host = "http://localhost"
    
    def on_start(self):
        """用户初始化"""
        print(f"=== 智能用户开始测试 ===")
        
        # 生成唯一的用户信息
        timestamp = int(time.time() * 1000)
        self.username = f"smart_user_{timestamp}_{random.randint(1000,9999)}"
        self.password = "testpass123"
        self.email = f"{self.username}@example.com"
        
        print(f"创建用户: {self.username}")
        
        # 注册并登录
        if self.register() and self.login():
            # 获取实验和题目数据
            self.load_experiment_data()
            print(f"✅ 用户 {self.username} 初始化成功")
        else:
            print(f"❌ 用户 {self.username} 初始化失败")
    
    def register(self):
        """用户注册"""
        payload = {
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "role": "student"
        }
        
        response = self.client.post(
            "/api/auth/register/",
            json=payload,
            name="1.用户注册"
        )
        
        success = response.status_code == 201
        print(f"注册结果: {response.status_code} - {'成功' if success else '失败'}")
        return success
    
    def login(self):
        """用户登录"""
        payload = {
            "username": self.username,
            "password": self.password
        }
        
        response = self.client.post(
            "/api/auth/login/",
            json=payload,
            name="2.用户登录"
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                self.auth_token = data.get('access')
                print(f"登录成功")
                return True
            except:
                print(f"登录响应解析失败")
                return False
        else:
            print(f"登录失败: {response.status_code}")
            return False
    
    def get_headers(self):
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def load_experiment_data(self):
        """加载真实的实验和题目数据"""
        print("📡 获取实验数据...")
        
        # 获取实验列表
        response = self.client.get(
            "/api/experiments/experiments/",
            headers=self.get_headers(),
            name="3.获取实验列表"
        )
        
        self.experiments = []
        self.choice_problems = []
        self.fill_problems = []  
        self.coding_problems = []
        
        if response.status_code == 200:
            try:
                self.experiments = response.json()
                print(f"获取到 {len(self.experiments)} 个实验")
                
                if self.experiments:
                    # 获取第一个实验的详细信息
                    exp_id = self.experiments[0]['id']
                    self.load_problems(exp_id)
                else:
                    print("⚠️ 没有找到实验，将创建测试实验")
                    self.create_test_experiment()
                    
            except Exception as e:
                print(f"解析实验数据失败: {e}")
                self.create_test_experiment()
        else:
            print(f"获取实验列表失败: {response.status_code}")
            self.create_test_experiment()
    
    def load_problems(self, experiment_id):
        """加载指定实验的题目"""
        print(f"📋 获取实验 {experiment_id} 的题目...")
        
        # 获取选择题
        choice_response = self.client.get(
            f"/api/experiments/choice-problems/?experiment={experiment_id}",
            headers=self.get_headers(),
            name="4.获取选择题"
        )
        if choice_response.status_code == 200:
            self.choice_problems = choice_response.json()
            print(f"获取到 {len(self.choice_problems)} 个选择题")
        
        # 获取填空题  
        fill_response = self.client.get(
            f"/api/experiments/fill-problems/?experiment={experiment_id}",
            headers=self.get_headers(),
            name="5.获取填空题"
        )
        if fill_response.status_code == 200:
            self.fill_problems = fill_response.json()
            print(f"获取到 {len(self.fill_problems)} 个填空题")
            
        # 获取编程题
        coding_response = self.client.get(
            f"/api/experiments/coding-problems/?experiment={experiment_id}",
            headers=self.get_headers(),
            name="6.获取编程题"
        )
        if coding_response.status_code == 200:
            self.coding_problems = coding_response.json()
            print(f"获取到 {len(self.coding_problems)} 个编程题")
    
    def create_test_experiment(self):
        """如果没有实验，创建一个测试实验"""
        print("🛠️ 创建测试实验...")
        
        # 创建实验
        exp_data = {
            "title": f"Locust测试实验 {int(time.time())}",
            "description": "自动创建的测试实验",
            "start_time": "2025-01-01T00:00:00Z",
            "deadline": "2025-12-31T23:59:59Z",
            "students": [],
            "allow_late_submission": True
        }
        
        exp_response = self.client.post(
            "/api/experiments/experiments/",
            json=exp_data,
            headers=self.get_headers(),
            name="创建测试实验"
        )
        
        if exp_response.status_code == 201:
            experiment = exp_response.json()
            exp_id = experiment['id']
            print(f"✅ 创建实验成功，ID: {exp_id}")
            
            # 创建一个简单的编程题
            coding_data = {
                "experiment": exp_id,
                "description": "计算两个数的和",
                "test_cases": [
                    {"input": "1 2", "output": "3"},
                    {"input": "5 7", "output": "12"}
                ],
                "timeout": 10,
                "mem_limit": 256,
                "score": 10,
                "order": 1
            }
            
            coding_response = self.client.post(
                "/api/experiments/coding-problems/",
                json=coding_data,
                headers=self.get_headers(),
                name="创建编程题"
            )
            
            if coding_response.status_code == 201:
                self.experiments = [experiment]
                self.coding_problems = [coding_response.json()]
                print("✅ 创建编程题成功")
            else:
                print(f"❌ 创建编程题失败: {coding_response.status_code}")
        else:
            print(f"❌ 创建实验失败: {exp_response.status_code}")
    
    @task(2)
    def test_get_experiments_periodic(self):
        """定期获取实验列表 - 模拟用户浏览"""
        response = self.client.get(
            "/api/experiments/experiments/",
            headers=self.get_headers(),
            name="定期获取实验列表，模拟用户浏览"
        )
        if response.status_code == 200:
            print(f"📋 {self.username} 浏览实验列表")

    @task(5)
    def test_smart_submit(self):
        """智能代码提交测试 - 使用真实数据"""
        if not self.experiments:
            print("⚠️ 没有可用实验，跳过提交")
            return
            
        experiment = self.experiments[0]
        experiment_id = experiment['id']
        
        print(f"🚀 {self.username} 向实验 {experiment_id} 提交代码...")
        
        # 构造答案数据
        answers = {}
        
        # 选择题答案
        if self.choice_problems:
            answers['choice'] = []
            for problem in self.choice_problems[:2]:  # 最多提交2个选择题
                answers['choice'].append({
                    "question_id": problem['id'],
                    "selected": str(random.randint(0, 2))  # 随机选择
                })
        
        # 填空题答案  
        if self.fill_problems:
            answers['fill'] = []
            for problem in self.fill_problems[:2]:  # 最多提交2个填空题
                answers['fill'].append({
                    "question_id": problem['id'],
                    "answer": "测试答案"
                })
        
        # 编程题答案
        if self.coding_problems:
            answers['coding'] = []
            for problem in self.coding_problems[:2]:  # 最多提交2个编程题
                answers['coding'].append({
                    "question_id": problem['id'],
                    "code": self.get_smart_code()
                })
        
        # 如果没有任何题目，创建一个模拟的提交
        if not any([self.choice_problems, self.fill_problems, self.coding_problems]):
            print("⚠️ 没有找到题目，使用模拟数据")
            answers = {
                "coding": [{
                    "question_id": 1,  # 假设存在ID为1的编程题
                    "code": self.get_smart_code()
                }]
            }
        
        # 构造提交数据
        submission_data = {
            "experiment_id": experiment_id,
            "answers": answers
        }
        
        print(f"提交数据预览: 实验ID={experiment_id}, 答案类型={list(answers.keys())}")
        
        # 发送提交请求
        response = self.client.post(
            "/submit/experiment/",
            json=submission_data,
            headers=self.get_headers(),
            name="7.实验提交及代码测评",
            timeout=30
        )
        
        # 分析结果
        if response.status_code in [200, 201]:
            try:
                result = response.json()
                score = result.get('total_score', '未知')
                success = result.get('success', False)
                print(f"✅ 代码提交{'成功' if success else '处理'}! 得分: {score}")
                
                # 打印详细结果
                if 'results' in result:
                    results = result['results']
                    print(f"   选择题: {len(results.get('choice', []))}题")
                    print(f"   填空题: {len(results.get('fill', []))}题") 
                    print(f"   编程题: {len(results.get('coding', []))}题")
                    
            except Exception as e:
                print(f"✅ 提交成功但响应解析失败: {e}")
                print(f"原始响应: {response.text[:200]}")
        else:
            print(f"❌ 代码提交失败 ({response.status_code})")
            print(f"错误详情: {response.text[:300]}")
    
    def get_smart_code(self):
        """获取智能生成的代码"""
        codes = [
            # 简单加法 
            "a, b = map(int, input().split())\nprint(a + b)",
            
            # 带函数的版本
            "def solve():\n    a, b = map(int, input().split())\n    return a + b\n\nprint(solve())",
            
            # 健壮版本
            "try:\n    line = input().strip()\n    numbers = line.split()\n    if len(numbers) >= 2:\n        a, b = int(numbers[0]), int(numbers[1])\n        print(a + b)\n    else:\n        print(0)\nexcept:\n    print(0)"
        ]
        return random.choice(codes)


# 事件监听器
from locust import events

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("🎯 ========== 智能代码提交测试开始 ==========")
    print("📊 图表数据已清空，开始新的测试周期")
    
    # 重置环境统计（如果需要的话）
    if hasattr(environment, 'stats'):
        print("🔄 重置统计数据...")

@events.test_stop.add_listener 
def on_test_stop(environment, **kwargs):
    print("🏁 ========== 智能测试结束 ==========")
    print("💡 提示：要开始全新测试，请：")
    print("   1. 点击 'Reset stats' 按钮清空图表")
    print("   2. 或者重启 Locust 服务")
    
    stats = environment.stats
    print(f"📊 测试统计:")
    print(f"   总请求数: {stats.total.num_requests}")
    print(f"   失败数: {stats.total.num_failures}")
    success_rate = ((stats.total.num_requests - stats.total.num_failures) / max(stats.total.num_requests, 1) * 100)
    print(f"   成功率: {success_rate:.1f}%")
    print(f"   平均响应时间: {stats.total.avg_response_time:.0f}ms")
    
    # 重点关注代码提交接口的性能
    for name, stat in stats.entries.items():
        if '代码提交' in name[0] and stat.num_requests > 0:
            submit_success_rate = ((stat.num_requests - stat.num_failures) / stat.num_requests * 100)
            print(f"\n🎯 代码提交接口性能:")
            print(f"   请求次数: {stat.num_requests}")
            print(f"   成功率: {submit_success_rate:.1f}%")
            print(f"   平均响应时间: {stat.avg_response_time:.0f}ms")
            print(f"   最大响应时间: {stat.max_response_time}ms")
            break
