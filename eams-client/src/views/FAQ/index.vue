<template>
  <div class="faq-page">
    <header class="page-header">
      <button class="back-btn" @click="$router.back()">
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
        </svg>
      </button>
      <h1>常见问题</h1>
    </header>

    <div class="search-box">
      <svg class="search-icon" viewBox="0 0 24 24" width="20" height="20">
        <path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
      </svg>
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="搜索问题关键词..."
        @keyup.enter="search"
      >
    </div>

    <div class="faq-content">
      <div v-for="category in faqCategories" :key="category.name" class="faq-category">
        <div class="category-title">{{ category.name }}</div>
        <div class="faq-list">
          <div 
            v-for="item in category.items" 
            :key="item.id"
            class="faq-item"
            :class="{ expanded: expandedId === item.id }"
            @click="toggleExpand(item.id)"
          >
            <div class="faq-question">
              <span class="q-badge">Q</span>
              <span class="question-text">{{ item.question }}</span>
              <svg class="arrow-icon" viewBox="0 0 24 24" width="20" height="20" :class="{ rotated: expandedId === item.id }">
                <path fill="currentColor" d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
              </svg>
            </div>
            <div class="faq-answer" v-show="expandedId === item.id">
              <span class="a-badge">A</span>
              <span class="answer-text">{{ item.answer }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="contact-section">
      <p>没有找到答案？</p>
      <button class="contact-btn" @click="goToChat">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
        </svg>
        联系人工客服
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')
const expandedId = ref<string | null>(null)

const faqCategories = ref([
  {
    name: '订单相关',
    items: [
      {
        id: '1',
        question: '如何查看我的订单状态？',
        answer: '您可以在"我的订单"页面查看所有订单的状态。订单状态包括：待付款、待发货、待收货、已完成等。点击具体订单可以查看详细信息。'
      },
      {
        id: '2',
        question: '订单可以取消吗？',
        answer: '未付款的订单可以自动取消；已付款未发货的订单可以联系客服申请取消；已发货的订单需要收货后申请退货退款。'
      },
      {
        id: '3',
        question: '如何修改订单地址？',
        answer: '订单未发货前可以联系客服修改收货地址。已发货的订单无法修改地址，建议联系快递公司协商。'
      }
    ]
  },
  {
    name: '物流相关',
    items: [
      {
        id: '4',
        question: '什么时候发货？',
        answer: '一般情况下，付款后24小时内发货。预售商品以页面标注的发货时间为准。节假日可能有所延迟。'
      },
      {
        id: '5',
        question: '发什么快递？',
        answer: '我们默认使用顺丰、中通、圆通等主流快递公司。您可以在订单详情页查看具体的物流公司和运单号。'
      },
      {
        id: '6',
        question: '如何查询物流信息？',
        answer: '在"我的订单"中点击对应订单，进入订单详情页即可查看物流跟踪信息。也可以复制运单号到快递公司官网查询。'
      }
    ]
  },
  {
    name: '售后相关',
    items: [
      {
        id: '7',
        question: '支持7天无理由退换货吗？',
        answer: '支持。自签收之日起7天内，商品未使用、包装完好、配件齐全的情况下可以申请无理由退换货。定制类商品除外。'
      },
      {
        id: '8',
        question: '如何申请售后？',
        answer: '在"我的订单"中找到对应订单，点击"申请售后"按钮，选择售后类型（退货/换货/维修），填写原因并提交即可。'
      },
      {
        id: '9',
        question: '退款多久到账？',
        answer: '退款申请审核通过后，款项将在1-3个工作日内原路退回。具体到账时间取决于银行或支付平台的处理速度。'
      }
    ]
  },
  {
    name: '优惠活动',
    items: [
      {
        id: '10',
        question: '有哪些优惠活动？',
        answer: '我们会不定期推出满减、折扣、赠品等优惠活动。请关注首页Banner或订阅我们的消息推送，及时获取优惠信息。'
      },
      {
        id: '11',
        question: '优惠券如何使用？',
        answer: '在购物车页面或结算页面，点击"使用优惠券"，选择符合条件的优惠券即可自动抵扣。注意查看优惠券的使用门槛和有效期。'
      }
    ]
  }
])

const toggleExpand = (id: string) => {
  expandedId.value = expandedId.value === id ? null : id
}

const search = () => {
  // 搜索功能
  console.log('搜索:', searchQuery.value)
}

const goToChat = () => {
  router.push('/')
}
</script>

<style scoped>
.faq-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 80px;
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

.search-box {
  display: flex;
  align-items: center;
  margin: 12px 16px;
  padding: 10px 16px;
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.search-icon {
  color: #999;
  margin-right: 10px;
  flex-shrink: 0;
}

.search-box input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  outline: none;
}

.search-box input::placeholder {
  color: #999;
}

.faq-content {
  padding: 0 16px;
}

.faq-category {
  margin-bottom: 16px;
}

.category-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  padding: 12px 0;
  margin-bottom: 8px;
}

.faq-list {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
}

.faq-item {
  border-bottom: 1px solid #f0f0f0;
}

.faq-item:last-child {
  border-bottom: none;
}

.faq-question {
  display: flex;
  align-items: center;
  padding: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.faq-question:hover {
  background: #fafafa;
}

.q-badge {
  width: 20px;
  height: 20px;
  background: #1677ff;
  color: #fff;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.question-text {
  flex: 1;
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}

.arrow-icon {
  color: #999;
  transition: transform 0.3s;
  flex-shrink: 0;
  margin-left: 8px;
}

.arrow-icon.rotated {
  transform: rotate(180deg);
}

.faq-answer {
  display: flex;
  padding: 0 16px 16px;
  background: #fafafa;
}

.a-badge {
  width: 20px;
  height: 20px;
  background: #52c41a;
  color: #fff;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.answer-text {
  flex: 1;
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

.contact-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: #fff;
  border-top: 1px solid #e8e8e8;
  text-align: center;
}

.contact-section p {
  font-size: 13px;
  color: #999;
  margin-bottom: 12px;
}

.contact-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 32px;
  background: #1677ff;
  color: #fff;
  border: none;
  border-radius: 24px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s;
}

.contact-btn:hover {
  background: #4096ff;
}

/* 响应式适配 */
@media (min-width: 481px) {
  .faq-page {
    max-width: 480px;
    margin: 0 auto;
    border-left: 1px solid #e8e8e8;
    border-right: 1px solid #e8e8e8;
  }
  
  .contact-section {
    max-width: 480px;
    left: 50%;
    transform: translateX(-50%);
  }
}

@media (min-width: 769px) {
  .faq-page {
    max-width: 600px;
  }
  
  .contact-section {
    max-width: 600px;
  }
}
</style>
