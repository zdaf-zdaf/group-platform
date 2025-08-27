<template>
  <div class="submission-detail">
    <el-card class="student-info">
      <div>
        <strong>学生：</strong>{{ submission.studentName }}（学号：{{ submission.studentId }}）
      </div>
      <div><strong>提交时间：</strong>{{ submission.submittedAt }}</div>
    </el-card>

    <el-divider>题目详情</el-divider>

    <el-card v-for="(q, index) in submission.questions" :key="q.id" class="question-card">
      <template #header>
        <div class="q-header">
          <span>题目 {{ index + 1 }}（{{ q.type }}）</span>
          <el-switch v-model="q.passed" active-text="通过" inactive-text="未通过" />
        </div>
      </template>

      <div class="q-content">
        <p><strong>题干：</strong>{{ q.prompt }}</p>

        <!-- 选择题 / 填空题展示作答与标准答案 -->
        <template v-if="q.type !== '编程题'">
          <p><strong>学生答案：</strong>{{ q.answer }}</p>
          <p><strong>标准答案：</strong>{{ q.correctAnswer }}</p>
        </template>

        <!-- 编程题 -->
        <template v-else>
          <p><strong>学生提交代码：</strong></p>
          <el-input type="textarea" :rows="8" v-model="q.code" readonly />
          <el-button type="primary" plain icon="el-icon-download" @click="downloadCode(q)"
            >下载代码</el-button
          >

          <p style="margin-top: 10px"><strong>测试点结果：</strong></p>
          <el-table :data="q.test_cases" border stripe style="width: 100%">
            <el-table-column prop="input" label="输入" />
            <el-table-column prop="expected" label="期望输出" />
            <el-table-column prop="actual" label="学生输出" />
            <el-table-column
              prop="pass"
              label="是否通过"
              :formatter="(row) => (row.pass ? '✔️' : '❌')"
            />
          </el-table>
        </template>
      </div>
    </el-card>

    <el-button type="success" style="margin-top: 20px" @click="saveReview">保存批改结果</el-button>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
// 引入 axios 或其他请求库
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'


// 获取路由中的参数
const route = useRoute()
const studentId = (route.query.studentId as string)
const setId = (route.query.setId as string)
const submissionId = route.query.submissionId as string;

// 存储提交数据
const submission = ref<any>({
  studentId,
  setId,
  studentName: '',
  submittedAt: '',
  passed: false,
  answers: [],  // 后端返回的答案列表
  questions: [], // 组装后供页面展示的题目数组
})

// 根据后端返回的 answers 组装前端展示用的 questions
const processAnswers = (answers: any[]) => {
  return answers.map(ans => {
    const type = ans.question_type_display || '未知题型'

    return {
      id: ans.id,
      type,
      prompt: ans.prompt || '无题干',
      answer: ans.student_answer || ans.answer_text || '',
      correctAnswer: ans.correct_answer || '无标准答案',
      code: ans.code || '',
      passed: ans.is_passed,
      test_cases: (ans.test_results || []).map(tr => ({
        input: tr.test_case_input || '无输入',
        expected: tr.expected_output || '无期望',
        actual: tr.actual_output || '',
        pass: tr.is_passed,
      })),
    }
  })
}


// 从后端接口获取数据
const getSubmissionData = async (submissionId: string) => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/experiments/submissions/${submissionId}/`);

    const data = response.data
    submission.value = data
    submission.value.questions = processAnswers(data.answers || [])
  } catch (error) {
    console.error('获取提交详情失败:', error)
    ElMessage.error('加载提交详情失败，请检查网络或后端接口。')
  }
}


// 在页面加载时调用获取数据的方法
onMounted(async () => {
  await getSubmissionData(submissionId)
})

const downloadCode = (q: { code: string; id: number }) => {
  if (!q.code) {
    ElMessage.warning('无代码可下载')
    return
  }
  const blob = new Blob([q.code], { type: 'text/plain;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `题目${q.id}_代码.py`
  a.click()
  URL.revokeObjectURL(a.href)
}

const saveReview = async () => {
  try {
    const answersToReview = submission.value.questions.map((q: any) => ({
      id: q.id,
      is_passed: q.passed,
    }))

    console.log('准备保存的批改数据:', answersToReview) // 调试用

    const response = await axios.patch(
      `http://127.0.0.1:8000/api/experiments/submissions/${submissionId}/review_answers/`,
      { answers: answersToReview }
    )

    ElMessage.success(response.data.message || '保存批改结果成功！')

    // 保存后刷新数据，确保页面显示最新状态
    await getSubmissionData(submissionId)
  } catch (error: any) {
    console.error('保存批改结果失败', error)
    ElMessage.error(
      error.response?.data?.error ||
      error.response?.data?.message ||
      '保存批改结果失败，请重试'
    )
  }
}


</script>

<style scoped lang="scss">
.submission-detail {
  padding: 20px;

  .student-info {
    margin-bottom: 20px;
  }

  .question-card {
    margin-bottom: 20px;
  }

  .q-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .q-content {
    padding-top: 10px;
    font-size: 14px;
  }
}
</style>
