<template>
  <div class="chat-page">
    <!-- 头部 -->
    <header class="chat-header">
      <div class="shop-info">
        <img src="https://via.placeholder.com/40" alt="店铺" class="shop-avatar">
        <div class="shop-detail">
          <h3>官方客服</h3>
          <span class="status">
            <span class="status-dot online"></span>
            在线
          </span>
        </div>
      </div>
      <div class="header-actions">
        <button class="icon-btn" @click="showOrders = true">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- 消息列表 -->
    <div class="message-list" ref="messageListRef">
      <div class="message-date">今天</div>
      
      <div v-for="(msg, index) in messages" :key="index" 
           :class="['message', msg.type]">
        <div class="message-content">
          <div class="bubble" v-if="msg.type === 'ai' || msg.type === 'human'">
            <div class="avatar" v-if="msg.type === 'ai'">
              <img src="https://via.placeholder.com/32" alt="AI">
            </div>
            <div class="text">{{ msg.content }}</div>
          </div>
          
          <!-- 商品卡片 -->
          <div class="product-card" v-if="msg.product">
            <img :src="msg.product.image" alt="商品">
            <div class="product-info">
              <div class="product-title">{{ msg.product.title }}</div>
              <div class="product-price">¥{{ msg.product.price }}</div>
            </div>
          </div>
          
          <!-- 订单卡片 -->
          <div class="order-card" v-if="msg.order">
            <div class="order-header">
              <span>订单号：{{ msg.order.id }}</span>
              <span :class="['order-status', msg.order.status]">{{ msg.order.statusText }}</span>
            </div>
            <div class="order-items">
              <div v-for="item in msg.order.items" :key="item.id" class="order-item">
                <img :src="item.image" alt="">
                <span>{{ item.name }}</span>
              </div>
            </div>
          </div>
          
          <div class="message-time">{{ msg.time }}</div>
        </div>
      </div>
    </div>

    <!-- 快捷问题 -->
    <div class="quick-questions" v-if="showQuickQuestions">
      <div class="quick-title">常见问题</div>
      <div class="quick-list">
        <button v-for="q in quickQuestions" :key="q" 
                class="quick-btn" @click="sendQuick(q)">
          {{ q }}
        </button>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <div class="input-toolbar">
        <button class="tool-btn" @click="showEmoji = !showEmoji">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/>
          </svg>
        </button>
        <button class="tool-btn" @click="sendImage">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
          </svg>
        </button>
      </div>
      <div class="input-box">
        <textarea 
          v-model="inputMessage" 
          placeholder="请输入您的问题..."
          rows="1"
          @keydown.enter.prevent="sendMessage"
          @input="autoResize"
          ref="textareaRef"
        ></textarea>
        <button class="send-btn" :disabled="!inputMessage.trim()" @click="sendMessage">
          发送
        </button>
      </div>
    </div>

    <!-- 订单侧边栏 -->
    <div class="orders-drawer" :class="{ open: showOrders }" @click.self="showOrders = false">
      <div class="orders-panel">
        <div class="orders-header">
          <h3>我的订单</h3>
          <button class="close-btn" @click="showOrders = false">×</button>
        </div>
        <div class="orders-list">
          <div v-for="order in orders" :key="order.id" class="order-item-card">
            <div class="order-item-header">
              <span>{{ order.date }}</span>
              <span :class="['status', order.status]">{{ order.statusText }}</span>
            </div>
            <div class="order-item-body">
              <img :src="order.image" alt="">
              <div class="order-item-info">
                <div class="order-item-title">{{ order.title }}</div>
                <div class="order-item-price">¥{{ order.price }}</div>
              </div>
            </div>
            <div class="order-item-actions">
              <button class="action-btn primary" @click="consultOrder(order)">咨询此订单</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'

const messageListRef = ref<HTMLElement>()
const textareaRef = ref<HTMLTextAreaElement>()
const inputMessage = ref('')
const showOrders = ref(false)
const showQuickQuestions = ref(true)
const showEmoji = ref(false)

const quickQuestions = [
  '什么时候发货？',
  '支持退换货吗？',
  '有优惠活动吗？',
  '发什么快递？',
  '商品保修多久？'
]

const messages = ref([
  {
    type: 'ai',
    content: '您好！我是智能客服助手，很高兴为您服务。请问有什么可以帮助您的？',
    time: '09:30'
  }
])

const orders = ref([
  {
    id: '202403200001',
    date: '2024-03-20',
    status: 'shipped',
    statusText: '已发货',
    title: 'iPhone 15 Pro Max 256GB',
    price: '9999',
    image: 'https://via.placeholder.com/60'
  },
  {
    id: '202403190002',
    date: '2024-03-19',
    status: 'delivered',
    statusText: '已签收',
    title: 'AirPods Pro 2',
    price: '1899',
    image: 'https://via.placeholder.com/60'
  }
])

const autoResize = () => {
  const textarea = textareaRef.value
  if (textarea) {
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px'
  }
}

