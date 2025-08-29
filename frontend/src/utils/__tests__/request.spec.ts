import { describe, it, expect, vi, beforeEach } from 'vitest'
import service from '../request'
vi.mock('element-plus', () => ({ ElMessage: { error: vi.fn() } }))
// 默认 mock，token 为 undefined，便于 localStorage 测试
vi.mock('@/stores/authStore', () => ({ useAuthStore: () => ({ logout: vi.fn(), token: undefined }) }))

describe('request util', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should inject token in request headers', async () => {
    const token = 'test-token'
    vi.spyOn(window.localStorage.__proto__, 'getItem').mockReturnValue(token)
    const config = { headers: {}, data: {} }
    // @ts-expect-error: 直接访问拦截器类型不匹配，测试用
    const result = await service.interceptors.request.handlers[0].fulfilled(config)
    expect(result.headers['Authorization']).toBe(`Bearer ${token}`)
  })

  it('should handle 401 response', async () => {
    const error = { response: { status: 401 }, message: 'Unauthorized' }
    // mock window.location，避免 jsdom navigation 报错
    const originalLocation = window.location
    // @ts-expect-error: mock location for test
    delete window.location
    // @ts-expect-error: mock location for test
    window.location = { href: '' }
    // @ts-expect-error: 直接访问拦截器类型不匹配，测试用
    await expect(service.interceptors.response.handlers[0].rejected(error)).rejects.toBe(error)
    // 用 defineProperty 恢复 window.location，避免类型报错
    Object.defineProperty(window, 'location', {
      configurable: true,
      enumerable: true,
      writable: true,
      value: originalLocation
    })
  })
})
