<template>
  <div class="discussion-container">
    <!-- 头部操作栏 -->
    <div class="operation-bar">
      <el-button
        type="primary"
        icon="el-icon-circle-plus-outline"
        @click="showCreateDialog">
        新建讨论
      </el-button>
    </div>

    <!-- 帖子列表 -->
    <el-table
      :data="filteredPosts"
      style="width: 100%"
      stripe
      v-loading="loading">
      <el-table-column prop="title" label="标题" width="300">
        <template #default="{ row }">
          <router-link
            :to="`/discussion/${row.id}`"
            class="post-title">
            {{ row.title }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column prop="author" label="作者" width="150" />
      <el-table-column prop="createTime" label="发布时间" width="200">
        <template #default="{ row }">
          {{ formatTime(row.createTime) }}
        </template>
      </el-table-column>
      <el-table-column prop="likes" label="点赞数" width="100" align="center" />
      <el-table-column prop="replies" label="回复数" width="100" align="center" />
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="totalPosts"
        :page-size="pageSize"
        v-model:current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 新建帖子弹窗 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建新讨论"
      width="600px">
      <el-form
        ref="postForm"
        :model="newPost"
        :rules="formRules"
        label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="newPost.title" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="newPost.content"
            type="textarea"
            :rows="4"
            placeholder="请输入讨论内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreatePost">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import dayjs from 'dayjs'
import { useDiscussionStore } from '@/stores/discussion'
const store = useDiscussionStore()
const mockPosts = computed(() => store.posts)
// 临时模拟数据
interface DiscussionPost {
  id: number
  title: string
  author: string
  createTime: string
  likes: number
  replies: number
  content: string
}

// 组件逻辑
const loading = ref(false)
const currentPage = ref(1)
const pageSize = 10
const totalPosts = computed(() => mockPosts.value.length)
const createDialogVisible = ref(false)
const postForm = ref<FormInstance>()

const newPost = reactive({
  title: '',
  content: ''
})

const formRules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 5, max: 50, message: '长度在5到50个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入讨论内容', trigger: 'blur' },
    { min: 10, message: '内容至少10个字符', trigger: 'blur' }
  ]
}

const filteredPosts = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return mockPosts.value.slice(start, start + pageSize)
})

const formatTime = (time: string) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

const showCreateDialog = () => {
  createDialogVisible.value = true
}

const handleCreatePost = async () => {
  const valid = await postForm.value?.validate()
  if (!valid) return


  store.addPost({
    title: newPost.title,
    content: newPost.content,
    author: '当前用户', // 这里可以替换为实际的用户信息
    createTime: new Date().toISOString(),
    likes: 0,
    replies: 0
  })
  currentPage.value = 1
  ElMessage.success('讨论创建成功')
  createDialogVisible.value = false
  postForm.value?.resetFields()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}
</script>

<style scoped>
.discussion-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.operation-bar {
  margin-bottom: 20px;
}

.post-title {
  color: var(--el-color-primary);
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
