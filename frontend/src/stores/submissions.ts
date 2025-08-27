// stores/submissions.ts
import { defineStore } from 'pinia'
import axios from 'axios'
import { ref } from 'vue'

interface Submission {
  id: number
  studentId: number
  studentName: string
  setId: number
  setTitle: string
  deadline: string
  submittedAt: string
  passed: boolean
  answers: any[]
}

export const useSubmissionStore = defineStore('submissions', () => {
  const submissions = ref<Submission[]>([])

  // 从后端加载提交记录
  const fetchSubmissions = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/experiments/submissions/')
      submissions.value = res.data
    } catch (err) {
      console.error('获取提交记录失败', err)
    }
  }

  return { submissions, fetchSubmissions }
})
