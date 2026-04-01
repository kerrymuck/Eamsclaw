<template>
  <div class="unified-inbox">
    <!-- 左侧：平台/店铺筛选 + 会话列表 -->
    <aside class="sidebar-left">
      <!-- 店铺筛选 -->
      <div class="shop-filter">
        <div class="filter-header">
          <span class="title">📬 统一收件箱</span>
          <el-badge :value="totalUnread" v-if="totalUnread > 0" />
        </div>
        
        <!-- 平台筛选标签 -->
        <div class="platform-tabs">
          <div 
            v-for="platform in platforms" 
            :key="platform.id"
            :class="['platform-tab', { active: currentPlatform === platform.id }]"
            @click="selectPlatform(platform.id)"
          >
            <span class="platform-icon">{{ platform.icon }}</span>
            <span class="platform-name">{{ platform.name }}</span>
            <el-badge :value="platform.unread" v-if="platform.unread > 0" />
          </div>
        </div>
        
        <!-- 店铺选择器 -->
        <div class="shop-selector" v-if="currentPlatform !== 'all'">
          <el-select 
            v-model="currentShop" 
            placeholder="选择店铺" 
            size="small"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="shop in filteredShops"
              :key="shop.id"
              :label="shop.name"
              :value="shop.id"
            >
              <span style="float: left">{{ shop.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                <el-badge :value="shop.unread" v-if="shop.unread > 0" />
              </span>
            </el-option>
          </el-select>
        </div>
        
        <!-- 所有店铺列表（按平台分组） -->
        <div class="all-shops" v-else>
          <el-collapse v-model="expandedShops">
            <el-collapse-item 
              v-for="group in shopGroups" 
              :key="group.platform"
              :title="group.platformName + ' (' + group.shops.length + ')'"
              :name="group.platform"
            >
              <div 
                v-for="shop in group.shops" 
                :key="shop.id"
                :class="['shop-item', { active: currentShop === shop.id }]"
                @click="selectShop(shop.id)"
              >
                <el-avatar :size="24" :src="shop.logo">{{ shop.name[0] }}</el-avatar>
                <span class="shop-name">{{ shop.name }}</span>
                <el-badge :value="shop.unread" v-if="shop.unread > 0" />
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
      
      <!-- 会话列表 -->
      <div class="conversation-list">
        <div class="list-header">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索客户" 
            :prefix-icon="Search"
            size="small"
          />
          <el-dropdown>
            <el-button size="small">筛选</el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>待处理</el-dropdown-item>
                <el-dropdown-item>AI处理中</el-dropdown-item>
                <el-dropdown-item>需人工</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        
        <div class="conversations">
          <div 
            v-for="conv in filteredConversations" 
            :key="conv.id"
            :class="['conversation-item', { 
              active: currentConversation?.id === conv.id,
              'ai-handling': conv.aiStatus === 'handling',
              'need-human': conv.aiStatus === 'need_human'
            }]"
            @click="selectConversation(conv)"
          >
            <div class="conv-platform" :style="{ color: getPlatformColor(conv.platform) }">
              {{ getPlatformIcon(conv.platform) }}
            </div>
            <div class="conv-content">
              <div class="conv-header">
                <span class="username">{{ conv.customerName }}</span>
                <span class="time">{{ conv.lastMessageTime }}</span>
              </div>
              <div class="conv-preview">
                <el-tag size="small" v-if="conv.aiStatus === 'handling'" type="success">AI处理中</el-tag>
                <el-tag size="small" v-else-if="conv.aiStatus === 'need_human'" type="warning">需人工</el-tag>
                {{ conv.lastMessage }}
              </div>
            </div>
            <div class="conv-meta">
              <el-badge :value="conv.unread" v-if="conv.unread > 0" />
              <el-tag size="small" v-if="conv.customerTag" :type="conv.tagType">{{ conv.customerTag }}</el-tag>
            </div>
          </div>
        </div>
      </div>
    </aside>
    
    <!-- 中间：对话区域 -->
    <main class="chat-area">
      <template v-if="currentConversation">
        <!-- 对话头部 -->
        <header class="chat-header">
          <div class="customer-info">
            <el-avatar :size="40">{{ currentConversation.customerName[0] }}</el-avatar>
            <div class="info-detail">
              <div class="name-row">
                <span class="name">{{ currentConversation.customerName }}</span>
                <el-tag size="small" :type="currentConversation.tagType">{{ currentConversation.customerTag }}</el-tag>
                <span class="platform-tag" :style="{ background: getPlatformColor(currentConversation.platform) }">
                  {{ getPlatformName(currentConversation.platform) }}
                </span>
              </div>
              <div class="meta-row">
                <span>累计消费: ¥{{ currentConversation.totalSpent }}</span>
                <span>订单数: {{ currentConversation.orderCount }}</span>
                <span>咨询次数: {{ currentConversation.inquiryCount }}</span>
              </div>
            </div>
          </div>
          <div class="chat-actions">
            <el-button 
              type="warning" 
              size="small"
              v-if="currentConversation.aiStatus === 'handling'"
              @click="takeOver"
            >
              接管对话
            </el-button>
            <el-button type="danger" size="small" @click="closeConversation">结束会话</el-button>
          </div>
        </header>
        
        <!-- AI建议面板 -->
        <div class="ai-suggestions" v-if="aiSuggestions.length > 0">
          <div class="suggestion-header">
            <el-icon><MagicStick /></el-icon>
            <span>AI建议回复</span>
            <span class="confidence">置信度: {{ aiConfidence }}%</span>
          </div>
          <div class="suggestion-list">
            <div 
              v-for="(suggestion, index) in aiSuggestions" 
              :key="index"
              class="suggestion-item"
              @click="applySuggestion(suggestion)"
            >
              {{ suggestion.text }}
            </div>
          </div>
        </div>
        
        <!-- 消息列表 -->
        <div class="message-list" ref="messageListRef">
          <div 
            v-for="msg in currentConversation.messages" 
            :key="msg.id"
            :class="['message', msg.sender]"
          >
            <div class="message-content">
              <div class="sender-info" v-if="msg.sender === 'ai'">
                <el-tag size="small" type="success">🤖 AI</el-tag>
              </div>
              <div class="sender-info" v-else-if="msg.sender === 'agent'">
                <el-tag size="small" type="primary">👤 客服</el-tag>
              </div>
              <div class="bubble">{{ msg.content }}</div>
              <div class="message-meta">
                <span class="time">{{ msg.time }}</span>
                <span class="platform" v-if="msg.platform">{{ getPlatformIcon(msg.platform) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 快捷回复 -->
        <div class="quick-replies">
          <el-scrollbar>
            <div class="quick-list">
              <el-button 
                v-for="reply in quickReplies" 
                :key="reply.id"
                size="small"
                @click="sendQuickReply(reply)"
              >
                {{ reply.text }}
              </el-button>
            </div>
          </el-scrollbar>
        </div>
        
        <!-- 输入区域 -->
        <div class="input-area">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入消息..."
            @keydown.enter.prevent="sendMessage"
          />
          <div class="input-actions">
            <el-button>📎</el-button>
            <el-button type="primary" @click="sendMessage" :disabled="!inputMessage.trim()">发送</el-button>
          </div>
        </div>
      </template>
      
      <el-empty v-else description="选择一个会话开始沟通">
        <template #image>
          <el-icon :size="60" color="#909399"><ChatDotRound /></el-icon>
        </template>
      </el-empty>
    </main>
    
    <!-- 右侧：用户资料 + 订单信息 -->
    <aside class="sidebar-right" v-if="currentConversation">
      <!-- 用户画像 -->
      <el-card class="profile-card">
        <template #header>
          <span>👤 客户画像</span>
        </template>
        <div class="profile-content">
          <div class="profile-item">
            <span class="label">客户ID</span>
            <span class="value">{{ currentConversation.customerId }}</span>
          </div>
          <div class="profile-item">
            <span class="label">手机号</span>
            <span class="value">{{ currentConversation.phone }}</span>
          </div>
          <div class="profile-item highlight">
            <span class="label">累计消费</span>
            <span class="value price">¥{{ currentConversation.totalSpent }}</span>
          </div>
          <div class="profile-item">
            <span class="label">跨平台订单</span>
            <span class="value">{{ currentConversation.orderCount }}笔</span>
          </div>
          <div class="profile-item">
            <span class="label">客户标签</span>
            <div class="tags">
              <el-tag v-for="tag in currentConversation.tags" :key="tag" size="small">{{ tag }}</el-tag>
            </div>
          </div>
        </div>
      </el-card>
      
      <!-- 最近订单 -->
      <el-card class="orders-card">
        <template #header>
          <div class="card-header">
            <span>📦 最近订单 (跨平台)</span>
            <el-link type="primary" size="small">查看全部</el-link>
          </div>
        </template>
        <div class="orders-list">
          <div 
            v-for="order in currentConversation.recentOrders" 
            :key="order.id"
            class="order-item"
          >
            <div class="order-header">
              <span class="platform" :style="{ color: getPlatformColor(order.platform) }">
                {{ getPlatformIcon(order.platform) }} {{ getPlatformName(order.platform) }}
              </span>
              <el-tag size="small" :type="getOrderStatusType(order.status)">
                {{ order.statusText }}
              </el-tag>
            </div>
            <div class="order-body">
              <img :src="order.image" class="order-image" />
              <div class="order-info">
                <div class="order-title">{{ order.title }}</div>
                <div class="order-price">¥{{ order.price }}</div>
              </div>
            </div>
            <div class="order-actions">
              <el-button size="small" @click="queryLogistics(order)">查物流</el-button>
              <el-button size="small" type="primary" @click="consultOrder(order)">咨询此单</el-button>
            </div>
          </div>
        </div>
      </el-card>
      
      <!-- 快捷操作 -->
      <el-card class="actions-card">
        <template #header>
          <span>⚡ 快捷操作</span>
        </template>
        <div class="quick-actions">
          <el-button size="small" @click="createOrder">📝 创建订单</el-button>
          <el-button size="small" @click="applyRefund">💰 申请退款</el-button>
          <el-button size="small" @click="modifyAddress">📍 修改地址</el-button>
          <el-button size="small" @click="sendCoupon">🎫 发送优惠券</el-button>
        </div>
      </el-card>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, ChatDotRound, MagicStick } from '@element-plus/icons-vue'

// 平台配置 - 支持国内及跨境主流电商平台
const platforms = [
  { id: 'all', name: '全部', icon: '📬', unread: 12 },
  // 阿里系
  { id: 'taobao', name: '淘宝', icon: '🍑', unread: 5 },
  { id: 'tmall', name: '天猫', icon: '🐱', unread: 3 },
  { id: 'alibaba', name: '1688', icon: '🔶', unread: 2 },
  { id: 'aliexpress', name: '速卖通', icon: '🌍', unread: 1 },
  // 其他国内平台
  { id: 'jd', name: '京东', icon: '🐕', unread: 4 },
  { id: 'pdd', name: '拼多多', icon: '🟥', unread: 3 },
  { id: 'douyin', name: '抖店', icon: '🎵', unread: 2 },
  { id: 'xiaohongshu', name: '小红书', icon: '📕', unread: 1 },
]

// 店铺数据
const shops = ref([
  { id: 1, name: '龙猫数码旗舰店', platform: 'taobao', logo: '', unread: 3 },
  { id: 2, name: '龙猫淘宝二店', platform: 'taobao', logo: '', unread: 2 },
  { id: 3, name: '龙猫京东自营', platform: 'jd', logo: '', unread: 4 },
  { id: 4, name: '龙猫京东POP', platform: 'jd', logo: '', unread: 0 },
  { id: 5, name: '龙猫拼多多店', platform: 'pdd', logo: '', unread: 3 },
])

const currentShop = ref<number | null>(null)
const expandedShops = ref(['taobao', 'jd', 'pdd'])

const currentPlatform = ref('all')
const searchQuery = ref('')
const currentConversation = ref<any>(null)
const inputMessage = ref('')
const messageListRef = ref<HTMLElement>()

// 按平台分组的店铺
const shopGroups = computed(() => {
  const groups: Record<string, any> = {
    // 阿里系
    taobao: { platform: 'taobao', platformName: '🍑 淘宝', shops: [] },
    tmall: { platform: 'tmall', platformName: '🐱 天猫', shops: [] },
    alibaba: { platform: 'alibaba', platformName: '🔶 1688', shops: [] },
    aliexpress: { platform: 'aliexpress', platformName: '🌍 速卖通', shops: [] },
    // 其他国内平台
    jd: { platform: 'jd', platformName: '🐕 京东', shops: [] },
    pdd: { platform: 'pdd', platformName: '🟥 拼多多', shops: [] },
    douyin: { platform: 'douyin', platformName: '🎵 抖店', shops: [] },
    xiaohongshu: { platform: 'xiaohongshu', platformName: '📕 小红书', shops: [] },
  }
  shops.value.forEach(shop => {
    if (groups[shop.platform]) {
      groups[shop.platform].shops.push(shop)
    }
  })
  return Object.values(groups).filter(g => g.shops.length > 0)
})

// 筛选后的店铺
const filteredShops = computed(() => {
  if (currentPlatform.value === 'all') return shops.value
  return shops.value.filter(s => s.platform === currentPlatform.value)
})

// 模拟会话数据
const conversations = ref([
  {
    id: 1,
    customerName: '张先生',
    customerId: 'TB_123456',
    phone: '138****8888',
    platform: 'taobao',
    lastMessage: '我的订单什么时候发货？',
    lastMessageTime: '2分钟前',
    unread: 2,
    aiStatus: 'handling', // handling, need_human, human
    customerTag: 'VIP',
    tagType: 'danger',
    totalSpent: 12580,
    orderCount: 15,
    inquiryCount: 8,
    tags: ['高价值', '复购率高'],
    messages: [
      { id: 1, sender: 'customer', content: '你好，我想问一下我的订单', time: '12:30', platform: 'taobao' },
      { id: 2, sender: 'ai', content: '您好！我是智能客服，请问您的订单号是多少呢？', time: '12:30' },
      { id: 3, sender: 'customer', content: '我的订单什么时候发货？', time: '12:31', platform: 'taobao' },
    ],
    recentOrders: [
      { id: 'TB20240320001', platform: 'taobao', title: 'iPhone 15 Pro Max', price: '9999', status: 'shipped', statusText: '已发货', image: '' },
      { id: 'JD20240319001', platform: 'jd', title: 'AirPods Pro 2', price: '1899', status: 'delivered', statusText: '已签收', image: '' },
    ]
  },
  {
    id: 2,
    customerName: '李女士',
    customerId: 'JD_789012',
    phone: '139****6666',
    platform: 'jd',
    lastMessage: '这个商品有优惠吗？',
    lastMessageTime: '5分钟前',
    unread: 1,
    aiStatus: 'need_human',
    customerTag: '新客户',
    tagType: 'success',
    totalSpent: 299,
    orderCount: 1,
    inquiryCount: 3,
    tags: ['价格敏感'],
    messages: [
      { id: 1, sender: 'customer', content: '这个商品有优惠吗？', time: '12:25', platform: 'jd' },
      { id: 2, sender: 'ai', content: '抱歉，AI无法识别您的具体商品，建议转人工处理。', time: '12:26' },
    ],
    recentOrders: [
      { id: 'JD20240318001', platform: 'jd', title: '小米手机', price: '2999', status: 'paid', statusText: '待发货', image: '' },
    ]
  }
])

const aiSuggestions = ref([
  { text: '您的订单已于今日发货，预计3天内送达。' },
  { text: '抱歉让您久等了，我帮您查询一下物流信息。' },
  { text: '您可以在订单详情页查看实时物流状态。' },
])
const aiConfidence = ref(92)

const quickReplies = ref([
  { id: 1, text: '今日已发货' },
  { id: 2, text: '预计3天送达' },
  { id: 3, text: '请提供订单号' },
  { id: 4, text: '支持7天无理由退换' },
])

const totalUnread = computed(() => conversations.value.reduce((sum, c) => sum + c.unread, 0))

const filteredConversations = computed(() => {
  let result = conversations.value
  if (currentPlatform.value !== 'all') {
    result = result.filter(c => c.platform === currentPlatform.value)
  }
  if (searchQuery.value) {
    result = result.filter(c => c.customerName.includes(searchQuery.value))
  }
  return result
})

const selectPlatform = (id: string) => {
  currentPlatform.value = id
  currentShop.value = null
}

const selectShop = (shopId: number) => {
  currentShop.value = shopId
}

const selectConversation = (conv: any) => {
  currentConversation.value = conv
  conv.unread = 0
}

const getPlatformColor = (platform: string) => {
  const colors: Record<string, string> = {
    taobao: '#ff5000',
    tmall: '#ff0036',
    alibaba: '#ff6a00',
    aliexpress: '#ff4747',
    jd: '#e4393c',
    pdd: '#e02e24',
    douyin: '#000000',
    xiaohongshu: '#ff2442',
  }
  return colors[platform] || '#666'
}

const getPlatformIcon = (platform: string) => {
  const icons: Record<string, string> = {
    taobao: '🍑',
    tmall: '🐱',
    alibaba: '🔶',
    aliexpress: '🌍',
    jd: '🐕',
    pdd: '🟥',
    douyin: '🎵',
    xiaohongshu: '📕',
  }
  return icons[platform] || '📦'
}

const getPlatformName = (platform: string) => {
  const names: Record<string, string> = {
    taobao: '淘宝',
    tmall: '天猫',
    alibaba: '1688',
    aliexpress: '速卖通',
    jd: '京东',
    pdd: '拼多多',
    douyin: '抖店',
    xiaohongshu: '小红书',
  }
  return names[platform] || platform
}

const getOrderStatusType = (status: string) => {
  const types: Record<string, string> = {
    paid: 'primary',
    shipped: 'success',
    delivered: 'success',
    refunded: 'warning',
  }
  return types[status] || 'info'
}

const sendMessage = () => {
  if (!inputMessage.value.trim() || !currentConversation.value) return
  
  currentConversation.value.messages.push({
    id: Date.now(),
    sender: 'agent',
    content: inputMessage.value,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  })
  inputMessage.value = ''
}

const sendQuickReply = (reply: any) => {
  inputMessage.value = reply.text
  sendMessage()
}

const applySuggestion = (suggestion: any) => {
  inputMessage.value = suggestion.text
}

const takeOver = () => {
  if (currentConversation.value) {
    currentConversation.value.aiStatus = 'human'
  }
}

const closeConversation = () => {
  currentConversation.value = null
}

const queryLogistics = (order: any) => {
  inputMessage.value = `订单${order.id}的物流信息显示：已到达【杭州转运中心】，预计明天送达。`
}

const consultOrder = (order: any) => {
  inputMessage.value = `关于您的订单 ${order.title} (${order.id})，请问有什么可以帮您的？`
}

const createOrder = () => {}
const applyRefund = () => {}
const modifyAddress = () => {}
const sendCoupon = () => {}
</script>

<style scoped>
.unified-inbox {
  display: flex;
  height: calc(100vh - 60px);
  background: #f5f7fa;
}

/* 左侧边栏 */
.sidebar-left {
  width: 280px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.platform-filter {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.filter-header .title {
  font-weight: 600;
  font-size: 16px;
}

.platform-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.platform-tab {
  padding: 6px 12px;
  border-radius: 16px;
  background: #f5f7fa;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  transition: all 0.3s;
}

.platform-tab:hover,
.platform-tab.active {
  background: #409eff;
  color: #fff;
}

.conversation-list {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.list-header {
  padding: 12px;
  display: flex;
  gap: 8px;
}

.conversations {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  display: flex;
  gap: 10px;
  transition: all 0.3s;
}

.conversation-item:hover,
.conversation-item.active {
  background: #f5f7fa;
}

.conversation-item.ai-handling {
  border-left: 3px solid #67c23a;
}

.conversation-item.need-human {
  border-left: 3px solid #e6a23c;
}

.conv-platform {
  font-size: 20px;
}

.conv-content {
  flex: 1;
  min-width: 0;
}

.conv-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.username {
  font-weight: 500;
  color: #303133;
}

.time {
  font-size: 12px;
  color: #909399;
}

.conv-preview {
  font-size: 13px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
}

.conv-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

/* 中间聊天区域 */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  min-width: 0;
}

.chat-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.customer-info {
  display: flex;
  gap: 12px;
}

.info-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name {
  font-weight: 600;
  font-size: 16px;
}

.platform-tag {
  padding: 2px 8px;
  border-radius: 4px;
  color: #fff;
  font-size: 12px;
}

.meta-row {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #606266;
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.ai-suggestions {
  background: #f0f9ff;
  border-bottom: 1px solid #e4e7ed;
  padding: 12px 16px;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: #096dd9;
  font-size: 13px;
}

.confidence {
  margin-left: auto;
  color: #52c41a;
}

.suggestion-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.suggestion-item {
  padding: 6px 12px;
  background: #fff;
  border: 1px solid #91caff;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.suggestion-item:hover {
  background: #e6f7ff;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
}

.message {
  margin-bottom: 16px;
  display: flex;
}

.message.customer {
  justify-content: flex-end;
}

.message-content {
  max-width: 70%;
}

.sender-info {
  margin-bottom: 4px;
}

.bubble {
  padding: 12px 16px;
  border-radius: 12px;
  background: #fff;
  word-break: break-word;
}

.message.customer .bubble {
  background: #409eff;
  color: #fff;
}

.message.ai .bubble {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
}

.message-meta {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.quick-replies {
  padding: 8px 16px;
  border-top: 1px solid #e4e7ed;
  background: #fff;
}

.quick-list {
  display: flex;
  gap: 8px;
}

.input-area {
  padding: 12px 16px;
  border-top: 1px solid #e4e7ed;
  background: #fff;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

/* 右侧边栏 */
.sidebar-right {
  width: 320px;
  background: #fff;
  border-left: 1px solid #e4e7ed;
  padding: 16px;
  overflow-y: auto;
}

.profile-card,
.orders-card,
.actions-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.profile-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-item.highlight {
  padding: 8px;
  background: #fff7e6;
  border-radius: 4px;
}

.profile-item .label {
  color: #606266;
  font-size: 13px;
}

.profile-item .value {
  color: #303133;
  font-weight: 500;
}

.profile-item .value.price {
  color: #f56c6c;
  font-size: 18px;
}

.tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.order-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 12px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.order-body {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.order-image {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  background: #e4e7ed;
}

.order-info {
  flex: 1;
}

.order-title {
  font-size: 13px;
  color: #303133;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.order-price {
  color: #f56c6c;
  font-weight: 600;
  margin-top: 4px;
}

.order-actions {
  display: flex;
  gap: 8px;
}

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

/* 响应式 */
@media screen and (max-width: 1200px) {
  .sidebar-right {
    display: none;
  }
}

@media screen and (max-width: 768px) {
  .sidebar-left {
    width: 100%;
  }
  .chat-area {
    display: none;
  }
}
</style>
