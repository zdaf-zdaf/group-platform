<script setup lang="ts">
import { ref, reactive, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/authStore'
import type { FormInstance, FormRules } from 'element-plus'

// 注册表单类型
export interface RegisterForm {
  username: string
  email: string
  password: string
  confirmPassword: string
  role: 'student' | 'teacher'
  agreedToTerms: boolean
}

// 组件逻辑
const router = useRouter()
const authStore = useAuthStore()

const registerFormRef = ref<FormInstance>()
const isLoading = ref(false)
const showSuccess = ref(false)
const redirectTimer = ref<number | null>(null)

const registerForm = reactive<RegisterForm>({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: 'student',
  agreedToTerms: false
})

// 自定义密码验证规则
const validatePassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6 || value.length > 18) {
    callback(new Error('密码长度必须在6到18个字符之间'))
  } else {
    callback()
  }
}

// 确认密码验证
const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 验证规则
const rules = reactive<FormRules<RegisterForm>>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 16, message: '长度在3到16个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择身份', trigger: 'change' }
  ],
  agreedToTerms: [
    {
      validator: (rule: any, value: boolean, callback: any) => {
        if (!value) {
          callback(new Error('请同意用户协议和隐私政策'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
})

// 注册处理
const handleRegister = async () => {
  if (!registerFormRef.value) return

  try {
    isLoading.value = true
    if (redirectTimer.value) {
      clearTimeout(redirectTimer.value)
      redirectTimer.value = null
    }
    // 验证表单
    await registerFormRef.value.validate()

    // 调用注册方法
    await authStore.register(registerForm)

    // 显示成功消息
    ElMessage.success('注册成功！')
    showSuccess.value = true

    // 3秒后跳转到登录页面
    redirectTimer.value = setTimeout(() => {
      if (router.currentRoute.value.name === 'Register') {
        router.push({ name: 'Login' })
      }
    }, 3000) as unknown as number

  } catch (error: any) {
    // 增强错误处理
    let errorMessage = '注册失败'

    if (error.message.includes('already exists')) {
      errorMessage = '用户名或邮箱已被注册'
    } else if (error.message.includes('password')) {
      errorMessage = '密码不符合要求'
    } else if (error.message.includes('network')) {
      errorMessage = '网络连接失败，请检查网络'
    } else if (error.message) {
      errorMessage = error.message
    }

    ElMessage.error(errorMessage)
  } finally {
    isLoading.value = false
  }
}
onBeforeUnmount(() => {
  if (redirectTimer.value) {
    clearTimeout(redirectTimer.value)
  }
})
</script>

<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <h2 class="auth-title">创建新账户</h2>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="rules"
        label-width="100px"
        label-position="top"
        status-icon
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入3-16位用户名"
            clearable
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱地址"
            clearable
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入6-18位密码"
            show-password
          />
          <div class="password-tips">密码应包含字母和数字，长度6-18位</div>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="身份" prop="role">
          <el-select
            v-model="registerForm.role"
            placeholder="请选择身份"
            class="full-width"
          >
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </el-form-item>

        <el-form-item prop="agreedToTerms">
          <el-checkbox v-model="registerForm.agreedToTerms">
            我已阅读并同意
            <a href="#" class="terms-link">用户协议</a>
            和
            <a href="#" class="terms-link">隐私政策</a>
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="full-width"
            @click="handleRegister"
            :loading="isLoading"
          >
            注册账号
          </el-button>
        </el-form-item>

        <div v-if="showSuccess" class="success-message">
          <i class="el-icon-success"></i> 注册成功！正在跳转到登录页面...
        </div>
      </el-form>

      <div class="auth-footer">
        已有账户？<router-link to="/login" class="auth-link">立即登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;

  .auth-card {
    width: 500px;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);

    .auth-title {
      text-align: center;
      margin-bottom: 30px;
      color: #409eff;
      font-size: 24px;
      position: relative;

      &::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 50px;
        height: 3px;
        background-color: #409eff;
        border-radius: 2px;
      }
    }

    .full-width {
      width: 100%;
    }

    .auth-footer {
      margin-top: 20px;
      text-align: center;
      color: #606266;
      font-size: 14px;
    }

    .auth-link {
      color: #409eff;
      text-decoration: none;
      margin-left: 5px;

      &:hover {
        text-decoration: underline;
      }
    }

    .password-tips {
      color: #909399;
      font-size: 12px;
      margin-top: 5px;
    }

    .terms-link {
      color: #409eff;
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }
    }

    .success-message {
      margin-top: 15px;
      text-align: center;
      color: #67c23a;
      font-size: 14px;

      .el-icon-success {
        margin-right: 5px;
      }
    }
  }
}
</style>
