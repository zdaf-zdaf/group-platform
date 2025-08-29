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
});
