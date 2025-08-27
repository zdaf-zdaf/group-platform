import { defineStore } from 'pinia'

interface DiscussionPost {
  id: number
  title: string
  author: string
  createTime: string
  likes: number
  replies: number
  content: string
  isLiked: boolean // 新增字段
}

export const useDiscussionStore = defineStore('discussion', {
  state: () => ({
    posts: [] as DiscussionPost[],
  }),
  actions: {
    // 新增更新方法
    updatePost(id: number, payload: Partial<DiscussionPost>) {
      const index = this.posts.findIndex(post => post.id === id)
      if (index !== -1) {
        this.posts[index] = { ...this.posts[index], ...payload }
      }
    },
    // 修正之前的addPost方法
    addPost(post: Omit<DiscussionPost, 'id' | 'isLiked'>) {
      this.posts.unshift({
        ...post,
        id: Date.now(), // 生成唯一ID
        isLiked: false
      })
    }
  }
})
