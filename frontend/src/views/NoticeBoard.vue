<template>
  <div class="notice-page">
    <!-- 搜索过滤栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchText"
        placeholder="搜索公告..."
        clearable
        style="width: 300px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-select
        v-model="filterType"
        placeholder="全部类型"
        clearable
        style="margin-left: 15px; width: 150px"
      >
        <el-option
          v-for="type in noticeTypes"
          :key="type.value"
          :label="type.label"
          :value="type.value"
        />
      </el-select>

      <!-- 发布公告按钮 -->
      <el-button v-if="!authStore.isStudent" type="primary" style="margin-left: 20px" @click="toggleSetForm">
        发布公告
      </el-button>
    </div>

    <!-- 学生端未读信息显示 -->
    <div v-if="authStore.isStudent" class="unread-info">
      <el-tag type="info">
        未读公告: <span class="unread-count">{{ unreadCount }}</span>
      </el-tag>
    </div>

    <!-- 发布公告表单 -->
    <el-card v-if="isSetFormVisible" class="set-card">
      <h2>{{ editingNoticeId ? '编辑公告' : '发布公告' }}</h2>
      <el-form :model="setForm" label-width="100px">
        <el-form-item label="公告标题">
          <el-input v-model="setForm.title" placeholder="请输入公告标题" />
        </el-form-item>

        <el-divider>公告内容</el-divider>
        <el-form-item label="公告内容">
          <el-input
            v-model="setForm.content"
            type="textarea"
            rows="4"
            placeholder="请输入公告内容"
          />
        </el-form-item>

        <!-- 选择公告类型 -->
        <el-form-item label="公告类型">
          <el-select v-model="setForm.type" placeholder="选择公告类型" :teleported="false">
            <el-option
              v-for="type in noticeTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" plain @click="submitNotice">
            {{ editingNoticeId ? '更新公告' : '发布公告' }}
          </el-button>
          <el-button plain @click="resetForm">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>


    <!-- 公告列表 -->
    <el-scrollbar height="calc(100vh - 230px)">
      <div class="notice-list">
        <el-card
          v-for="notice in filteredNotices"
          :key="notice.id"
          class="notice-item"
          shadow="hover"
          :class="{ unread: authStore.isStudent && !notice.is_read }"
          @click="markNoticeRead(notice)"
        >
          <!-- 学生端未读标记 - 小红点 -->
          <div v-if="authStore.isStudent && !notice.is_read" class="unread-dot"></div>

          <div class="notice-header">
            <el-tag
              :type="noticeTypeMap[notice.type].type"
              size="small"
              effect="plain"
            >
              {{ noticeTypeMap[notice.type].label }}
            </el-tag>
            <h3 class="title">{{ notice.title }}</h3>
            <el-icon v-if="notice.is_top" class="top-icon"><Top /></el-icon>
            <span class="time">{{ notice.formatted_date }}</span>
            <span class="author">发布者: {{ notice.author_name }}</span>

            <!-- 修改点1：显示已读数量（教师端和学生端都显示） -->
            <span class="read-count">
              已读: {{ notice.read_count || 0 }}
            </span>

            <!-- 编辑和删除按钮（教师端） -->
            <div v-if="!authStore.isStudent" class="actions">
              <el-button size="small" @click="editNotice(notice)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteNotice(notice.id)">删除</el-button>
            </div>
          </div>
          <div class="content">{{ notice.content }}</div>
        </el-card>
      </div>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/authStore'
import { Search, Top } from '@element-plus/icons-vue'
import { NoticeApi, type Notice } from '@/api/notice'
import { useNoticeStore } from '@/stores/noticeStore'

const authStore = useAuthStore()
const noticeStore = useNoticeStore()

const isSetFormVisible = ref(false)
const toggleSetForm = () => {
  isSetFormVisible.value = !isSetFormVisible.value
}

// 公告数据
const notices = ref<Notice[]>([])

