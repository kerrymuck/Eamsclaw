import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Chat',
      component: () => import('@/views/Chat/index.vue'),
      meta: { title: '智能客服' }
    },
    {
      path: '/orders',
      name: 'Orders',
      component: () => import('@/views/Orders/index.vue'),
      meta: { title: '我的订单' }
    },
    {
      path: '/faq',
      name: 'FAQ',
      component: () => import('@/views/FAQ/index.vue'),
      meta: { title: '常见问题' }
    }
  ]
})

router.beforeEach((to) => {
  document.title = to.meta.title as string || '智能客服'
})

export default router
