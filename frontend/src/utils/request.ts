// src/utils/request.ts
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/authStore'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000
})

// 请求拦截器 - 添加 Token
service.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.token || localStorage.getItem('token')

    if (token) {
      config.headers['Authorization'] = `Bearer ${token}` // 确保格式正确
    }

    // 如果是文件上传，设置正确的 Content-Type
    if (config.data instanceof FormData) {
      config.headers['Content-Type'] = 'multipart/form-data'
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理 Token 过期
service.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default service
