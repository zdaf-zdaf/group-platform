import { describe, it, expect, vi } from 'vitest'
import { authService } from '@/api/auth'
import { apiClient } from '@/api/auth'

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

  it('register 正例: 注册成功', async () => {
    const spy = vi.spyOn(apiClient, 'post').mockResolvedValueOnce({});
    await expect(authService.register({ username: 'u', password: 'p', email: 'e', role: 'student' })).resolves.toBeUndefined();
    spy.mockRestore();
  });

  it('register 反例: 注册失败', async () => {
    const error = Object.assign(new Error('注册失败'), { response: { data: { message: '注册失败' } }, isAxiosError: true });
    const spy = vi.spyOn(apiClient, 'post').mockRejectedValueOnce(error);
    await expect(authService.register({ username: 'u', password: 'p', email: 'e', role: 'student' })).rejects.toThrow('注册失败');
    spy.mockRestore();
  });

  it('updateUserProfile 正例: 更新成功', async () => {
    const spy = vi.spyOn(apiClient, 'patch').mockResolvedValueOnce({});
    await expect(authService.updateUserProfile({ student_id: '1' })).resolves.toBeUndefined();
    spy.mockRestore();
  });

  it('updateUserProfile 反例: 更新失败', async () => {
    const error = Object.assign(new Error('更新失败'), { response: { data: { message: '更新失败' } }, isAxiosError: true });
    const spy = vi.spyOn(apiClient, 'patch').mockRejectedValueOnce(error);
    await expect(authService.updateUserProfile({ student_id: '1' })).rejects.toThrow('更新失败');
    spy.mockRestore();
  });
})
