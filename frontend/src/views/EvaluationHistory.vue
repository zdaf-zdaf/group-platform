<template>
  <div class="evaluation-container">
    <el-table :data="submissionStore.submissions">
      <!-- 实验名称 -->
      <el-table-column prop="setTitle" label="实验名称" />

      <!-- 提交时间 -->
      <el-table-column prop="submittedAt" label="提交时间">
        <template #default="{ row }">
          {{ formatTime(row.submittedAt) }}
        </template>
      </el-table-column>

      <!-- 状态（用布尔字段 passed 显示） -->
      <el-table-column prop="passed" label="状态">
        <template #default="{ row }">
          <el-tag :type="row.passed ? 'success' : 'danger'">
            {{ row.passed ? '已通过' : '未通过' }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { useSubmissionStore } from '@/stores/submissions'
import { onMounted } from 'vue'
import { format } from 'date-fns'

const submissionStore = useSubmissionStore()
onMounted(() => {
  submissionStore.fetchSubmissions()
})

const formatTime = (timestamp: string) => {
  return format(new Date(timestamp), 'yyyy-MM-dd HH:mm')
}
</script>
