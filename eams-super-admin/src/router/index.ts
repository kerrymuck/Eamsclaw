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
          meta: { title: '数据面板' }
        },
        {
          path: 'system',
          name: 'System',
          component: () => import('@/views/System/index.vue'),
          meta: { title: '系统设置' }
        },
        {
          path: 'system/info',
          name: 'SystemInfo',
          component: () => import('@/views/System/Info.vue'),
          meta: { title: '系统信息' }
        },
        {
          path: 'system/params',
          name: 'SystemParams',
          component: () => import('@/views/System/Params.vue'),
          meta: { title: '参数设置' }
        },
        {
          path: 'system/version',
          name: 'SystemVersion',
          component: () => import('@/views/System/Version.vue'),
          meta: { title: '版本说明' }
        },
        {
          path: 'provider',
          name: 'Provider',
          component: () => import('@/views/Provider/index.vue'),
          meta: { title: '服务商管理' }
        },
        {
          path: 'provider/settings',
          name: 'ProviderSettings',
          component: () => import('@/views/Provider/Settings.vue'),
          meta: { title: '服务商设置' }
        },
        {
          path: 'level',
          name: 'Level',
          component: () => import('@/views/Level/index.vue'),
          meta: { title: '级别管理' }
        },
        {
          path: 'level/settings',
          name: 'LevelSettings',
          component: () => import('@/views/Level/Settings.vue'),
          meta: { title: '等级设置' }
        },
        {
          path: 'development',
          name: 'Development',
          component: () => import('@/views/Development/index.vue'),
          meta: { title: '开发管理' }
        },
        {
          path: 'development/platforms',
          name: 'DevPlatforms',
          component: () => import('@/views/Development/Platforms.vue'),
          meta: { title: '平台列表' }
        },
        {
          path: 'development/settings',
          name: 'DevSettings',
          component: () => import('@/views/Development/Settings.vue'),
          meta: { title: '平台设置' }
        },
        {
          path: 'finance',
          name: 'Finance',
          component: () => import('@/views/Finance/index.vue'),
          meta: { title: '财务管理' }
        },
        {
          path: 'finance/transactions',
          name: 'FinanceTransactions',
          component: () => import('@/views/Finance/Transactions.vue'),
          meta: { title: '收支明细' }
        },
        {
          path: 'finance/recharge',
          name: 'FinanceRecharge',
          component: () => import('@/views/Finance/Recharge.vue'),
          meta: { title: '充值明细' }
        },
        {
          path: 'ai',
          name: 'AI',
          component: () => import('@/views/AI/index.vue'),
          meta: { title: 'AI算力中控' }
        },
        {
          path: 'ai/models',
          name: 'AIModels',
          component: () => import('@/views/AI/Models.vue'),
          meta: { title: '大模型管理' }
        },
        {
          path: 'ai/pricing',
          name: 'AIPricing',
          component: () => import('@/views/AI/Pricing.vue'),
          meta: { title: '价格设置' }
        },
        {
          path: 'license',
          name: 'License',
          component: () => import('@/views/License/index.vue'),
          meta: { title: '授权码管理' }
        },
        {
          path: 'license/settings',
          name: 'LicenseSettings',
          component: () => import('@/views/License/Settings.vue'),
          meta: { title: '授权设置' }
        },
        {
          path: 'security',
          name: 'Security',
          component: () => import('@/views/Security/index.vue'),
          meta: { title: '安全管理' }
        },
        {
          path: 'security/anti-crack',
          name: 'SecurityAntiCrack',
          component: () => import('@/views/Security/AntiCrack.vue'),
          meta: { title: '防破解' }
        },
        {
          path: 'security/encryption',
          name: 'SecurityEncryption',
          component: () => import('@/views/Security/Encryption.vue'),
          meta: { title: '加密管理' }
        },
        {
          path: 'security/ecode',
          name: 'SecurityEcode',
          component: () => import('@/views/Security/Ecode.vue'),
          meta: { title: 'Ecode设置' }
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
  
  // 开发模式自动登录
  if (!userStore.token) {
    userStore.setToken('super_admin_dev_token')
    userStore.setUserInfo('超级管理员', 'super_admin')
  }
  
  if (!to.meta.public && !userStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
