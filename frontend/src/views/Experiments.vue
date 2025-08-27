<!-- views/Experiments.vue -->
<template>
  <el-card>
    <template #header>
      <span>我的实验记录</span>
    </template>

    <el-table :data="experiments" style="width: 100%">
      <el-table-column prop="date_begin" label="开始日期" width="180" />
      <el-table-column prop="date_end" label="截止日期" />

      <el-table-column prop="name" label="实验名称">
        <template #default="{ row }">
          <!-- 修改路由路径匹配嵌套路由结构 -->
          <router-link :to="{
            name: 'ExperimentDetail',
            params: { id: row.id }
          }">
            {{ row.name }}
          </router-link>
        </template>
      </el-table-column>

      <el-table-column label="完成状态">
        <template #default="{ row }">
          <el-tag :type="row.is_completed ? 'success' : 'info'" size="small">
            {{ row.is_completed ? '已完成' : '未完成' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="截止状态">
        <template #default="{ row }">
          <el-tag :type="deadlineTagType(row.deadline_status)" size="small">
            {{ row.deadline_status }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const experiments = ref([])

function getDeadlineStatus(startStr: string | null | undefined, deadlineStr: string | null | undefined) {
  if (!startStr || !deadlineStr) return '未知'

  const now = new Date()
  const start = new Date(startStr)
  const deadline = new Date(deadlineStr)

  if (isNaN(start.getTime()) || isNaN(deadline.getTime())) return '未知'

  if (now < start) {
    return '未开始'
  } else if (now >= start && now <= deadline) {
    return '进行中'
  } else {
    return '已截止'
  }
}

// 不同状态对应不同标签颜色
function deadlineTagType(status: string) {
  switch (status) {
    case '未开始': return 'info'
    case '进行中': return 'success'
    case '已截止': return 'danger'
    default: return 'default'
  }
}

const fetchExperiments = async () => {
  try {
    const response = await axios.get('/api/api/experiments/experiments/',{
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      withCredentials: true
    })
    experiments.value = response.data.map(item => ({
      id: item.id,
      date_begin: item.created_at ? item.created_at.slice(0, 10) : '',
      date_end: item.deadline ? item.deadline.slice(0, 10) : '',
      name: item.title,
      is_completed: item.has_submission,
      deadline_status: getDeadlineStatus(item.created_at, item.deadline)
    }))
  } catch (error) {
    console.error('获取实验列表失败', error)
  }
}

onMounted(() => {
  fetchExperiments()
})
</script>
