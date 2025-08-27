import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { RegisterForm } from '@/views/auth/Register.vue'
import type { LoginForm } from '@/views/auth/Login.vue'
import { authService } from '@/api/auth';
import { ElMessage } from 'element-plus'
type UserRole = 'student' | 'teacher'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>('')
  const userInfo = ref<{
    username: string
    role: UserRole
    email?: string
    student_id?: string
    faculty?: string
  } | null>(null)
  const isLoading = ref(false)

  // 计算属性 - 使用立即执行的函数确保初始化
  const isStudent = computed(() => userInfo.value?.role === 'student')
  const isAuthenticated = computed(() => Boolean(token.value))
  // 初始化方法 - 添加类型检查
  const initAuth = () => {
    const savedToken = localStorage.getItem('token') || sessionStorage.getItem('token')
    const savedUser = localStorage.getItem('userInfo') || sessionStorage.getItem('userInfo')

    if (savedToken && savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser)
        // 验证存储的数据结构
        if (parsedUser && typeof parsedUser === 'object' && 'username' in parsedUser && 'role' in parsedUser) {
          token.value = savedToken
          userInfo.value = parsedUser
        } else {
          clearStorage() // 无效数据则清除
        }
      } catch (e) {
        console.error('用户信息解析失败:', e)
        clearStorage()
      }
    }
  }

  // 新增：清理存储的辅助方法
  const clearStorage = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('userInfo')
  }

  // 登录方法 - 优化存储逻辑
  const login = async (formData: LoginForm) => {
    isLoading.value = true
    try {
      // 调用真实 API 服务
      const response = await authService.login(formData);
      console.log('登录响应:', response);

      token.value = response.access;
      userInfo.value = {
        username: response.username,
        role: response.role,
        email: response.email,
        student_id: response.student_id,  // 存储学号
        faculty: response.faculty    // 存储学院
      };

      // 清除旧存储
      clearStorage();

      // 根据记住我选项选择存储方式
      if (formData.rememberMe) {
        localStorage.setItem('token', token.value);
        localStorage.setItem('userInfo', JSON.stringify(userInfo.value));
      } else {
        sessionStorage.setItem('token', token.value);
        sessionStorage.setItem('userInfo', JSON.stringify(userInfo.value));
      }
      return true;
    } catch (error: any) {
      // 标准化错误消息
      let errorMessage = '登录失败，请重试'
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  // 在 useAuthStore 中添加
  const register = async (formData: RegisterForm) => {
    isLoading.value = true;
    try {
      // 调用真实 API 服务
      await authService.register(formData);
      ElMessage.success('注册成功！');
      return true;
    } catch (error: any) {
      let errorMessage = '注册失败，请重试'
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false;
    }
  }
  // 新增方法：更新用户个人信息
  const updateUserProfile = async (profileData: {
    student_id?: string,
    faculty?: string
  }) => {
    if (!userInfo.value) return;

    try {
      // 调用后端API更新个人信息
      await authService.updateUserProfile(profileData);

      // 更新本地存储
      userInfo.value.student_id = profileData.student_id || userInfo.value.student_id;
      userInfo.value.faculty = profileData.faculty || userInfo.value.faculty;

      // 更新本地存储
      const storage = localStorage.getItem('token') ? localStorage : sessionStorage;
      storage.setItem('userInfo', JSON.stringify(userInfo.value));

      ElMessage.success('个人信息更新成功');
    } catch (error) {
      ElMessage.error('更新失败');
    }
  }
  // 登出方法
  const logout = () => {
    token.value = ''
    userInfo.value = null
    clearStorage()
  }

  // 重要：应用启动时立即初始化
  initAuth()

  return { token, userInfo, isAuthenticated, isLoading, register, login, logout, updateUserProfile, isStudent }
})
