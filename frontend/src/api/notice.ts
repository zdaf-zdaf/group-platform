import axios from 'axios';
import type { AxiosError } from 'axios';
import { useAuthStore } from '@/stores/authStore';
import { ElMessage } from 'element-plus';

// 创建 Axios 实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'X-Requested-With': 'XMLHttpRequest'
  }
});

// 请求拦截器 - 添加 Token
api.interceptors.request.use((config) => {
  const authStore = useAuthStore();

  // 优先从authStore获取token，而不是localStorage
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
  }

  // 打印请求调试信息
  console.log(`发送请求: ${config.method?.toUpperCase()} ${config.url}`, {
    params: config.params,
    data: config.data,
    headers: config.headers
  });

  return config;
}, (error) => {
  console.error('请求拦截器错误:', error);
  return Promise.reject(error);
});

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  (response) => {
    // 打印成功响应信息
    console.log(`请求成功: ${response.config.url}`, {
      status: response.status,
      data: response.data
    });
    return response;
  },
  (error) => {
    const axiosError = error as AxiosError;

    // 详细的错误日志
    console.error('请求错误:', {
      url: axiosError.config?.url,
      method: axiosError.config?.method,
      status: axiosError.response?.status,
      statusText: axiosError.response?.statusText,
      responseData: axiosError.response?.data,
      config: axiosError.config
    });

    if (axiosError.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      const authStore = useAuthStore();
      authStore.logout();
      window.location.href = '/login';
    } else if (axiosError.response?.status === 403) {
      // 添加更详细的403错误处理
      const errorDetail = (axiosError.response.data as any)?.detail || '无权限操作';
      ElMessage.error(`权限不足: ${errorDetail}`);
    } else {
      ElMessage.error('请求失败，请稍后再试');
    }

    return Promise.reject(axiosError);
  }
);

// 类型声明
export interface Notice {
  id: number;
  title: string;
  content: string;
  type: number;
  created_at: string;
  is_top: boolean;
  created_by: number;
  created_by_name: string;
  formatted_date?: string;
  author_name?: string;
  is_read?: boolean;
  read_count?: number;
}

export interface CreateNoticeParams {
  title: string;
  content: string;
  type: number;
  attachments?: File[];
}

export interface UpdateNoticeParams {
  id: number;
  title: string;
  content: string;
  type: number;
  attachments?: File[];
}

// 统一的 NoticeApi 类
export class NoticeApi {
  // 获取公告列表
  static async getNotices(search?: string, type?: number): Promise<Notice[]> {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (type) params.append('type', type.toString());

    try {
      const response = await api.get<Notice[]>('/api/notices/', { params });
      return response.data;
    } catch (error) {
      throw new Error('获取实验列表失败');
    }
  }

  // 创建公告
  static async createNotice(params: CreateNoticeParams): Promise<Notice> {
    try {
      const response = await api.post<Notice>('/api/notices/', {
        title: params.title,
        content: params.content,
        type: params.type
      });
      return response.data;
    } catch (error) {
      throw new Error('创建公告失败');
    }
  }

  // 更新公告
  static async updateNotice(params: UpdateNoticeParams): Promise<Notice> {
    try {
      const response = await api.put<Notice>(`/api/notices/${params.id}/`, {
        title: params.title,
        content: params.content,
        type: params.type
      });
      return response.data;
    } catch (error) {
      throw new Error('更新公告失败');
    }
  }

  // 删除公告
  static async deleteNotice(id: number): Promise<void> {
    try {
      await api.delete(`/api/notices/${id}/`);
    } catch (error) {
      throw new Error('删除公告失败');
    }
  }

  // 获取未读公告数量
  static async getUnreadCount(): Promise<number> {
    try {
      const response = await api.get<{count: number}>('/api/notices/unread_count/');
      return response.data.count;
    } catch (error) {
      throw new Error('获取未读公告数量失败');
    }
  }

  // 标记所有公告为已读
  static async markAllAsRead(): Promise<void> {
    try {
      console.log('[DEBUG] 尝试标记所有公告为已读', {
        auth: useAuthStore().token ? '已认证' : '未认证'
      });

      const response = await api.post('/api/notices/mark_all_read/');
      console.log('[DEBUG] 标记所有公告成功');
      return response.data;
    } catch (error: any) {
      throw new Error('标记所有公告为已读失败');
    }
  }

  // 标记单个公告为已读
  static async markAsRead(id: number): Promise<void> {
    const authStore = useAuthStore()

    // 只在学生用户时调用API
    if (authStore.isStudent) {
      try {
        const response = await api.post(`/api/notices/${id}/mark_as_read/`, null, {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          },
          validateStatus: (status) => {
            // 接受400-499状态码作为可处理错误
            return status < 500 || status >= 400 && status < 500;
          }
        })

        // 处理403状态码
        if (response.status === 403) {
          throw new Error(response.data.detail || '无权限操作')
        }

        // 处理500错误
        if (response.status === 500) {
          throw new Error(response.data.detail || '服务器内部错误')
        }

        return response.data
      } catch (error: any) {
        console.error('标记单个公告为已读失败:', {
          status: error.response?.status,
          data: error.response?.data,
          config: error.config
        })

        // 创建新的错误对象，携带更多信息
        const enrichedError = new Error(error.message)
        enrichedError.status = error.response?.status
        enrichedError.response = error.response

        throw enrichedError
      }
    } else {
      // 教师用户不需要调用API
      console.log(`[INFO] 教师用户 ${authStore.userInfo?.username} 不需要标记公告为已读`)
    }
  }

}
