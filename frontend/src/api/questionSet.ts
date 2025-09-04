import axios from 'axios'

// 创建 Axios 实例
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/',
  headers: {
    'X-Requested-With': 'XMLHttpRequest'
  }
});

// 请求拦截器 - 自动注入 token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface QuestionSet {
  id?: number
  title: string
  deadline: string
  teacher?: number
  students: number[]
  questions: Question[]
}

export interface Question {
  id?: number
  type: string
  prompt: string
  correct_answer?: string
  score: number
  order: number
  testcases: TestCase[]
}

export interface TestCase {
  input: string
  output: string
}

export const questionSetService = {
  // 获取所有实验
  async getAllSets(): Promise<QuestionSet[]> {
    try {
  const response = await axios.get('/api/experiments/experiments/')
      return response.data
    } catch (error) {
      throw new Error('获取实验列表失败')
    }
  },

  // 获取单个实验详情
  async getSetById(id: number): Promise<QuestionSet> {
    try {
  const response = await axios.get(`/api/experiments/experiments/${id}/`)
      return response.data
    } catch (error) {
      throw new Error('获取实验详情失败')
    }
  },

  // 创建实验
  async createSet(setData: Omit<QuestionSet, 'id'>): Promise<QuestionSet> {
    try {
      const response = await axios.post('/api/experiments/experiments/', setData)
      return response.data
    } catch (error) {
      throw new Error('创建实验失败')
    }
  },

  // 更新实验
  async updateSet(id: number, setData: Partial<QuestionSet>): Promise<QuestionSet> {
    try {
      const response = await axios.put(`/api/experiments/experiments/${id}/`, setData)
      return response.data
    } catch (error) {
      throw new Error('更新实验失败')
    }
  },

  // 删除实验
  async deleteSet(id: number): Promise<void> {
    try {
      await axios.delete(`/api/experiments/experiments/${id}/`)
    } catch (error) {
      throw new Error('删除实验失败')
    }
  }
}
