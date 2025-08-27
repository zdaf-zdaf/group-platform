import axios from 'axios'

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
      const response = await axios.get('/experiments/sets/')
      return response.data
    } catch (error) {
      throw new Error('获取实验列表失败')
    }
  },

  // 获取单个实验详情
  async getSetById(id: number): Promise<QuestionSet> {
    try {
      const response = await axios.get(`/experiments/sets/${id}/`)
      return response.data
    } catch (error) {
      throw new Error('获取实验详情失败')
    }
  },

  // 创建实验
  async createSet(setData: Omit<QuestionSet, 'id'>): Promise<QuestionSet> {
    try {
      const response = await axios.post('/experiments/sets/', setData)
      return response.data
    } catch (error) {
      throw new Error('创建实验失败')
    }
  },

  // 更新实验
  async updateSet(id: number, setData: Partial<QuestionSet>): Promise<QuestionSet> {
    try {
      const response = await axios.put(`/experiments/sets/${id}/`, setData)
      return response.data
    } catch (error) {
      throw new Error('更新实验失败')
    }
  },

  // 删除实验
  async deleteSet(id: number): Promise<void> {
    try {
      await axios.delete(`/experiments/sets/${id}/`)
    } catch (error) {
      throw new Error('删除实验失败')
    }
  }
}
