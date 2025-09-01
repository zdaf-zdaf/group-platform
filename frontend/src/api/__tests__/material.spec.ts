import { describe, it, expect, beforeEach } from 'vitest'
import { addMaterial, removeMaterial, updateMaterial, getMaterial } from '@/utils/materialUtils'

// 模拟材料数据
const sampleMaterial = { id: 1, name: 'Steel', quantity: 10 }
const anotherMaterial = { id: 2, name: 'Wood', quantity: 5 }

describe('Material Functions', () => {
  // ===============================
  // addMaterial
  // ===============================
  describe('addMaterial', () => {
    it('应该成功添加新材料', () => {
      const store: any[] = []
  addMaterial(store, sampleMaterial)
      expect(store).toContainEqual(sampleMaterial)
    })

    it('添加重复 ID 的材料时应抛出错误', () => {
      const store = [sampleMaterial]
      expect(() => addMaterial(store, sampleMaterial)).toThrowError(/already exists/i)
    })
  })

  // ===============================
  // removeMaterial
  // ===============================
  describe('removeMaterial', () => {
    it('应该成功移除已存在的材料', () => {
      const store = [sampleMaterial, anotherMaterial]
      removeMaterial(store, 1)
      expect(store).not.toContainEqual(sampleMaterial)
      expect(store).toContainEqual(anotherMaterial)
    })

    it('尝试移除不存在的材料时应抛出错误', () => {
      const store = [anotherMaterial]
      expect(() => removeMaterial(store, 999)).toThrowError(/not found/i)
    })
  })

  // ===============================
  // updateMaterial
  // ===============================
  describe('updateMaterial', () => {
    it('应该成功更新材料信息', () => {
      const store = [sampleMaterial]
      updateMaterial(store, 1, { quantity: 20 })
      expect(store[0].quantity).toBe(20)
    })

    it('尝试更新不存在的材料时应抛出错误', () => {
      const store = [anotherMaterial]
      expect(() => updateMaterial(store, 999, { name: 'Updated' }))
        .toThrowError(/not found/i)
    })
  })

  // ===============================
  // getMaterial
  // ===============================
  describe('getMaterial', () => {
    it('应该正确返回已存在的材料', () => {
      const store = [sampleMaterial, anotherMaterial]
      const material = getMaterial(store, 2)
      expect(material).toEqual(anotherMaterial)
    })

    it('尝试获取不存在的材料时应返回 null', () => {
      const store = [sampleMaterial]
      const material = getMaterial(store, 999)
      expect(material).toBeNull()
    })
  })
})

// ===============================
// MaterialApi 接口函数单元测试
// ===============================
import { MaterialApi } from '../material'
import { vi } from 'vitest'

vi.mock('axios', () => {
  const axiosMock = {
    create: vi.fn(() => axiosMock),
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } }
  }
  return { default: axiosMock }
})
import axios from 'axios'
const mockedAxios = axios as unknown as {
  create: any
  get: any
  post: any
  put: any
  delete: any
}

describe('MaterialApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getMaterials', () => {
    it('正例: 获取材料列表', async () => {
      const data = [{ id: 1, title: 't', description: '', type: 'pdf', size: 1, downloads: 0, created_at: '', file: '', file_url: '', created_by: 1 }]
      mockedAxios.get.mockResolvedValueOnce({ data })
      const res = await MaterialApi.getMaterials()
      expect(res).toEqual(data)
    })
    it('反例: 获取失败', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('fail'))
      await expect(MaterialApi.getMaterials()).rejects.toThrow()
    })
  })

  describe('createMaterial', () => {
    it('正例: 创建成功', async () => {
      const material = { id: 1, title: 't', description: '', type: 'pdf', size: 1, downloads: 0, created_at: '', file: '', file_url: '', created_by: 1 }
      mockedAxios.post.mockResolvedValueOnce({ data: material })
      const formData = new FormData()
      const res = await MaterialApi.createMaterial(formData)
      expect(res).toEqual(material)
    })
    it('反例: 创建失败', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('fail'))
      await expect(MaterialApi.createMaterial(new FormData())).rejects.toThrow()
    })
  })

  describe('updateMaterial', () => {
    it('正例: 更新成功', async () => {
      const material = { id: 1, title: 't', description: '', type: 'pdf', size: 1, downloads: 0, created_at: '', file: '', file_url: '', created_by: 1 }
      mockedAxios.put.mockResolvedValueOnce({ data: material })
      const formData = new FormData()
      const res = await MaterialApi.updateMaterial(1, formData)
      expect(res).toEqual(material)
    })
    it('反例: 更新失败', async () => {
      mockedAxios.put.mockRejectedValueOnce(new Error('fail'))
      await expect(MaterialApi.updateMaterial(1, new FormData())).rejects.toThrow()
    })
  })

  describe('deleteMaterial', () => {
    it('正例: 删除成功', async () => {
      mockedAxios.delete.mockResolvedValueOnce({})
      await expect(MaterialApi.deleteMaterial(1)).resolves.toBeUndefined()
    })
    it('反例: 删除失败', async () => {
      mockedAxios.delete.mockRejectedValueOnce(new Error('fail'))
      await expect(MaterialApi.deleteMaterial(1)).rejects.toThrow()
    })
  })

  describe('downloadMaterial', () => {
    it('正例: 下载成功', async () => {
      const blob = new Blob(['test'])
      mockedAxios.get.mockResolvedValueOnce({ data: blob })
      const res = await MaterialApi.downloadMaterial(1)
      expect(res).toBe(blob)
    })
    it('反例: 下载失败', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('fail'))
      await expect(MaterialApi.downloadMaterial(1)).rejects.toThrow()
    })
  })
})
