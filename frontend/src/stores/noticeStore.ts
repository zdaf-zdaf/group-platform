import { defineStore } from 'pinia'
import { ref } from 'vue'
import { NoticeApi } from '@/api/notice'

export const useNoticeStore = defineStore('notice', () => {
  const unreadCount = ref(0)
  const initialized = ref(false)

  // 获取未读公告数量
  const fetchUnreadCount = async () => {
    try {
      const count = await NoticeApi.getUnreadCount()
      unreadCount.value = count
      initialized.value = true
      
      // 触发事件让父组件更新导航栏未读数量
      window.dispatchEvent(new CustomEvent('update-unread-count', {
        detail: { count }
      }));
    } catch (error) {
      console.error('获取未读公告数量失败:', error)
      unreadCount.value = 0
    }
  }

  // 标记所有公告为已读
  const markAllAsRead = async () => {
    try {
      if (unreadCount.value > 0) {
        await NoticeApi.markAllAsRead()
        unreadCount.value = 0
        
        // 触发事件让父组件更新导航栏未读数量
        window.dispatchEvent(new CustomEvent('update-unread-count', {
          detail: { count: 0 }
        }));
      }
    } catch (error) {
      console.error('标记所有公告为已读失败:', error)
      throw error
    }
  }

  return {
    unreadCount,
    initialized,
    fetchUnreadCount,
    markAllAsRead
  }
})