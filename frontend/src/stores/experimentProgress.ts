import { defineStore } from 'pinia'

interface Progress {
  answers: {
    choice: { [key: number]: string }
    fill: { [key: number]: string }
    coding: { [key: number]: string }
  }
  lastSaved: string
}

interface CodingProgress {
  code: string
  timestamp: string
}

interface ExperimentProgress {
  [key: number]: Progress
}

interface CodingState {
  [key: number]: {
    [key: number]: CodingProgress
  }
}

export const useExperimentProgressStore = defineStore('experimentProgress', {
  state: () => ({
    progress: {} as ExperimentProgress,
    codingProgress: {} as CodingState
  }),

  actions: {
    // 保存实验整体进度
    saveProgress(experimentId: number, answers: Progress['answers']) {
      this.progress[experimentId] = {
        answers,
        lastSaved: new Date().toISOString()
      }
      // 保存到 localStorage
      localStorage.setItem('experimentProgress', JSON.stringify(this.progress))
    },

    // 加载实验整体进度
    loadProgress(experimentId: number): Progress | null {
      // 从 localStorage 加载
      const savedProgress = localStorage.getItem('experimentProgress')
      if (savedProgress) {
        this.progress = JSON.parse(savedProgress)
      }
      return this.progress[experimentId] || null
    },

    // 清除实验进度
    clearProgress(experimentId: number) {
      delete this.progress[experimentId]
      localStorage.setItem('experimentProgress', JSON.stringify(this.progress))
    },

    // 保存编程题进度
    saveCodingProgress(experimentId: number, questionId: number, data: CodingProgress) {
      if (!this.codingProgress[experimentId]) {
        this.codingProgress[experimentId] = {}
      }
      this.codingProgress[experimentId][questionId] = data
      localStorage.setItem('codingProgress', JSON.stringify(this.codingProgress))
    },

    // 加载编程题进度
    loadCodingProgress(experimentId: number, questionId: number): CodingProgress | null {
      const savedProgress = localStorage.getItem('codingProgress')
      if (savedProgress) {
        this.codingProgress = JSON.parse(savedProgress)
      }
      return this.codingProgress[experimentId]?.[questionId] || null
    },

    // 清除编程题进度
    clearCodingProgress(experimentId: number, questionId: number) {
      if (this.codingProgress[experimentId]) {
        delete this.codingProgress[experimentId][questionId]
        localStorage.setItem('codingProgress', JSON.stringify(this.codingProgress))
      }
    }
  },

  persist: true
})
