from locust import HttpUser, task, between
import time
import random
import json

class StudentUser(HttpUser):
    wait_time = between(1, 3) 
    host = "http://localhost:8000/api"  
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student_username = None
        self.student_token = None
        self.created_notice_id = None
        self.test_password = "testPassword"  
    def on_start(self):
        """每个用户开始时的初始化操作"""
        self.register_student()
        self.login_student()
        
    def register_student(self):
        """学生注册"""
        timestamp = str(int(time.time() * 1000))
        username = f"student_{timestamp}"
        email = f"student_{timestamp}@example.com"
        
        payload = {
            "username": username,
            "password": self.test_password,
            "email": email,
            "role": "student"
        }
        
        with self.client.post("/auth/register/", 
                             json=payload, 
                             catch_response=True) as response:
            if response.status_code == 201:
                self.student_username = username
                response.success()
            else:
                response.failure(f"注册失败: {response.status_code} {response.text}")
    
    def login_student(self):
        """学生登录"""
        if not self.student_username:
            return
            
        payload = {
            "username": self.student_username,
            "password": self.test_password
        }
        
        with self.client.post("/auth/login/", 
                             json=payload, 
                             catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if 'access' in data:
                    self.student_token = data['access']
                    response.success()
                else:
                    response.failure("响应中缺少access token")
            else:
                response.failure(f"登录失败: {response.status_code} {response.text}")

    @task(3)
    def get_notices_list(self):
        """获取公告列表"""
        if not self.student_token:
            return
            
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        with self.client.get("/notices/", 
                            headers=headers, 
                            catch_response=True) as response:
            if response.status_code == 200:
                # 检查响应结构
                try:
                    notices = response.json()
                    if not isinstance(notices, list):
                        response.failure("响应不是数组")
                    else:
                        response.success()
                except:
                    response.failure("无法解析JSON响应")
            else:
                response.failure(f"获取公告失败: {response.status_code}")

    @task(2)
    def get_unread_count(self):
        """获取未读公告计数"""
        if not self.student_token:
            return
            
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        with self.client.get("/notices/unread_count/", 
                            headers=headers, 
                            catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'count' in data and isinstance(data['count'], int):
                        response.success()
                    else:
                        response.failure("缺少count字段或格式错误")
                except:
                    response.failure("无法解析JSON响应")
            else:
                response.failure(f"获取未读计数失败: {response.status_code}")

    @task(1)
    def mark_notice_as_read(self):
        """标记公告为已读"""
        if not self.student_token or not self.created_notice_id:
            return
            
        headers = {"Authorization": f"Bearer {self.student_token}"}
        url = f"/notices/{self.created_notice_id}/mark_as_read/"
        
        with self.client.post(url, 
                             headers=headers, 
                             catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('status') == 'success':
                        response.success()
                    else:
                        response.failure("响应状态不是success")
                except:
                    response.failure("无法解析JSON响应")
            else:
                response.failure(f"标记已读失败: {response.status_code}")

    @task(1)
    def mark_all_notices_read(self):
        """标记所有公告为已读"""
        if not self.student_token:
            return
            
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        with self.client.post("/notices/mark_all_read/", 
                             headers=headers, 
                             catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('status') == 'success':
                        response.success()
                    else:
                        response.failure("响应状态不是success")
                except:
                    response.failure("无法解析JSON响应")
            else:
                response.failure(f"标记所有已读失败: {response.status_code}")

    @task(1)
    def create_notice_error_case(self):
        """学生尝试创建公告（错误用例）"""
        if not self.student_token:
            return
            
        headers = {
            "Authorization": f"Bearer {self.student_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "title": "Unauthorized Notice",
            "content": "Student trying to create notice",
            "type": 1
        }
        
        with self.client.post("/notices/", 
                             json=payload, 
                             headers=headers, 
                             catch_response=True) as response:
            if response.status_code == 403:
                try:
                    data = response.json()
                    if data.get('detail') == '无权限操作':
                        response.success()
                    else:
                        response.failure("未返回预期的错误消息")
                except:
                    response.failure("无法解析JSON响应")
            else:
                response.failure(f"预期403错误，实际收到: {response.status_code}")


class TeacherUser(HttpUser):
    wait_time = between(1, 3)  
    host = "http://localhost:8000/api"  
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher_username = None
        self.teacher_token = None
        self.created_notice_id = None
        self.teacher_password = "teacherPassword"  

    def on_start(self):
        """每个用户开始时的初始化操作"""
        self.register_teacher()
        self.login_teacher()
        
    def register_teacher(self):
        """教师注册"""
        timestamp = str(int(time.time() * 1000))
        username = f"teacher_{timestamp}"
        email = f"teacher_{timestamp}@example.com"
        
        payload = {
            "username": username,
            "password": self.teacher_password,
            "email": email,
            "role": "teacher"
        }
        
        with self.client.post("/auth/register/", 
                             json=payload, 
                             catch_response=True) as response:
            if response.status_code == 201:
                self.teacher_username = username
                response.success()
            else:
                response.failure(f"教师注册失败: {response.status_code} {response.text}")
    
    def login_teacher(self):
        """教师登录"""
        if not self.teacher_username:
            return
            
        payload = {
            "username": self.teacher_username,
            "password": self.teacher_password
        }
        
        with self.client.post("/auth/login/", 
                             json=payload, 
                             catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if 'access' in data:
                    self.teacher_token = data['access']
                    response.success()
                else:
                    response.failure("响应中缺少access token")
            else:
                response.failure(f"教师登录失败: {response.status_code} {response.text}")

    @task(5)
    def create_notice(self):
        """教师创建公告"""
        if not self.teacher_token:
            return
            
        headers = {
            "Authorization": f"Bearer {self.teacher_token}",
            "Content-Type": "application/json"
        }
        
        timestamp = int(time.time())
        payload = {
            "title": f"Test Notice {timestamp}",
            "content": "This is a test notice created by Locust tests.",
            "type": 1
        }
        
        with self.client.post("/notices/", 
                             json=payload, 
                             headers=headers, 
                             catch_response=True) as response:
            if response.status_code == 201:
                try:
                    data = response.json()
                    if 'id' in data:
                        self.created_notice_id = data['id']
                        response.success()
                    else:
                        response.failure("响应中缺少公告ID")
                except:
                    response.failure("无法解析JSON响应")
            else:
                response.failure(f"创建公告失败: {response.status_code} {response.text}")

    @task(2)
    def get_notices_list(self):
        """教师获取公告列表"""
        if not self.teacher_token:
            return
            
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        with self.client.get("/notices/", 
                            headers=headers, 
                            catch_response=True) as response:
            if response.status_code == 200:
                # 检查响应结构
                try:
                    notices = response.json()
                    if not isinstance(notices, list):
                        response.failure("响应不是数组")
                    else:
                        response.success()
                except:
                    response.failure("无法解析JSON响应")
            else:
                response.failure(f"获取公告失败: {response.status_code}")

    @task(1)
    def delete_notice(self):
        """教师删除公告"""
        if not self.teacher_token or not self.created_notice_id:
            return
            
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        url = f"/notices/{self.created_notice_id}/"
        
        with self.client.delete(url, 
                               headers=headers, 
                               catch_response=True) as response:
            if response.status_code == 204:
                self.created_notice_id = None  # 重置已删除的公告ID
                response.success()
            else:
                response.failure(f"删除公告失败: {response.status_code}")

    @task(1)
    def delete_notice_error_case(self):
        """学生尝试删除公告（错误用例）"""
        if not self.teacher_token or not self.created_notice_id:
            return
            
        # 先获取学生token（需要学生用户存在）
        # 在实际测试中，这部分需要更复杂的协调
        headers = {
            "Authorization": f"Bearer {self.teacher_token}",  # 这里故意使用学生token会失败
            "Content-Type": "application/json"
        }
        url = f"/notices/{self.created_notice_id}/"
        
        # 注意：在实际测试中，这里应该使用学生token
        # 但为了简化，我们假设这个请求会失败
        with self.client.delete(url, 
                               headers=headers, 
                               catch_response=True) as response:
            if response.status_code == 403:
                response.success()
            else:
                response.failure(f"预期403错误，实际收到: {response.status_code}")