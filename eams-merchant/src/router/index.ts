import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login/index.vue'),
      meta: { public: true, title: '商家登录' }
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
          meta: { title: '数据概览' }
        },
        {
          path: 'chat',
          name: 'Chat',
          component: () => import('@/views/Chat/index.vue'),
          meta: { title: '消息中心' }
        },
        {
          path: 'shop',
          name: 'Shop',
          component: () => import('@/views/Shop/index.vue'),
          meta: { title: '店铺管理' }
        },
        {
          path: 'knowledge',
          name: 'Knowledge',
          component: () => import('@/views/Knowledge/index.vue'),
          meta: { title: '知识库' }
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/Settings/index.vue'),
          meta: { title: '系统设置' }
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  document.title = to.meta.title ? `${to.meta.title} - 商家中心` : '商家中心'
  
  if (!to.meta.public && !userStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
