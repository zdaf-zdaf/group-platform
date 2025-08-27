<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div class="forum">
    <!-- 发布问题卡片 -->
    <el-card class="publish-card">
      <h2 style="margin-top: -5px;">发布问题</h2>
      <el-form :model="questionForm" label-width="100px" style="margin-left: -30px;">
        <!-- 问题标题 -->
        <el-form-item label="问题标题">
          <el-input v-model="questionForm.title" placeholder="请输入问题标题" />
        </el-form-item>

        <!-- 问题内容 -->
        <el-form-item label="问题内容">
          <el-input
            v-model="questionForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入问题内容"
          />
        </el-form-item>

        <!-- 发布按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            @click="submitQuestion"
            :loading="isSubmittingQuestion"
          >
            <template v-if="!isSubmittingQuestion">发布问题</template>
            <template v-else>发布中...</template>
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>
    <!-- 展示问题列表 -->
    <el-card
      class="post-card"
      v-for="post in posts"
      :key="post.id"
      :class="{ sticky: post.is_sticky }"
    >
      <template #header>
        <div class="post-header">
          <img :src="post.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'" alt="User Avatar" class="avatar" />
          <span class="username">{{ post.author.username }}</span>
          <span class="post-time">{{ formatDate(post.created_at) }}</span>

          <!-- 管理员操作 -->
          <template v-if="authStore.userInfo?.role === 'teacher'">
            <el-button
              size="small"
              @click="toggleStick(post.id)"
              :loading="post.isTogglingSticky"
            >
              {{ post.is_sticky ? '取消置顶' : '置顶' }}
            </el-button>
          </template>

          <!-- 作者或管理员删除 -->
          <el-button
            size="small"
            @click="deletePost(post.id)"
            :loading="post.isDeleting"
            v-if="isPostOwner(post)"
          >
            删除
          </el-button>
        </div>
      </template>

      <div class="post-content" style="margin-top: -30px;">
        <h3>{{ post.title }}</h3>
        <p>{{ post.content }}</p>
        <div class="post-actions">
          <el-button
            @click="likePost(post.id)"
            :type="post.liked ? 'primary' : 'default'"
            :loading="post.isTogglingLike"
          >
            {{ post.liked ? '取消点赞' : '点赞' }}
          </el-button>
          <span class="likes">{{ post.likes_count }}人点赞</span>
        </div>

        <el-divider></el-divider>
        <h4>评论 ({{ post.comments.length }})</h4>
        <div
          v-for="comment in post.comments"
          :key="comment.id"
          class="comment"
        >
          <div class="comment-header">
            <img :src="comment.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'" alt="User Avatar" class="avatar" />
            <span class="username">{{ comment.author.username }}</span>
            <el-button
              size="small"
              @click="deleteComment(post.id, comment.id)"
              :loading="comment.isDeleting"
              v-if="isCommentOwner(comment)"
            >
              删除评论
            </el-button>
          </div>
          <p>{{ comment.content }}</p>
          <span class="comment-time" style="font-size: 12px;">{{ formatDate(comment.created_at) }}</span>
        </div>

        <el-input
          v-model="newComment[post.id]"
          placeholder="写下你的评论..."
          @keyup.enter="submitComment(post.id)"
          :disabled="!authStore.isAuthenticated"
        />
        <!-- 发布按钮 -->
        <el-form-item style="margin-top: 10px;">
          <el-button
            type="primary"
            @click="submitComment(post.id)"
            :loading="post.isSubmittingComment"
          >
            评论
          </el-button>
        </el-form-item>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/authStore'
import { forumService } from '@/api/auth'
import dayjs from 'dayjs'

