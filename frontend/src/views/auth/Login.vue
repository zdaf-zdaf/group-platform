<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/authStore'
import type { FormInstance, FormRules } from 'element-plus'

import { authService } from '@/api/auth';

// 类型定义
export interface LoginForm {
  username: string
  password: string
  // role: 'student' | 'teacher'
  rememberMe: boolean
}

// 组件逻辑
const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()
const loginForm = reactive<LoginForm>({
  username: '',
  password: '',
  // role: 'student',
  rememberMe: false
})

// 验证规则
const rules = reactive<FormRules<LoginForm>>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 16, message: '长度在3到16个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 18, message: '长度在6到18个字符', trigger: 'blur' }
  ],
  // role: [
  //   { required: true, message: '请选择身份', trigger: 'change' }
  // ]
})

// 提交处理
const handleLogin = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  try {
    await formEl.validate()
    await authStore.login(loginForm)
    const response = await authService.login(loginForm);
    ElMessage.success('登录成功,请及时完善个人信息')
    localStorage.setItem('token', response.access);
    console.log('登录成功，当前Token:', localStorage.getItem('token'));
    router.push({ path: '/profile' })
  } catch (error) {
    ElMessage.error((error as Error).message || '登录失败')
  }
}

// 跳转到注册页面
const goToRegister = () => {
  router.push({ name: 'Register' })
}
</script>

<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="login-title">灵狐智验系统登录</h2>
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        label-width="80px"
        status-icon
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            clearable
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <!-- <el-form-item label="身份" prop="role">
          <el-select
            v-model="loginForm.role"
            placeholder="请选择身份"
            class="full-width"
          >
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </el-form-item> -->

        <el-form-item prop="rememberMe">
          <el-checkbox v-model="loginForm.rememberMe" style="margin-left: -70px;">记住登录信息</el-checkbox>
        </el-form-item>

        <el-form-item style="margin-left: -80px; margin-top: -20px;">
          <el-button
            type="primary"
            class="full-width"
            :Loading="authStore.isLoading"
            @click="handleLogin(loginFormRef)"
          >
            立即登录
          </el-button>
          <br /><br />
          <!-- 新增注册按钮
          <el-button
            type="primary"
            class="full-width"
            @click="goToRegister"
          >
            注册新账户
          </el-button> -->
          <div class="auth-footer" style="margin-left: 140px;">
          还没注册？<router-link to="/register" class="auth-link">立即注册</router-link>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;

  .login-card {
    width: 450px;
    padding: 20px;
    .auth-link {
      color: #409eff;
      text-decoration: none;
      margin-left: 5px;

      &:hover {
        text-decoration: underline;
      }
    }
    .login-title {
      text-align: center;
      margin-bottom: 30px;
      color: #409eff;
    }

    .full-width {
      width: 100%;
    }
  }
}
</style>