// 类型配置
const noticeTypes = [
  { value: 1, label: '安全公告', type: 'danger' },
  { value: 2, label: '课程通知', type: 'success' },
  { value: 3, label: '设备维护', type: 'warning' }
]

const noticeTypeMap = Object.fromEntries(
  noticeTypes.map(t => [t.value, t])
)

// 未读公告数量（用于导航栏显示）
const unreadCount = ref(0)

// 搜索过滤
const searchText = ref('')
const filterType = ref<number | null>(null)

const filteredNotices = computed(() => {
  return notices.value.filter(n => {
    const matchText = searchText.value
      ? n.title.includes(searchText.value) ||
        n.content.includes(searchText.value)
      : true

    const matchType = filterType.value
      ? n.type === filterType.value
      : true

    return matchText && matchType
  }).sort((a, b) => {
    // 使用后端返回的is_top字段
    if (a.is_top !== b.is_top) return a.is_top ? -1 : 1
    // 使用 date 字段排序
    return new Date(b.date).getTime() - new Date(a.date).getTime()
  })
})

// 公告发布表单
const setForm = ref({
  title: '',
  content: '',
  type: 1,
})

const editingNoticeId = ref<number | null>(null)

// 重置表单
const resetForm = () => {
  setForm.value = {
    title: '',
    content: '',
    type: 1,
  }
  editingNoticeId.value = null
  isSetFormVisible.value = false
}


const markNoticeRead = async (notice: Notice) => {
  try {
    // 学生用户处理未读标记
    if (authStore.isStudent && !notice.is_read) {
      await NoticeApi.markAsRead(notice.id)

      // 即使API调用成功，有时需要手动更新状态
      // 刷新公告列表以获取最新状态
      await fetchNotices()

      // 刷新未读数量
      await noticeStore.fetchUnreadCount()

      // 触发事件让父组件更新导航栏未读数量
      window.dispatchEvent(new CustomEvent('update-unread-count', {
        detail: { count: noticeStore.unreadCount }
      }));
    } else {
      // 教师用户只需正常打开公告，不执行标记操作
      console.log(`[INFO] 教师用户 ${authStore.userInfo?.username} 查看公告 ${notice.id}`)
    }
  } catch (error) {
    console.error('标记公告为已读失败:', error)
    // 只在学生用户时显示错误消息
    if (authStore.isStudent) {
      // 特定错误处理
      if (error.status === 500) {
        ElMessage.error('标记公告失败，正在刷新数据')
        // 刷新数据
        await fetchNotices()
        await noticeStore.fetchUnreadCount()
      } else {
        ElMessage.error('标记公告失败')
      }
    }
  }
}

// 获取公告列表
const fetchNotices = async () => {
  try {
    const data = await NoticeApi.getNotices()
    notices.value = data

    // 学生端获取未读数量
    if (authStore.isStudent) {
      fetchUnreadCount()
    }
  } catch (error: any) {
    console.error('获取公告失败:', error)
    if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('获取公告失败，请检查网络连接')
    }
  }
}

// 获取未读公告数量
const fetchUnreadCount = async () => {
  try {
    if (authStore.isStudent) {
      // 调用API获取未读数量
      const count = await NoticeApi.getUnreadCount()
      unreadCount.value = count

      // 触发事件让父组件更新导航栏未读数量
      window.dispatchEvent(new CustomEvent('update-unread-count', {
        detail: { count }
      }));
    }
  } catch (error) {
    console.error('获取未读公告数量失败:', error)
    unreadCount.value = 0
  }
}

