<template>
  <div class="manage-submissions">
    <div class="filters">
      <el-select v-model="selectedSet" placeholder="选择题组" style="width: 200px" clearable>
        <el-option v-for="set in sets" :key="set.id" :label="set.title" :value="set.id" />
      </el-select>

      <el-input
        v-model="searchKeyword"
        placeholder="搜索学生姓名"
        style="width: 200px; margin-left: 16px"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <template v-if="filteredSubmissions.length > 0">
      <el-row :gutter="16" style="margin-top: 20px">
        <el-col :span="6" v-for="submission in filteredSubmissions" :key="submission.id">
          <el-card class="submission-card" @click="goToDetail(submission)">
            <div>
              <p><strong>学生：</strong>{{ submission.studentName }}</p>
              <p><strong>题组：</strong>{{ submission.setTitle }}</p>
              <p><strong>提交时间：</strong>{{ submission.submittedAt }}</p>
              <p><strong>截止时间：</strong>{{ submission.deadline }}</p>
              <p>
                <strong>状态：</strong>
                <el-tag :type="getStatusTagType(submission)">
                  {{ getStatusText(submission) }}
                </el-tag>
              </p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </template>
    <el-empty
      v-else
      description="暂无符合条件的提交记录"
      style="margin-top: 40px"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Search } from '@element-plus/icons-vue'

// 路由跳转
const router = useRouter()

// 判断是否已批改：只要 passed 字段不是 null/undefined 就算已批改
const isReviewed = (submission: { passed: boolean | null; deadline: string }) => {
  return submission.passed !== null && submission.passed !== undefined
}

// 状态判断：已批改/已截止/未批改
const getStatusTagType = (submission: { passed: boolean | null; deadline: string }) => {
  if (isReviewed(submission)) return 'success'       // 已批改，显示绿色标签
  if (new Date(submission.deadline) < new Date()) return 'danger' // 已截止，显示红色标签
  return 'warning'                                   // 未批改，显示黄色标签
}

const getStatusText = (submission: { passed: boolean | null; deadline: string }) => {
  if (isReviewed(submission)) return '已批改'
  if (new Date(submission.deadline) < new Date()) return '已截止'
  return '未批改'
}

const sets = ref<any[]>([])

const fetchSets = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/experiments/experiments/', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
    sets.value = response.data
  } catch (error) {
    console.error('获取题组失败', error)
  }
}
// 所有提交记录
const allSubmissions = ref<any[]>([])

// 当前筛选条件
const selectedSet = ref('')
const searchKeyword = ref('')

// 获取后端提交数据
const fetchSubmissions = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/experiments/submissions/', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
    allSubmissions.value = response.data
  } catch (error) {
    console.error('获取提交记录失败', error)
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchSets()
  fetchSubmissions()
})

// 根据题组/关键字进行筛选
const filteredSubmissions = computed(() => {
  return allSubmissions.value.filter((s) => {
    const matchSet = !selectedSet.value || s.setId === Number(selectedSet.value)
    const matchSearch = !searchKeyword.value || s.studentName.includes(searchKeyword.value)
    return matchSet && matchSearch
  })
})

// 跳转详情页
const goToDetail = (submission: any) => {
  router.push({
    name: 'ViewSubmissionDetail',
    query: {
      studentId: submission.studentId,
      setId: submission.setId,
      submissionId: submission.id
    }
  })
}
</script>


<style scoped lang="scss">
.manage-submissions {
  padding: 20px;

  .filters {
    display: flex;
    align-items: center;
  }

  .submission-card {
    margin-bottom: 20px;
    cursor: pointer;
    transition: transform 0.2s;

    &:hover {
      transform: scale(1.02);
    }
  }
}
</style>