const authStore = useAuthStore()
// 发布问题表单数据
const questionForm = reactive({
  title: '',
  content: '',
})
const isSubmittingQuestion = ref(false)
// 假数据 - 帖子
// const posts = ref([
//   {
//     id: 1,
//     username: '小明',
//     avatar: 'https://randomuser.me/api/portraits/men/1.jpg',
//     title: '如何快速提高编程能力？',
//     content: '最近感觉编程进展慢，大家有没有什么快速提高的建议？',
//     time: '2025-05-08 12:30',
//     liked: false,
//     likes: 10,
//     isStuck: false,
//     comments: [
//       {
//         id: 1,
//         username: '小红',
//         avatar: 'https://randomuser.me/api/portraits/women/1.jpg',
//         text: '我觉得可以通过做项目来提高编程能力。',
//       },
//       {
//         id: 2,
//         username: '小刚',
//         avatar: 'https://randomuser.me/api/portraits/men/2.jpg',
//         text: '同意，多做练习，积累经验。',
//       },
//     ],
//   },
// ])
const posts = ref<any[]>([])
const isLoading = ref(true)
// 新评论存储
const newComment = ref<{ [key: number]: string }>({})
// 初始化加载问题
onMounted(() => {
  loadQuestions()
})
// 加载问题
const loadQuestions = async () => {
  try {
    isLoading.value = true
    const response = await forumService.getQuestions()
    // 检查响应数据结构
    console.log('API Response:', response)

    // 确保我们处理的是数组
    const postsData = Array.isArray(response) ? response : response.data || []
    posts.value = postsData.map((post: any) => ({
      ...post,
      isTogglingSticky: false,
      isTogglingLike: false,
      isDeleting: false,
      comments: post.comments.map((comment: any) => ({
        ...comment,
        isDeleting: false,
      }))
    }))
  } catch (error) {
    ElMessage.error('加载问题失败：' + (error as Error).message)
  } finally {
    isLoading.value = false
  }
}
// 格式化日期
const formatDate = (dateString: string) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}
// 检查是否是帖子作者
const isPostOwner = (post: any) => {
  return authStore.userInfo?.username === post.author.username
}
// 检查是否是评论作者
const isCommentOwner = (comment: any) => {
  return authStore.userInfo?.username === comment.author.username
}
// 检查是否是教师
const isTeacher = authStore.userInfo?.role === 'teacher'
// 提交问题
const submitQuestion = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    return
  }
  if (!questionForm.title.trim() || !questionForm.content.trim()) {
    ElMessage.warning('标题和内容不能为空')
    return
  }
  try {
    isSubmittingQuestion.value = true
    const { data: newPost } = await forumService.createQuestion({ // 注意这里解构data
      title: questionForm.title,
      content: questionForm.content,
    })
    // 使用Vue的响应式方法更新数组
    posts.value = [
      {
        ...newPost,
        comments: newPost.comments || [],
        isTogglingSticky: false,
        isTogglingLike: false,
        isDeleting: false,
        isSubmittingComment: false
      },
      ...posts.value // 将新问题放在数组开头
    ]

    questionForm.title = ''
    questionForm.content = ''

    ElMessage.success('问题发布成功')
  } catch (error) {
    ElMessage.error('发布问题失败：' + (error as Error).message)
  } finally {
    isSubmittingQuestion.value = false
  }
}

// 点赞功能
const likePost = async (postId: number) => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    return
  }

  const post = posts.value.find(p => p.id === postId)
  if (!post) return

  try {
    // 保存当前状态用于可能的回滚
    const previousLiked = post.liked
    const previousLikesCount = post.likes_count

    // 乐观更新：立即更新UI
    post.liked = !post.liked
    post.likes_count = post.liked ? previousLikesCount + 1 : previousLikesCount - 1
    post.isTogglingLike = true

    // 调用API
    const { data } = await forumService.toggleLike(postId)

    // 确保状态与API返回一致
    post.liked = data.liked
    post.likes_count = data.likes_count

    // 可选：显示操作反馈
    if (post.liked) {
      ElMessage.success('点赞成功')
    }
  } catch (error) {
    // 出错时回滚状态
    post.liked = !post.liked
    post.likes_count = post.liked ? post.likes_count - 1 : post.likes_count + 1
    console.error('点赞操作失败:', error)
    ElMessage.error('操作失败：' + (error as Error).message)
  } finally {
    post.isTogglingLike = false
  }
}

