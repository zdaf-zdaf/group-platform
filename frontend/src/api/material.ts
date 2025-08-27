import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/stores/authStore';
import { ElMessage } from 'element-plus';

// 创建带类型声明的 Axios 实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'X-Requested-With': 'XMLHttpRequest'
  }
});

// 请求拦截器 - 添加 Token 和 CSRF
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    console.log('当前Token:', token); // 调试

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log('请求头已添加Authorization'); // 调试
    }
    return config;
});

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      const authStore = useAuthStore();
      authStore.logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Cookie 辅助函数
function getCookie(name: string): string | undefined {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift();
}

// 类型安全的 API 接口
export interface LearningMaterial {
  id: number;
  title: string;
  description: string;
  type: 'pdf' | 'video' | 'doc' | 'image';
  size: number;
  downloads: number;
  created_at: string;
  file: string;
  file_url: string;
  created_by: number;
  cover?: string;  // 可选视频封面
  format?: string; // 文件格式扩展名
}

export const MaterialApi = {
  async getMaterials(search?: string, type?: string): Promise<LearningMaterial[]> {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (type) params.append('type', type);

    const response = await api.get<LearningMaterial[]>('/materials/', { params });
    return response.data;
  },

  async createMaterial(formData: FormData): Promise<LearningMaterial> {
    const response = await api.post<LearningMaterial>('/materials/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        // 如果需要可以添加其他头信息
      }
    });
    return response.data;
  },

  async updateMaterial(id: number, formData: FormData): Promise<LearningMaterial> {
    const response = await api.put<LearningMaterial>(`/materials/${id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  async deleteMaterial(id: number): Promise<void> {
    await api.delete(`/materials/${id}/`);
  },

  async downloadMaterial(id: number): Promise<Blob> {
    const response = await api.get<Blob>(`/materials/${id}/download/`, {
      responseType: 'blob'
    });
    return response.data;
  }
};
