from locust import HttpUser, task, between

class NoticeUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        # 教师注册并登录，获取token
        teacher_reg = self.client.post("/auth/register/", json={
            "username": "teacher_locust",
            "password": "12345678",
            "email": "teacher_locust@example.com",
            "role": "teacher"
        })
        teacher_login = self.client.post("/auth/login/", json={
            "username": "teacher_locust",
            "password": "12345678"
        })
        if teacher_login.status_code == 200:
            self.teacher_token = teacher_login.json().get("access")
        else:
            self.teacher_token = None

        # 学生注册并登录，获取token
        student_reg = self.client.post("/auth/register/", json={
            "username": "student_locust",
            "password": "12345678",
            "email": "student_locust@example.com",
            "role": "student"
        })
        student_login = self.client.post("/auth/login/", json={
            "username": "student_locust",
            "password": "12345678"
        })
        if student_login.status_code == 200:
            self.student_token = student_login.json().get("access")
        else:
            self.student_token = None

        # 教师创建一条公告，保存公告ID
        if self.teacher_token:
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            notice = self.client.post("/notices/", json={
                "title": "Locust Test Notice",
                "content": "This is a test notice.",
                "type": 1
            }, headers=headers)
            if notice.status_code == 201:
                self.notice_id = notice.json().get("id")
            else:
                self.notice_id = 1  # 默认ID

    @task
    def list_notices(self):
        # 学生获取公告列表
        if self.student_token:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            self.client.get("/notices/", headers=headers)

    @task
    def notice_detail(self):
        # 学生获取公告详情
        if self.student_token and hasattr(self, "notice_id"):
            headers = {"Authorization": f"Bearer {self.student_token}"}
            self.client.get(f"/notices/{self.notice_id}/", headers=headers)

    @task
    def create_notice(self):
        # 教师创建公告
        if self.teacher_token:
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            self.client.post("/notices/", json={
                "title": "Locust Create Notice",
                "content": "Created by Locust.",
                "type": 1
            }, headers=headers)

    @task
    def mark_notice_as_read(self):
        # 学生标记公告为已读
        if self.student_token and hasattr(self, "notice_id"):
            headers = {"Authorization": f"Bearer {self.student_token}"}
            self.client.post(f"/notices/{self.notice_id}/mark_as_read/", headers=headers)