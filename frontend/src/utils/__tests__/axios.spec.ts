import { describe, it, expect, vi, beforeEach } from 'vitest'
import instance from '../axios'

describe('axios util', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should inject token in request headers', async () => {
    const token = 'token-axios'
    vi.spyOn(window.localStorage.__proto__, 'getItem').mockReturnValue(token)
    const config = { headers: {} }
    // @ts-expect-error: 直接访问拦截器类型不匹配，测试用
    const result = await instance.interceptors.request.handlers[0].fulfilled(config)
    expect(result.headers.Authorization).toBe(`Bearer ${token}`)
  })

  it('should handle error response', async () => {
    const error = { response: { data: { message: 'fail' } }, message: 'fail' }
  // @ts-expect-error: 直接访问拦截器类型不匹配，测试用
  await expect(instance.interceptors.response.handlers[0].rejected(error)).rejects.toBe('fail')
  })
})
