<template>
  <div class="orders-page">
    <header class="page-header">
      <button class="back-btn" @click="$router.back()">
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
        </svg>
      </button>
      <h1>我的订单</h1>
    </header>

    <div class="order-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        :class="['tab-btn', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="orders-list">
      <div v-for="order in filteredOrders" :key="order.id" class="order-card">
        <div class="order-header">
          <span class="order-date">{{ order.date }}</span>
          <span :class="['order-status', order.status]">{{ order.statusText }}</span>
        </div>
        
        <div class="order-goods">
          <div v-for="item in order.items" :key="item.id" class="goods-item">
            <img :src="item.image" alt="">
            <div class="goods-info">
              <div class="goods-title">{{ item.title }}</div>
              <div class="goods-spec">{{ item.spec }}</div>
              <div class="goods-price">
                <span class="price">¥{{ item.price }}</span>
                <span class="count">x{{ item.count }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="order-footer">
          <div class="order-total">
            共{{ order.itemCount }}件商品 合计：<span class="total-price">¥{{ order.total }}</span>
          </div>
          <div class="order-actions">
            <button class="action-btn" @click="consult(order)">咨询客服</button>
            <button v-if="order.status === 'pending'" class="action-btn primary">立即付款</button>
            <button v-if="order.status === 'shipped'" class="action-btn primary">确认收货</button>
            <button v-if="order.status === 'delivered'" class="action-btn">申请售后</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="filteredOrders.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" width="64" height="64" style="opacity: 0.3;">
        <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
      </svg>
      <p>暂无订单</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('all')

const tabs = [
  { key: 'all', label: '全部' },
  { key: 'pending', label: '待付款' },
  { key: 'paid', label: '待发货' },
  { key: 'shipped', label: '待收货' },
  { key: 'delivered', label: '已完成' }
]

const orders = ref([
  {
    id: '202403200001',
    date: '2024-03-20 14:30',
    status: 'shipped',
    statusText: '待收货',
    itemCount: 2,
    total: '10998',
    items: [
      {
        id: 1,
        title: 'iPhone 15 Pro Max 256GB 原色钛金属',
        spec: '256GB;原色钛金属',
        price: '9999',
        count: 1,
        image: 'https://via.placeholder.com/80'
      },
      {
        id: 2,
        title: '20W USB-C 电源适配器',
        spec: '白色',
        price: '149',
        count: 1,
        image: 'https://via.placeholder.com/80'
      }
    ]
  },
  {
    id: '202403190002',
    date: '2024-03-19 10:15',
    status: 'delivered',
    statusText: '已完成',
    itemCount: 1,
    total: '1899',
    items: [
      {
        id: 3,
        title: 'AirPods Pro 2 主动降噪无线蓝牙耳机',
        spec: '白色',
        price: '1899',
        count: 1,
        image: 'https://via.placeholder.com/80'
      }
    ]
  },
  {
    id: '202403180003',
    date: '2024-03-18 16:45',
    status: 'pending',
    statusText: '待付款',
    itemCount: 1,
    total: '299',
    items: [
      {
        id: 4,
        title: 'iPhone 15 硅胶保护壳',
        spec: '陶土色',
        price: '299',
        count: 1,
        image: 'https://via.placeholder.com/80'
      }
    ]
  }
])

const filteredOrders = computed(() => {
  if (activeTab.value === 'all') return orders.value
  return orders.value.filter(o => o.status === activeTab.value)
})

const consult = (order: any) => {
  router.push({
    path: '/',
    query: { orderId: order.id }
  })
}
</script>

<style scoped>
.orders-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.page-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  background: none;
  border: none;
  padding: 8px;
  margin-right: 8px;
  cursor: pointer;
  color: #333;
  border-radius: 50%;
  transition: background 0.2s;
}

.back-btn:hover {
  background: #f0f0f0;
}

.page-header h1 {
  font-size: 17px;
  font-weight: 600;
  margin: 0;
}

.order-tabs {
  display: flex;
  background: #fff;
  padding: 0 16px;
  border-bottom: 1px solid #e8e8e8;
  overflow-x: auto;
  scrollbar-width: none;
}

.order-tabs::-webkit-scrollbar {
  display: none;
}

.tab-btn {
  flex: 1;
  min-width: 60px;
  padding: 12px 8px;
  background: none;
  border: none;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  position: relative;
  white-space: nowrap;
}

.tab-btn.active {
  color: #1677ff;
  font-weight: 500;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background: #1677ff;
  border-radius: 1px;
}

.orders-list {
  padding: 12px;
}

.order-card {
  background: #fff;
  border-radius: 12px;
  margin-bottom: 12px;
  overflow: hidden;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.order-date {
  font-size: 13px;
  color: #999;
}

.order-status {
  font-size: 13px;
  font-weight: 500;
}

.order-status.pending { color: #fa8c16; }
.order-status.paid { color: #1890ff; }
.order-status.shipped { color: #52c41a; }
.order-status.delivered { color: #999; }

.order-goods {
  padding: 12px 16px;
}

.goods-item {
  display: flex;
  gap: 12px;
  padding: 8px 0;
}

.goods-item img {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
}

.goods-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.goods-title {
  font-size: 14px;
  color: #333;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.goods-spec {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.goods-price {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.price {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.count {
  font-size: 13px;
  color: #999;
}

.order-footer {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
}

.order-total {
  text-align: right;
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
}

.total-price {
  font-size: 16px;
  font-weight: 600;
  color: #ff4d4f;
}

.order-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.action-btn {
  padding: 6px 14px;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #666;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: #1677ff;
  color: #1677ff;
}

.action-btn.primary {
  background: #1677ff;
  color: #fff;
  border-color: #1677ff;
}

.action-btn.primary:hover {
  background: #4096ff;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #999;
}

.empty-state p {
  margin-top: 16px;
  font-size: 14px;
}

/* 响应式适配 */
@media (min-width: 481px) {
  .orders-page {
    max-width: 480px;
    margin: 0 auto;
    border-left: 1px solid #e8e8e8;
    border-right: 1px solid #e8e8e8;
  }
}

@media (min-width: 769px) {
  .orders-page {
    max-width: 600px;
  }
}
</style>
