import axios from 'axios';
import type { AxiosResponse } from 'axios';
import type { LoginForm } from '@/views/auth/Login.vue';

// 配置后端基础 URL（根据你的实际后端地址修改）
const BASE_URL = 'http://localhost:8000/api/'; // Django 后端地址

// 创建 axios 实例
export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
});

// 添加请求拦截器 - 自动注入 token
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token');
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 添加响应拦截器 - 统一处理响应和错误
apiClient.interceptors.response.use(
  response => response, // 直接返回data
  error => {
    const message = error.response?.data?.message ||
                   error.response?.data?.detail ||
                   error.message;
    return Promise.reject(new Error(message));
  }
);


// 登录响应数据类型
export interface LoginResponse {
  access: string;
  refresh: string;
  username: string;
  role: 'student' | 'teacher';
  email: string; // 添加邮箱字段
  student_id?: string; // 添加学号字段
  faculty?: string; // 添加院系字段
}

// 注册请求数据类型
export interface RegisterRequest {
  username: string;
  password: string;
  email: string;
  role: 'student' | 'teacher';
}

// API 服务对象
export const authService = {
  /**
   * 用户登录
   * @param formData 登录表单数据
   * @returns 登录响应数据
   */
  async login(formData: LoginForm): Promise<LoginResponse> {
    try {
      const response = await apiClient.post<LoginResponse>('/auth/login/', {
        username: formData.username,
        password: formData.password,
      });
      return response.data; // 返回完整响应数据
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || error.message;
        throw new Error(message);
      }
      throw new Error('登录失败');
    }
  },

  /**
   * 用户注册
   * @param formData 注册表单数据
   * @returns 注册结果
   */
  async register(formData: RegisterRequest): Promise<void> {
    try {

      await apiClient.post('/auth/register/', {
        username: formData.username,
        password: formData.password,
        email: formData.email,
        role: formData.role
      });
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || error.message;
        throw new Error(message);
      } else {
        throw new Error('未知注册错误');
      }
    }
  },

  /**
   * 获取当前用户信息
   * @param token 认证令牌
   * @returns 用户信息
   */
  async getUserInfo(token: string): Promise<{ username: string; role: 'student' | 'teacher' }> {
    try {
      const response = await apiClient.get('/auth/user', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      throw new Error('获取用户信息失败');
    }
  },

  /**
   * 更新用户个人信息
   * @param data 要更新的信息
   */
  async updateUserProfile(data: { student_id?: string; faculty?: string }) {
    try {
      await apiClient.patch('/auth/user/profile/', data);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || error.message;
        throw new Error(message);
      } else {
        throw new Error('更新用户信息失败');
      }
    }
  }
};

export const forumService = {
  /**
   * 获取问题列表
   * @returns 问题列表
   */
  async getQuestions() {
    const response = await apiClient.get('/forum/questions/');
    return response;
  },
  /**
   * 创建新问题
   * @param formData 问题数据
   * @returns 创建的问题
   */
  async createQuestion(formData: { title: string; content: string}) {
    const response = await apiClient.post('/forum/questions/', formData);
    return response;
  },
  /**
   * 删除问题
   * @param questionId 问题ID
   */
  async deleteQuestion(questionId: number) {
    await apiClient.delete(`/forum/questions/${questionId}/`);
  },
  /**
   * 切换问题置顶状态
   * @param questionId 问题ID
   */
  async toggleSticky(questionId: number) {
    const response = await apiClient.patch(`/forum/questions/${questionId}/toggle-sticky/`);
    return response;
  },
  /**
   * 切换点赞状态
   * @param questionId 问题ID
   */
  async toggleLike(questionId: number) {
    const response = await apiClient.patch(`/forum/questions/${questionId}/toggle-like/`);
    return response;
  },
  /**
   * 添加评论
   * @param questionId 问题ID
   * @param content 评论内容
   */
   async addComment(questionId: number, content: string) {
    const response = await apiClient.post(`/forum/questions/${questionId}/comments/`, { content });
    return response;
   },
   /**
    * 删除评论
    * @param commentId 评论ID
    */
   async deleteComment(commentId: number) {
    await apiClient.delete(`/forum/comments/${commentId}/`);
   },
};
