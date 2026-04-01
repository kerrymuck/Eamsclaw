import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login/index.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      name: 'Layout',
      component: () => import('@/components/Layout/index.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard/index.vue'),
          meta: { title: '仪表盘' }
        },
        {
          path: 'inbox',
          name: 'UnifiedInbox',
          component: () => import('@/views/UnifiedInbox/index.vue'),
          meta: { title: '消息中心' }
        },
        {
          path: 'knowledge',
          name: 'Knowledge',
          component: () => import('@/views/Knowledge/index.vue'),
          meta: { title: '知识库' }
        },
        {
          path: 'tickets',
          name: 'Tickets',
          component: () => import('@/views/Tickets/index.vue'),
          meta: { title: '工单流转' }
        },
        {
          path: 'performance',
          name: 'Performance',
          component: () => import('@/views/Performance/index.vue'),
          meta: { title: '绩效管理' }
        },
        {
          path: 'shops',
          name: 'Shops',
          component: () => import('@/views/Shops/index.vue'),
          meta: { title: '店铺管理' }
        },
        {
          path: 'orders',
          name: 'Orders',
          component: () => import('@/views/Orders/index.vue'),
          meta: { title: '订单管理' }
        },
        {
          path: 'ai-power',
          name: 'AIPower',
          component: () => import('@/views/AIPower/index.vue'),
          meta: { title: 'AI算力中心' }
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/Settings/index.vue'),
          meta: { title: '设置' }
        },
        {
          path: 'settings/:pathMatch(.*)*',
          redirect: '/settings'
        },
        {
          path: 'shops/:pathMatch(.*)*',
          redirect: '/shops'
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 开发模式：如果没有token，自动模拟登录
  if (!userStore.token) {
    userStore.token = 'dev_token_' + Date.now()
    userStore.username = 'admin'
    userStore.role = 'admin'
    localStorage.setItem('token', userStore.token)
    localStorage.setItem('username', 'admin')
    localStorage.setItem('role', 'admin')
  }
  
  if (!to.meta.public && !userStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
