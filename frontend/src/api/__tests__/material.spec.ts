import { describe, it, expect } from 'vitest'
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
