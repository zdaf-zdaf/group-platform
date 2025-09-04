from locust import HttpUser, task, between
import random
import string
import time

def random_text(prefix="内容", length=8):
    return prefix + ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_user(role):
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return {
        "username": f"locust_{role}_{suffix}",
        "password": "Test1234@",
        "email": f"{role}_{suffix}@test.com",
        "role": role
    }

class ForumUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        # 随机分配身份
        self.role = random.choice(["teacher", "student"])
        self.userinfo = random_user(self.role)
        self.token = None
        self.headers = {"Content-Type": "application/json"}

        # 1. 用户注册
        reg_data = {
            "username": self.userinfo["username"],
            "password": self.userinfo["password"],
            "email": self.userinfo["email"],
            "role": self.userinfo["role"]
        }
        self.client.post("/api/auth/register/", json=reg_data, headers=self.headers, name="1.用户注册")
        time.sleep(0.2)

        # 2. 用户登录
        login_data = {
            "username": self.userinfo["username"],
            "password": self.userinfo["password"]
        }
        login_resp = self.client.post("/api/auth/login/", json=login_data, headers=self.headers, name="2.用户登录")
        if login_resp.status_code == 200 and "access" in login_resp.json():
            self.token = login_resp.json()["access"]
            self.headers["Authorization"] = f"Bearer {self.token}"

        # 发一条初始化帖子
        self.post_id = None
        self.comment_id = None
        if self.token:
            title = random_text("Locust发帖_")
            content = random_text("Locust内容_")
            resp = self.client.post(
                "/api/forum/questions/",
                json={"title": title, "content": content},
                headers=self.headers,
                name="3.发帖(初始化)"
            )
            if resp.status_code in (200, 201):
                self.post_id = resp.json().get("id")

    @task(1)
    def create_post(self):
        if self.token:
            title = random_text("Locust发帖_")
            content = random_text("Locust内容_")
            resp = self.client.post(
                "/api/forum/questions/",
                json={"title": title, "content": content},
                headers=self.headers,
                name="4.发帖"
            )
            if resp.status_code in (200, 201):
                self.post_id = resp.json().get("id")

    @task(1)
    def get_post_detail(self):
        if self.post_id:
            self.client.get(f"/api/forum/questions/{self.post_id}/", headers=self.headers, name="5.获取帖子详情")

    @task(1)
    def comment_post(self):
        if self.post_id:
            resp = self.client.post(
                f"/api/forum/questions/{self.post_id}/comments/",
                json={"content": random_text("评论_")},
                headers=self.headers,
                name="6.评论帖子"
            )
            if resp.status_code in (200, 201):
                self.comment_id = resp.json().get("id")

    @task(1)
    def like_post(self):
        if self.post_id:
            self.client.patch(
                f"/api/forum/questions/{self.post_id}/toggle-like/",
                headers=self.headers,
                name="7.点赞/取消点赞"
            )

    @task(1)
    def sticky_post(self):
        if self.post_id and self.role == "teacher":
            self.client.patch(
                f"/api/forum/questions/{self.post_id}/toggle-sticky/",
                headers=self.headers,
                name="8.置顶/取消置顶"
            )

   
    @task(1)
    def delete_post(self):
        if self.post_id:
            self.client.delete(
                f"/api/forum/questions/{self.post_id}/",
                headers=self.headers,
                name="9.删除帖子"
            )
            self.post_id = None