// 置顶/取消置顶功能
const toggleStick = async (postId: number) => {
  const post = posts.value.find(p => p.id === postId)
  if (!post) return

  try {
    // 立即更新UI状态（乐观更新）
    const wasSticky = post.is_sticky
    post.is_sticky = !wasSticky  // 先切换状态
    post.isTogglingSticky = true

    const { data } = await forumService.toggleSticky(postId)

    // 确保状态与API返回一致（实际更新）
    post.is_sticky = data.is_sticky
    ElMessage.success(post.is_sticky ? '问题已置顶' : '已取消置顶')

    // 自动排序：置顶帖在前
    if (data.is_sticky) {
      posts.value.sort((a, b) =>
        (b.is_sticky - a.is_sticky) ||
        (new Date(b.created_at) - new Date(a.created_at))
      )
    }
  } catch (error) {
    // 操作失败时回滚状态
    post.is_sticky = !post.is_sticky
    console.error('置顶操作失败:', error)
    ElMessage.error('操作失败：' + (error as Error).message)
  } finally {
    post.isTogglingSticky = false
  }
}

// 删除帖子
const deletePost = async (postId: number) => {
  try {
    const post = posts.value.find(p => p.id === postId)
    if (!post) return
    post.isDeleting = true
    await forumService.deleteQuestion(postId)
    posts.value = posts.value.filter(p => p.id !== postId)
    ElMessage.success('问题已删除')
  } catch (error) {
    ElMessage.error('删除失败：' + (error as Error).message)
  }
}

// 提交评论
const submitComment = async (postId: number) => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    return
  }
  const commentText = newComment.value[postId]?.trim()
  if (!commentText) {
    ElMessage.warning('评论内容不能为空')
    return
  }
  try {
    // 设置当前帖子的加载状态
    const post = posts.value.find(p => p.id === postId)
    if (!post) return

    post.isSubmittingComment = true

    const { data: commentData } = await forumService.addComment(postId, commentText)

    // 使用响应式方式更新评论
    post.comments = [
      ...(post.comments || []),
      {
        ...commentData,
        isDeleting: false
      }
    ]

    // 清空输入框
    newComment.value[postId] = ''
    ElMessage.success('评论添加成功')
  } catch (error) {
    console.error('评论失败:', error)
    ElMessage.error('添加评论失败：' + (error as Error).message)
  } finally {
    // 确保重置加载状态
    const post = posts.value.find(p => p.id === postId)
    if (post) post.isSubmittingComment = false
  }
}

// 删除评论
const deleteComment = async (postId: number, commentId: number) => {
  try {
    const comment = posts.value.find(p => p.id === postId)
      ?.comments.find((c: any) => c.id === commentId)
    if (!comment) return
    comment.isDeleting = true
    await forumService.deleteComment(commentId)
    const post = posts.value.find(p => p.id === postId)
    if (post) {
      post.comments = post.comments.filter((c: any) => c.id !== commentId)
      ElMessage.success('评论已删除')
    }
  } catch (error) {
    ElMessage.error('删除评论失败：' + (error as Error).message)
  }
}
</script>

<style scoped>
.forum {
  padding: 20px;
}

.publish-card {
  margin-bottom: 20px;
}

.post-card {
  margin-bottom: 20px;
}

.post-header {
  display: flex;
  align-items: center;
}

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 10px;
}

.username {
  font-weight: bold;
  margin-right: 10px;
}

.post-time {
  font-size: 12px;
  color: #888;
}

.post-header .el-button {
  margin-left: 10px;
}

.post-content {
  padding: 10px 0;
}

.likes {
  margin-left: 10px;
  font-size: 12px;
  color: #888;
}

.comment {
  padding: 10px;
  background: #f9f9f9;
  margin-bottom: 10px;
}

.comment-header {
  display: flex;
  align-items: center;
}

.comment-header .avatar {
  width: 25px;
  height: 25px;
}

.comment-header .username {
  font-weight: bold;
  margin-left: 10px;
}

.el-input {
  margin-top: 10px;
}
</style>
