import { describe, it, expect, vi } from 'vitest';
import { questionSetService } from '@/api/questionSet';

vi.mock('axios', async () => {
  const actual = await vi.importActual<typeof import('axios')>('axios');
  return {
    ...actual,
    default: {
      ...actual.default,
      get: vi.fn((url) => {
        if (url === '/experiments/sets/') {
          return Promise.resolve({ data: [{ id: 1, title: 'set1', deadline: '', students: [], questions: [] }] });
        }
        if (url === '/experiments/sets/1/') {
          return Promise.resolve({ data: { id: 1, title: 'set1', deadline: '', students: [], questions: [] } });
        }
        return Promise.reject(new Error('获取失败'));
      }),
      post: vi.fn(() => Promise.resolve({ data: { id: 2, title: 'set2', deadline: '', students: [], questions: [] } })),
      put: vi.fn(() => Promise.resolve({ data: { id: 1, title: 'set1', deadline: '', students: [], questions: [] } })),
      delete: vi.fn(() => Promise.resolve()),
    }
  };
});

describe('questionSetService', () => {
  it('getAllSets 正例', async () => {
    const res = await questionSetService.getAllSets();
    expect(res[0].title).toBe('set1');
  });
  it('getAllSets 反例', async () => {
    await expect(questionSetService.getSetById(999)).rejects.toThrow();
  });
  it('createSet 正例', async () => {
    const res = await questionSetService.createSet({ title: 'set2', deadline: '', students: [], questions: [] });
    expect(res.title).toBe('set2');
  });

  it('updateSet 正例', async () => {
    const res = await questionSetService.updateSet(1, { title: 'set1' });
    expect(res.title).toBe('set1');
  });
  it('updateSet 反例', async () => {
    // mock put失败
    const axios = await import('axios');
    const oldPut = axios.default.put;
    axios.default.put = () => Promise.reject(new Error('更新失败'));
    await expect(questionSetService.updateSet(999, { title: 'fail' })).rejects.toThrow('更新实验失败');
    axios.default.put = oldPut;
  });

  it('deleteSet 正例', async () => {
    await expect(questionSetService.deleteSet(1)).resolves.toBeUndefined();
  });
  it('deleteSet 反例', async () => {
    // mock delete失败
    const axios = await import('axios');
    const oldDelete = axios.default.delete;
    axios.default.delete = () => Promise.reject(new Error('删除失败'));
    await expect(questionSetService.deleteSet(999)).rejects.toThrow('删除实验失败');
    axios.default.delete = oldDelete;
  });
});
