import { describe, it, expect, vi } from 'vitest'
import { authService } from '@/api/auth'

// mock axios (带 interceptors)
vi.mock('axios', async () => {
  const actual = await vi.importActual<typeof import('axios')>('axios')
  return {
    ...actual,
    default: {
      ...actual.default,
      create: () => {
        const mockInstance: any = {
          post: vi.fn((url, data) => {
            if (
              url === '/auth/login/' &&
              data.username === 'user' &&
              data.password === 'pass'
            ) {
              return Promise.resolve({
                data: {
                  access: 'token',
                  refresh: 'refresh',
                  username: 'user',
                  role: 'student',
                  email: 'user@example.com',
                },
              })
            }
            return Promise.reject({
              response: { data: { message: '登录失败' } },
            })
          }),
          get: vi.fn(() =>
            Promise.resolve({ data: { username: 'user', role: 'student' } }),
          ),
          patch: vi.fn(() => Promise.resolve()),
          // ✅ 补齐 interceptors
          interceptors: {
            request: { use: vi.fn() },
            response: { use: vi.fn() },
          },
        }
        return mockInstance
      },
    },
  }
})

describe('authService', () => {
  it('login 正例: 正确用户名密码', async () => {
    const res = await authService.login({
      username: 'user',
      password: 'pass',
      rememberMe: false,
    })
    expect(res.username).toBe('user')
    expect(res.role).toBe('student')
  })

  it('login 反例: 错误用户名密码', async () => {
    await expect(
      authService.login({ username: 'bad', password: 'bad', rememberMe: false }),
    ).rejects.toThrow('登录失败')
  })

  it('getUserInfo 正例', async () => {
    const res = await authService.getUserInfo('token')
    expect(res.username).toBe('user')
  })
})
