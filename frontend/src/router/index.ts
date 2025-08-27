import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/authStore' // 导入认证存储
const routes: Array<RouteRecordRaw> = [
  // 根路径重定向
  {
    path: '/',
    redirect: (to) => {
      const authStore = useAuthStore()
      if (authStore.isAuthenticated) {
        return '/profile'
      }
      return '/login'
    }
  },
  // 主布局路由（处理所有需要侧边栏的页面）
  {
    path: '/',
    component: () => import('@/views/index.vue'), // 主布局组件
    meta: {
      requiresAuth: true, // 需要认证
    },
    children: [
      // 通知公告
      {
        path: 'notices',
        name: 'NoticeBoard',
        component: () => import('@/views/NoticeBoard.vue'),
        meta: {
          title: '通知公告',
          icon: 'BellFilled',
          requiresAuth: true,
        },
      },

      // 查看学习资料
      {
        path: 'studyfile',
        name: 'StudyFile',
        component: () => import('@/views/StudyFile.vue'),
      },

      // 实验列表
      {
        path: 'experiments',
        name: 'Experiments',
        component: () => import('@/views/Experiments.vue'),
        meta: {
          studentOnly: true, // 仅学生可见
        }
      },

      // 评测记录
      {
        path: 'evaluation-history',
        name: 'EvaluationHistory',
        component: () => import('@/views/EvaluationHistory.vue'),
        meta: {
          studentOnly: true,
        },
      },

      // 个人信息
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/PersonalInfo.vue'),
      },

      // 实验详情模块（修正为正确嵌套结构）
      {
        path: 'experiment/:id',
        component: () => import('@/views/Experiment/ExperimentLayout.vue'),
        children: [
          {
            path: '',
            name: 'ExperimentDetail',
            component: () => import('@/views/Experiment/ExperimentDetail.vue'),
          },
          {
            path: 'coding/:questionId',
            name: 'CodingTask',
            component: () => import('@/views/Experiment/CodingEditor.vue'),
          },
        ],
      },

      // 讨论区
      {
        path: 'discussion',
        name: 'Discussion',
        component: () => import('@/views/discussion/DiscussionIndex.vue'),
      },
      // 讨论详情
      {
        path: 'discussion/:id',
        name: 'DiscussionDetail',
        component: () => import('@/views/discussion/DiscussionDetail.vue'),
      },
      //创建题目
      {
        path: '/teacher-create',
        name: 'PublishExperiment',
        component: () => import('@/views/Teacher/PublishExperiment.vue'),
        meta: {
          teacherOnly: true, // 仅教师可见
        }
      },
      //查看学生提交
      {
        path: '/teacher-review',
        name: 'ManageSubmissions',
        component: () => import('@/views/Teacher/ManageSubmissions.vue'),
        meta: {
          teacherOnly: true, // 仅教师可见
        }
      },
      //查看学生提交详情
      {
        path: '/teacher/submission-detail',
        name: 'ViewSubmissionDetail',
        component: () => import('@/views/Teacher/ViewSubmissionDetail.vue'),
        meta: {
          teacherOnly: true, // 仅教师可见
        }
      },
      // 论坛
      {
        path: 'forum',
        name: 'Forum',
        component: () => import('@/views/Forum.vue'),
      },
    ],
  },
  // 登录页面
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { public: true }, // 公开访问
  },
  // 注册页面
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { public: true }, // 公开访问
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 全局路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 1. 检查是否为公共页面
  if (to.meta.public) {
    return next()
  }

  // 2. 检查用户认证状态
  const isAuthenticated = authStore.isAuthenticated

  // 3. 需要认证但未登录：重定向到登录页
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({
      path: '/login',
      query: { redirect: to.fullPath } // 保存目标路径用于登录后重定向
    })
  }

  // 4. 已登录用户访问登录/注册页：重定向到首页
  if (isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
    // 根据角色重定向
    const homePath = authStore.isStudent ? '/experiments' : '/teacher-review'
    return next(homePath)
  }

  // 5. 检查角色权限
  if (to.meta.studentOnly && !authStore.isStudent) {
    // 教师试图访问学生专属页面
    return next('/teacher-review') // 重定向到教师主页
  }

  if (to.meta.teacherOnly && authStore.isStudent) {
    // 学生试图访问教师专属页面
    return next('/experiments') // 重定向到学生主页
  }

  next()
})

export default router
