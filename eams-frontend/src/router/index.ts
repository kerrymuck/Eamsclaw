import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHashHistory(),
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
        // 智能体管理
        {
          path: 'agent/workspace',
          name: 'AgentWorkspace',
          component: () => import('@/views/Agent/Workspace.vue'),
          meta: { title: '工作台管理' }
        },
        {
          path: 'agent/settings',
          name: 'AgentSettings',
          component: () => import('@/views/Agent/Settings.vue'),
          meta: { title: '智能体设置' }
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
          path: 'plan',
          name: 'Plan',
          component: () => import('@/views/Plan/index.vue'),
          meta: { title: '套餐订阅' }
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
      path: '/provider',
      component: () => import('@/views/Provider/Layout.vue'),
      redirect: '/provider/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'ProviderDashboard',
          component: () => import('@/views/Provider/Dashboard.vue'),
          meta: { title: '数据面板' }
        },
        {
          path: 'merchants',
          name: 'ProviderMerchants',
          component: () => import('@/views/Provider/Merchants.vue'),
          meta: { title: '商户管理' }
        },
        {
          path: 'plans',
          name: 'ProviderPlans',
          component: () => import('@/views/Provider/Plans.vue'),
          meta: { title: '套餐管理' }
        },
        {
          path: 'license',
          name: 'ProviderLicense',
          component: () => import('@/views/Provider/License.vue'),
          meta: { title: '授权码管理' }
        },
        {
          path: 'ai-power',
          name: 'ProviderAIPower',
          component: () => import('@/views/Provider/AIPower.vue'),
          meta: { title: 'AI算力管理' }
        },
        {
          path: 'finance',
          name: 'ProviderFinance',
          component: () => import('@/views/Provider/Finance.vue'),
          meta: { title: '财务管理' }
        },
        {
          path: 'account',
          name: 'ProviderAccount',
          component: () => import('@/views/Provider/Account.vue'),
          meta: { title: '账号管理' }
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
