<template>
  <div class="personal-info">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-title-container">
            <span class="header-title">个人信息</span>
            <el-tag type="success" class="identity-tag">
              <el-icon class="tag-icon"><UserFilled /></el-icon>
              {{ authStore.isStudent ? '学生' : '教师' }}
            </el-tag>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="toggleEdit">
              {{ isEditing ? '保存信息' : '编辑信息' }}
            </el-button>
            <el-button type="warning" @click="showPasswordDialog"> 修改密码 </el-button>
            <el-button type="danger" @click="handleLogout"> 退出登录 </el-button>
          </div>
        </div>
      </template>

      <!-- 头像上传 -->
      <div class="avatar-section">
        <el-upload
          class="avatar-uploader"
          action="/api/upload"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
        >
          <el-image v-if="form.avatar" :src="form.avatar" class="avatar" fit="cover" />
          <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
        </el-upload>
        <div class="avatar-tips">.</div>
      </div>

      <!-- 信息表单 -->
      <div class="form-container">
        <!-- 学号信息组 -->
        <div class="form-item-group">
          <div class="label-wrapper">
            <span class="form-label">学工号信息</span>
            <el-icon class="field-icon"><Document /></el-icon>
          </div>
          <el-input
            v-model="form.student_id"
            :disabled="!isEditing"
            placeholder="请输入学工号"
            class="centered-input"
          />
        </div>

        <!-- 学院信息组 -->
        <div class="form-item-group">
          <div class="label-wrapper">
            <span class="form-label">所属学院</span>
            <el-icon class="field-icon"><School /></el-icon>
          </div>
          <el-input
            v-model="form.faculty"
            :disabled="!isEditing"
            placeholder="请输入学院名称"
            class="centered-input"
          />
        </div>

        <!-- 电子邮箱组 -->
        <div class="form-item-group">
          <div class="label-wrapper">
            <span class="form-label">电子邮箱</span>
            <el-icon class="field-icon"><Message /></el-icon>
          </div>
          <el-input
            v-model="form.email"
            disabled
            placeholder="邮箱"
            class="centered-input"
          />
        </div>
      </div>

      <!-- 修改密码对话框 -->
      <el-dialog
        v-model="passwordDialogVisible"
        title="修改密码"
        width="500px"
        :close-on-click-modal="false"
      >
        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-width="100px"
        >
          <el-form-item label="旧密码" prop="oldPassword">
            <el-input
              v-model="passwordForm.oldPassword"
              type="password"
              show-password
              placeholder="请输入当前密码"
            />
          </el-form-item>
          <el-form-item label="新密码" prop="newPassword">
            <el-input
              v-model="passwordForm.newPassword"
              type="password"
              show-password
              placeholder="8-20位字母数字组合"
            />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="passwordForm.confirmPassword"
              type="password"
              show-password
              placeholder="请再次输入新密码"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitPasswordForm" :loading="isSubmitting">
            确认修改
          </el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { UserFilled, Document, School, Plus, Message } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/authStore.ts'
const authStore = useAuthStore()
// 个人信息相关
const isEditing = ref(false)
const form = ref({
  avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
  student_id: authStore.userInfo?.student_id || '',
  faculty: authStore.userInfo?.faculty || '',
  email: authStore.userInfo?.email || '' // 使用登录时存储的邮箱
})

const toggleEdit = async () => {
  isEditing.value = !isEditing.value
  if (!isEditing.value) {
    // 保存时调用更新方法
    try {
      await authStore.updateUserProfile({
        student_id: form.value.student_id,
        faculty: form.value.faculty
      })
      ElMessage.success('个人信息已保存')
    } catch (error) {
      ElMessage.error('保存失败')
    }
  }
}

const handleAvatarSuccess = (res: any) => {
  form.value.avatar = res.data.url
}

// 密码修改相关
const passwordDialogVisible = ref(false)
const passwordFormRef = ref<FormInstance>()
const isSubmitting = ref(false)
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const validatePassword = (rule: any, value: string, callback: Function) => {
  const regex = /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{8,20}$/
  if (!value) {
    callback(new Error('密码不能为空'))
  } else if (!regex.test(value)) {
    callback(new Error('密码必须为8-20位字母数字组合'))
  } else {
    callback()
  }
}

