<template>
  <div class="user-center">
    <!-- 侧边栏折叠按钮 -->
    <div class="collapse-btn" @click="isCollapsed = !isCollapsed">
      <el-icon :size="20">
        <component :is="isCollapsed ? 'Expand' : 'Fold'" />
      </el-icon>
    </div>

    <!-- 左侧导航（动态宽度） -->
    <div class="sidebar" :style="{ width: isCollapsed ? '64px' : '260px' }">
      <transition name="el-zoom-in-left">
        <div v-show="!isCollapsed" class="user-info">
          <el-avatar :size="80" :src="user.avatar" />
          <h2>{{ user.name }}</h2>
          <p>{{ user.email }}</p>
        </div>
      </transition>

      <el-menu
        :default-active="$route.path"
        router
        class="nav-menu"
        :collapse="isCollapsed"
        :collapse-transition="false"
      >
        <!-- 通知公告菜单项 - 添加未读计数 -->
        <el-menu-item index="/notices">
          <el-badge
            v-if="authStore.isStudent && noticeStore.unreadCount > 0"
            :value="noticeStore.unreadCount"
            :max="99"
            class="badge-item"
          >
            <el-icon><Bell /></el-icon>
            <span v-show="!isCollapsed">通知公告</span>
          </el-badge>

          <!-- 没有未读消息时显示 -->
          <template v-else>
            <el-icon><Bell /></el-icon>
            <span v-show="!isCollapsed">通知公告</span>
          </template>
        </el-menu-item>

        <el-menu-item index="/studyfile">
          <el-icon><Collection /></el-icon>
          <span v-show="!isCollapsed">学习资料</span>
        </el-menu-item>

        <el-menu-item v-if="authStore.isStudent" index="/experiments">
          <el-icon><Notebook /></el-icon>
          <span v-show="!isCollapsed">实验中心</span>
        </el-menu-item>

        <el-menu-item v-if="authStore.isStudent" index="/evaluation-history">
          <el-icon><List /></el-icon>
          <span v-show="!isCollapsed">评测记录</span>
        </el-menu-item>

        <!-- <el-menu-item v-if="authStore.isStudent" index="/discussion">
          <el-icon><List /></el-icon>
          <span v-show="!isCollapsed">讨论区</span>
        </el-menu-item> -->

        <el-menu-item v-if="!authStore.isStudent" index="/teacher-create">
          <el-icon><Notebook /></el-icon>
          <span v-show="!isCollapsed">创建实验</span>
        </el-menu-item>

        <el-menu-item v-if="!authStore.isStudent" index="/teacher-review">
          <el-icon><List /></el-icon>
          <span v-show="!isCollapsed">查看学生提交</span>
        </el-menu-item>

        <el-menu-item index="/forum">
          <el-icon><Notebook /></el-icon>
          <span v-show="!isCollapsed">答疑论坛</span>
        </el-menu-item>

        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span v-show="!isCollapsed">个人信息</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 右侧内容（动态边距） -->
    <div class="content" :style="{ marginLeft: isCollapsed ? '64px' : '260px' }">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Bell, Collection, Notebook, List, User } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/authStore'
import { useNoticeStore } from '@/stores/noticeStore' // 引入通知store

const authStore = useAuthStore()
const noticeStore = useNoticeStore() // 使用通知store
const isCollapsed = ref(false)

// 用户数据
const user = ref({
  name: authStore.userInfo?.username,
  email: authStore.userInfo?.email,
  avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
})
// 初始化时获取未读数量
onMounted(async () => {
  if (authStore.isAuthenticated && authStore.isStudent) {
    await noticeStore.fetchUnreadCount()
  }
})

// 监听认证状态变化
watch(() => authStore.isAuthenticated, async (newVal) => {
  if (newVal && authStore.isStudent) {
    await noticeStore.fetchUnreadCount()
  } else {
    noticeStore.unreadCount = 0
  }
})

// 监听角色变化
watch(() => authStore.userInfo?.role, async (newRole) => {
  if (newRole === 'student') {
    await noticeStore.fetchUnreadCount()
  } else {
    noticeStore.unreadCount = 0
  }
})

// 修改点6：监听自定义事件，更新未读数量
onMounted(() => {
  window.addEventListener('update-unread-count', (e: any) => {
    if (authStore.isStudent) {
      noticeStore.unreadCount = e.detail.count
    }
  })
})

</script>

<style scoped>
.user-center {
  position: relative;
  min-height: 100vh;
}

.collapse-btn {
  position: fixed;
  left: 20px;
  top: 20px;
  z-index: 1000;
  cursor: pointer;
  padding: 10px;
  background-color: #b3e0ff;
  border-radius: 50%;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  background: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: width 0.3s;
  z-index: 999;
}

.user-info {
  text-align: center;
  margin-bottom: 30px;
  overflow: hidden;
}

.content {
  transition: margin-left 0.3s;
  padding: 30px;
  background: #f5f7fa;
  min-height: 100vh;
}

/* 调整徽章位置 */
.badge-item :deep(.el-badge__content) {
  top: 10px;
  right: 10px;
}

</style>
