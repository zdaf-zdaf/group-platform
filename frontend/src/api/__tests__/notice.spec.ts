import { describe, it, expect, vi, beforeEach } from 'vitest'
import { NoticeApi, Notice } from '../notice'

// --------------------
// Mock axios with default export
// --------------------
vi.mock('axios', () => {
  const axiosMock = {
    create: vi.fn(() => axiosMock),
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } }
  }
  return {
    default: axiosMock
  }
})

// 导入 mock 之后再断言类型
import axios from 'axios'
const mockedAxios = axios as unknown as {
  create: any
  get: any
  post: any
  put: any
  delete: any
}

// --------------------
// Mock authStore
// --------------------
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    token: 'mock-token',
    isStudent: true,
    userInfo: { username: 'student' },
    logout: vi.fn()
  })
}))

// --------------------
// Tests
// --------------------
describe('NoticeApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getNotices', () => {
    it('正例: 返回公告列表', async () => {
      const notices: Notice[] = [
        { id: 1, title: 'n1', content: 'c1', type: 1, created_at: '2025-08-29', is_top: false, created_by: 1, created_by_name: 'teacher' }
      ]
      mockedAxios.get.mockResolvedValueOnce({ data: notices })

      const res = await NoticeApi.getNotices()
      expect(res).toEqual(notices)
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/notices/', { params: new URLSearchParams() })
    })

    it('反例: 获取失败抛出错误', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('fail'))
      await expect(NoticeApi.getNotices()).rejects.toThrow('获取实验列表失败')
    })
  })

  describe('createNotice', () => {
    it('正例: 创建成功', async () => {
      const notice: Notice = { id: 2, title: 'test', content: 'ok', type: 1, created_at: '2025-08-29', is_top: false, created_by: 1, created_by_name: 'teacher' }
      mockedAxios.post.mockResolvedValueOnce({ data: notice })

      const res = await NoticeApi.createNotice({ title: 'test', content: 'ok', type: 1 })
      expect(res).toEqual(notice)
    })

    it('反例: 创建失败', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('fail'))
      await expect(NoticeApi.createNotice({ title: 'fail', content: 'c', type: 1 })).rejects.toThrow('创建公告失败')
    })
  })

  describe('updateNotice', () => {
    it('正例: 更新成功', async () => {
      const notice: Notice = { id: 1, title: 'updated', content: 'updated', type: 1, created_at: '2025-08-29', is_top: false, created_by: 1, created_by_name: 'teacher' }
      mockedAxios.put.mockResolvedValueOnce({ data: notice })

      const res = await NoticeApi.updateNotice({ id: 1, title: 'updated', content: 'updated', type: 1 })
      expect(res).toEqual(notice)
    })

    it('反例: 更新失败', async () => {
      mockedAxios.put.mockRejectedValueOnce(new Error('fail'))
      await expect(NoticeApi.updateNotice({ id: 999, title: 'fail', content: 'fail', type: 1 })).rejects.toThrow('更新公告失败')
    })
  })

  describe('deleteNotice', () => {
    it('正例: 删除成功', async () => {
      mockedAxios.delete.mockResolvedValueOnce({ data: null })
      await expect(NoticeApi.deleteNotice(1)).resolves.toBeUndefined()
    })

    it('反例: 删除失败', async () => {
      mockedAxios.delete.mockRejectedValueOnce(new Error('fail'))
      await expect(NoticeApi.deleteNotice(999)).rejects.toThrow('删除公告失败')
    })
  })

  describe('getUnreadCount', () => {
    it('正例: 返回未读数', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: { count: 5 } })
      const res = await NoticeApi.getUnreadCount()
      expect(res).toBe(5)
    })

    it('反例: 获取失败返回0', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('fail'))
      await expect(NoticeApi.getUnreadCount()).rejects.toThrow('获取未读公告数量失败')
    })
  })

  describe('markAllAsRead', () => {
    it('正例: 标记全部已读成功', async () => {
      mockedAxios.post.mockResolvedValueOnce({ status: 200, data: {} })
      await expect(NoticeApi.markAllAsRead()).resolves.toEqual({})
    })
    it('反例: 标记全部已读失败', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('fail'))
      await expect(NoticeApi.markAllAsRead()).rejects.toThrow('标记所有公告为已读失败')
    })
  })

  describe('markAsRead', () => {
    it('正例: 标记单个已读成功', async () => {
      mockedAxios.post.mockResolvedValueOnce({ status: 200, data: {} })
      await expect(NoticeApi.markAsRead(1)).resolves.toEqual({})
    })
    it('反例: 标记单个已读失败', async () => {
      mockedAxios.post.mockRejectedValueOnce({ message: 'fail', response: { status: 500, data: { detail: '服务器内部错误' } } })
      await expect(NoticeApi.markAsRead(1)).rejects.toThrow('fail')
    })
  })
})