// 发布/更新公告
const submitNotice = async () => {
  if (!setForm.value.title || !setForm.value.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }

  try {
    if (editingNoticeId.value) {
      await NoticeApi.updateNotice({
        id: editingNoticeId.value,
        title: setForm.value.title,
        content: setForm.value.content,
        type: setForm.value.type,
      })
      ElMessage.success('公告更新成功')
    } else {
      await NoticeApi.createNotice({
        title: setForm.value.title,
        content: setForm.value.content,
        type: setForm.value.type,
      })
      ElMessage.success('公告发布成功')
    }

    resetForm()
    await fetchNotices()

    // 公告更新后刷新未读数量
    if (authStore.isStudent) {
      fetchUnreadCount()
    }
  } catch (error: any) {
    console.error('操作失败详情:', error)
    if (error.response) {
      console.error('服务器响应:', error.response.data)
      ElMessage.error(`操作失败: ${error.response.data.detail || error.response.statusText}`)
    } else if (error.request) {
      console.error('无响应:', error.request)
      ElMessage.error('服务器未响应，请检查网络连接')
    } else {
      console.error('错误详情:', error.message)
      ElMessage.error(`操作失败: ${error.message}`)
    }
  }
}

// 编辑公告
const editNotice = (notice: Notice) => {
  // 避免事件传播到卡片点击事件
  event?.stopPropagation()

  setForm.value = {
    title: notice.title,
    content: notice.content,
    type: notice.type,
  }
  editingNoticeId.value = notice.id
  isSetFormVisible.value = true
}

// 删除公告
const deleteNotice = async (id: number) => {
  // 避免事件传播到卡片点击事件
  event?.stopPropagation()

  try {
    await NoticeApi.deleteNotice(id)
    ElMessage.success('公告删除成功')
    await fetchNotices()

    // 公告删除后刷新未读数量
    if (authStore.isStudent) {
      fetchUnreadCount()
    }
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除公告失败')
  }
}

onMounted(() => {
  fetchNotices()

  // 如果学生登录，则获取未读公告数量
  if (authStore.isAuthenticated && authStore.isStudent) {
    fetchUnreadCount()
  }
})

// 暴露未读数量给父组件
defineExpose({
  unreadCount
})
</script>

<style scoped lang="scss">
.notice-page {
  padding: 20px;
  height: 100%;

  .filter-bar {
    margin-bottom: 20px;
    display: flex;
    align-items: center;
  }

  .set-card {
    margin-bottom: 20px;
  }

  .unread-info {
    margin-bottom: 15px;
    padding: 5px 10px;
    background-color: #f0f4ff;
    border-radius: 4px;
    font-size: 14px;

    .unread-count {
      font-weight: bold;
      color: #f56c6c;
      margin-left: 5px;
    }
  }

  .notice-list {
    padding-right: 15px;

    .notice-item {
      margin-bottom: 15px;
      transition: transform 0.3s;
      position: relative;
      cursor: pointer;

      &:hover {
        transform: translateX(5px);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
      }

      // 修改点4：学生端未读公告样式
      &.unread {
        border-left: 3px solid #409eff;
        background-color: rgba(64, 158, 255, 0.05);
      }

      // 修改点5：小红点样式
      .unread-dot {
        position: absolute;
        top: 15px;
        left: 15px;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #f56c6c;
      }

      .notice-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
        flex-wrap: wrap;

        .title {
          margin: 0;
          flex: 1;
          font-size: 16px;
          color: var(--el-text-color-primary);
          min-width: 200px;
        }

        .time {
          color: var(--el-text-color-secondary);
          font-size: 12px;
          white-space: nowrap;
        }

        .author {
          color: var(--el-text-color-secondary);
          font-size: 12px;
          margin-right: 10px;
        }

        .read-count {
          font-size: 12px;
          color: #909399;
          margin-left: auto;
          min-width: 80px;
          text-align: right;
        }

        .top-icon {
          color: var(--el-color-warning);
        }

        .actions {
          margin-left: auto;
        }
      }

      .content {
        color: var(--el-text-color-regular);
        line-height: 1.6;
        white-space: pre-wrap;
        margin-bottom: 10px;
      }
    }
  }

  .notice-item.unread {
    border-left: 3px solid #409eff;
    background-color: rgba(64, 158, 255, 0.05);
  }
}
</style>