const validateConfirm = (rule: any, value: string, callback: Function) => {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  oldPassword: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  newPassword: [{ required: true, validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ required: true, validator: validateConfirm, trigger: 'blur' }],
}

const showPasswordDialog = () => {
  passwordDialogVisible.value = true
}

const submitPasswordForm = () => {
  passwordFormRef.value?.validate(async (valid) => {
    if (valid) {
      isSubmitting.value = true
      try {
        // 这里调用修改密码API
        // await updatePassword(passwordForm)
        ElMessage.success('密码修改成功')
        passwordDialogVisible.value = false
        passwordFormRef.value?.resetFields()
      } catch (error) {
        ElMessage.error('密码修改失败')
      } finally {
        isSubmitting.value = false
      }
    }
  })
}

// 退出登录
import { useRouter } from 'vue-router'
import type { fa } from 'element-plus/es/locales.mjs'
const router = useRouter()
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      // 实际开发中需要清除token等操作
      // localStorage.removeItem('token')
      // router.push('/login')
      ElMessage.success('已安全退出')
      setTimeout(() => {
        // 确保用户看到退出反馈
        router.push('/login')
      }, 1600)
    })
    .catch(() => {})
}
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;

  .header-title-container {
    display: flex;
    align-items: center;
    gap: 12px;

    .header-title {
      font-size: 18px;
      font-weight: 600;
    }

    .identity-tag {
      padding: 4px 10px;
      border-radius: 12px;
      .tag-icon {
        vertical-align: -2px;
        margin-right: 4px;
        font-size: 14px;
      }
    }
  }

  .header-actions {
    display: flex;
    gap: 12px;

    .el-button {
      padding: 8px 15px;
      border-radius: 6px;
    }
  }
}

.avatar-section {
  text-align: center;
  margin-bottom: 30px;

  .avatar-uploader {
    margin: 0 auto;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    overflow: hidden;
    cursor: pointer;
    border: 2px dashed var(--el-border-color);
    transition: border-color 0.3s;

    &:hover {
      border-color: var(--el-color-primary);
    }

    .avatar {
      width: 100%;
      height: 100%;
    }

    .avatar-uploader-icon {
      width: 100%;
      height: 100%;
      font-size: 28px;
      color: #8c939d;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }

  .avatar-tips {
    margin-top: 10px;
    color: #999;
    font-size: 12px;
  }
}

.form-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 20px;

  .form-item-group {
    width: 100%;
    max-width: 400px;
    margin-bottom: 25px;

    .label-wrapper {
      display: inline-flex;
      align-items: center;
      margin-bottom: 12px;
      padding: 4px 8px;
      border-radius: 4px;
      background: rgba(64, 158, 255, 0.1);
      transition: all 0.2s;

      &:hover {
        background: rgba(64, 158, 255, 0.2);
      }

      .form-label {
        color: #409eff;
        font-size: 14px;
        font-weight: 500;
        margin-right: 8px;
      }

      .field-icon {
        color: #409eff;
        font-size: 16px;
        margin-right: 0;
      }
    }

    .centered-input {
      width: 100%;

      :deep(.el-input__wrapper) {
        padding: 8px 15px;
        border-radius: 8px;
        width: 100%;
        transition: all 0.3s;

        &:hover {
          box-shadow: 0 0 0 1px #409eff inset;
        }

        &.is-disabled {
          background: #f5f7fa;
        }
      }
    }
  }
}

:deep(.el-dialog) {
  border-radius: 8px;

  .el-dialog__header {
    margin-right: 0;
    border-bottom: 1px solid #eee;
    padding: 20px;
  }

  .el-dialog__body {
    padding: 20px;
  }

  .el-form-item__label {
    color: #606266;
  }

  .el-input__wrapper {
    border-radius: 6px;
  }
}
</style>
