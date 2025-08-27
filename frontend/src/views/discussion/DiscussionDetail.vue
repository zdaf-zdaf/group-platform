<template>
  <div class="detail-container" v-loading="loading">
    <!-- 主内容区 -->
    <template v-if="currentPost">
      <div class="header">
        <div class="left-info">
          <h1 class="title">{{ currentPost.title }}</h1>
          <div class="meta">
            <span class="author">作者：{{ currentPost.author }}</span>
            <span class="time">发布时间：{{ formatTime(currentPost.createTime) }}</span>
          </div>
        </div>
        <el-button
          :type="currentPost.isLiked ? 'danger' : 'primary'"
          class="like-btn"
          @click="handleLike"
        >
          {{ currentPost.isLiked ? '取消点赞' : '点赞' }} ({{ currentPost.likes }})
        </el-button>
      </div>

      <div class="content">
        {{ currentPost.content }}
      </div>

      <div class="reply-section">
        <el-button type="success" class="reply-btn">
          💬 回复 ({{ currentPost.replies }})
        </el-button>
      </div>
    </template>

    <!-- 帖子不存在提示 -->
    <div v-else class="not-found">
      <el-empty description="帖子不存在或已被删除">
        <el-button type="primary" @click="$router.push('/discussion')">返回列表</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import { useDiscussionStore } from '@/stores/discussion'

const store = useDiscussionStore()
const route = useRoute()
const loading = ref(false)

// 获取当前帖子（带类型断言）
const currentPost = computed(() => {
  const postId = Number(route.params.id)
  return store.posts.find(post => post.id === postId)
})

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 点赞/取消点赞功能
const handleLike = () => {
  if (!currentPost.value) return

  const originalLikes = currentPost.value.likes
  const originalStatus = currentPost.value.isLiked

  try {
    store.updatePost(currentPost.value.id, {
      likes: currentPost.value.isLiked ? originalLikes - 1 : originalLikes + 1,
      isLiked: !currentPost.value.isLiked
    })

    ElMessage.success(currentPost.value.isLiked ? '已取消点赞' : '点赞成功')
  } catch (error) {
    // 回滚状态
    currentPost.value.likes = originalLikes
    currentPost.value.isLiked = originalStatus
    ElMessage.error('操作失败，请重试')
  }
}
</script>

<style scoped lang="scss">
.detail-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);

  .header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid #eee;

    .left-info {
      .title {
        margin: 0 0 12px 0;
        font-size: 24px;
      }

      .meta {
        color: #666;
        font-size: 14px;

        .author {
          margin-right: 16px;
        }

        .time {
          color: #999;
        }
      }
    }

    .like-btn {
      min-width: 120px;
      transition: transform 0.2s;

      &:hover {
        transform: scale(1.05);
      }
    }
  }

  .content {
    line-height: 1.8;
    white-space: pre-wrap;
    margin-bottom: 32px;
  }

  .reply-section {
    text-align: right;
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid #eee;

    .reply-btn {
      padding: 12px 24px;
      font-size: 16px;
    }
  }

  .not-found {
    text-align: center;
    padding: 80px 0;
  }
}
</style>