const sendMessage = () => {
  const text = inputMessage.value.trim()
  if (!text) return
  
  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: text,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  })
  
  inputMessage.value = ''
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }
  showQuickQuestions.value = false
  
  // 模拟AI回复
  setTimeout(() => {
    messages.value.push({
      type: 'ai',
      content: '收到您的问题，正在为您查询相关信息...',
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    })
    scrollToBottom()
  }, 500)
  
  scrollToBottom()
}

const sendQuick = (question: string) => {
  inputMessage.value = question
  sendMessage()
}

const sendImage = () => {
  // 模拟发送图片
  messages.value.push({
    type: 'user',
    content: '[图片]',
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  })
  scrollToBottom()
}

const consultOrder = (order: any) => {
  inputMessage.value = `我想咨询订单 ${order.id} 的相关问题`
  showOrders.value = false
  sendMessage()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

/* 头部 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  position: sticky;
  top: 0;
  z-index: 100;
}

.shop-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.shop-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.shop-detail h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online {
  background: #52c41a;
}

.icon-btn {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: #666;
  border-radius: 50%;
  transition: background 0.2s;
}

.icon-btn:hover {
  background: #f0f0f0;
}

/* 消息列表 */
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.message-date {
  text-align: center;
  color: #999;
  font-size: 12px;
  margin: 16px 0;
}

.message {
  margin-bottom: 16px;
}

.message.user {
  text-align: right;
}

.message-content {
  display: inline-block;
  max-width: 80%;
}

.bubble {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.message.user .bubble {
  flex-direction: row-reverse;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.text {
  background: #fff;
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
  word-break: break-word;
}

.message.user .text {
  background: #1677ff;
  color: #fff;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
  text-align: center;
}

/* 商品卡片 */
.product-card {
  display: flex;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  margin: 8px 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.product-card img {
  width: 80px;
  height: 80px;
  object-fit: cover;
}

.product-info {
  padding: 12px;
  flex: 1;
}

.product-title {
  font-size: 14px;
  color: #333;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-price {
  font-size: 16px;
  font-weight: 600;
  color: #ff4d4f;
  margin-top: 8px;
}

/* 订单卡片 */
.order-card {
  background: #fff;
  border-radius: 12px;
  padding: 12px;
  margin: 8px 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
}

.order-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}

.order-status.pending { background: #fff7e6; color: #fa8c16; }
.order-status.paid { background: #e6f7ff; color: #1890ff; }
.order-status.shipped { background: #f6ffed; color: #52c41a; }
.order-status.delivered { background: #f6ffed; color: #52c41a; }

/* 快捷问题 */
.quick-questions {
  background: #fff;
  padding: 12px 16px;
  border-top: 1px solid #e8e8e8;
}

.quick-title {
  font-size: 13px;
  color: #999;
  margin-bottom: 8px;
}

.quick-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-btn {
  background: #f0f0f0;
  border: none;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: #e0e0e0;
}

/* 输入区域 */
.input-area {
  background: #fff;
  border-top: 1px solid #e8e8e8;
  padding: 8px 12px;
}

.input-toolbar {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.tool-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: #666;
  border-radius: 4px;
  transition: background 0.2s;
}

.tool-btn:hover {
  background: #f0f0f0;
}

.input-box {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: #f5f5f5;
  border-radius: 20px;
  padding: 8px 12px;
}

.input-box textarea {
  flex: 1;
  border: none;
  background: transparent;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  max-height: 100px;
  outline: none;
  font-family: inherit;
}

.send-btn {
  background: #1677ff;
  color: #fff;
  border: none;
  padding: 6px 16px;
  border-radius: 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  background: #4096ff;
}

.send-btn:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
}

/* 订单抽屉 */
.orders-drawer {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 200;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s;
}

.orders-drawer.open {
  opacity: 1;
  visibility: visible;
}

.orders-panel {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 85%;
  max-width: 360px;
  background: #fff;
  transform: translateX(100%);
  transition: transform 0.3s;
  display: flex;
  flex-direction: column;
}

.orders-drawer.open .orders-panel {
  transform: translateX(0);
}

.orders-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e8e8e8;
}

.orders-header h3 {
  margin: 0;
  font-size: 16px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
}

.orders-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.order-item-card {
  background: #f5f5f5;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}

.order-item-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.order-item-body {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.order-item-body img {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
}

.order-item-info {
  flex: 1;
}

.order-item-title {
  font-size: 14px;
  color: #333;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.order-item-price {
  font-size: 16px;
  font-weight: 600;
  color: #ff4d4f;
  margin-top: 4px;
}

.order-item-actions {
  display: flex;
  justify-content: flex-end;
}

.action-btn {
  padding: 6px 16px;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid #d9d9d9;
  background: #fff;
}

.action-btn.primary {
  background: #1677ff;
  color: #fff;
  border-color: #1677ff;
}

/* 响应式适配 */
@media (min-width: 481px) {
  .chat-page {
    max-width: 480px;
    margin: 0 auto;
    border-left: 1px solid #e8e8e8;
    border-right: 1px solid #e8e8e8;
  }
}

@media (min-width: 769px) {
  .chat-page {
    max-width: 600px;
  }
  
  .message-content {
    max-width: 70%;
  }
}
</style>
