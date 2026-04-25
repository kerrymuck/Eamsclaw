<template>
  <div class="agent-workspace">
    <!-- 三栏式布局 -->
    <el-row :gutter="16" class="workspace-container">
      <!-- 左侧：会话列表 -->
      <el-col :xs="24" :sm="7" :md="6" :lg="5">
        <el-card class="panel-card" :body-style="{ padding: '0' }">
          <template #header>
            <div class="panel-header">
              <span>会话列表</span>
              <el-badge :value="unreadCount" v-if="unreadCount > 0" />
            </div>
          </template>
          
          <!-- 搜索框 -->
          <div class="search-box">
            <el-input 
              v-model="searchKeyword" 
              placeholder="搜索客户/订单/消息" 
              prefix-icon="Search"
              clearable
              size="small"
            />
          </div>
          
          <!-- 筛选标签 -->
          <el-tabs v-model="activeTab" stretch class="conv-tabs">
            <el-tab-pane label="全部" name="all">
              <div class="conversation-list">
                <div 
                  v-for="conv in filteredConversations" 
                  :key="conv.id"
                  :class="['conversation-item', { active: currentConversation?.id === conv.id }]"
                  @click="selectConversation(conv)"
                >
                  <div class="conv-main">
                    <el-avatar :size="40" :src="conv.avatar" />
                    <div class="conv-info">
                      <div class="conv-title">
                        <span class="customer-name">{{ conv.customerName }}</span>
                        <el-tag size="small" :type="getPlatformType(conv.platform)">{{ conv.platform }}</el-tag>
                      </div>
                      <div class="conv-preview">{{ conv.lastMessage }}</div>
                      <div class="conv-meta">
                        <span class="shop-name">{{ conv.shopName }}</span>
                        <span class="conv-time">{{ conv.lastTime }}</span>
                      </div>
                    </div>
                    <div class="conv-badge">
                      <el-badge :value="conv.unread" v-if="conv.unread > 0" />
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="待处理" name="pending">
              <div class="conversation-list">
                <div 
                  v-for="conv in pendingConversations" 
                  :key="conv.id"
                  :class="['conversation-item', { active: currentConversation?.id === conv.id }]"
                  @click="selectConversation(conv)"
                >
                  <div class="conv-main">
                    <el-avatar :size="40" :src="conv.avatar" />
                    <div class="conv-info">
                      <div class="conv-title">
                        <span class="customer-name">{{ conv.customerName }}</span>
                        <el-tag size="small" :type="getPlatformType(conv.platform)">{{ conv.platform }}</el-tag>
                      </div>
                      <div class="conv-preview">{{ conv.lastMessage }}</div>
                      <div class="conv-meta">
                        <span class="shop-name">{{ conv.shopName }}</span>
                        <span class="conv-time">{{ conv.lastTime }}</span>
                      </div>
                    </div>
                    <div class="conv-badge">
                      <el-badge :value="conv.unread" v-if="conv.unread > 0" />
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="已解决" name="resolved">
              <div class="empty-state">
                <el-empty description="暂无已解决会话" :image-size="80" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
      
      <!-- 中间：聊天窗口 -->
      <el-col :xs="24" :sm="10" :md="11" :lg="12">
        <el-card v-if="currentConversation" class="panel-card chat-panel" :body-style="{ padding: '0' }">
          <template #header>
            <div class="chat-header">
              <div class="customer-basic">
                <el-avatar :size="36" :src="currentConversation.avatar" />
                <div class="basic-info">
                  <div class="name-row">
                    <span class="customer-name">{{ currentConversation.customerName }}</span>
                    <el-tag size="small" :type="currentConversation.status === 'ai' ? 'primary' : 'success'">
                      {{ currentConversation.status === 'ai' ? 'AI处理中' : '人工处理' }}
                    </el-tag>
                  </div>
                  <div class="platform-row">
                    <el-tag size="small" :type="getPlatformType(currentConversation.platform)">
                      {{ currentConversation.platform }}
                    </el-tag>
                    <span class="shop-name">{{ currentConversation.shopName }}</span>
                  </div>
                </div>
              </div>
              <div class="chat-actions">
                <el-button type="primary" size="small" @click="transferToHuman" v-if="currentConversation.status === 'ai'">
                  转人工
                </el-button>
                <el-button type="success" size="small" @click="markAsResolved">
                  标记解决
                </el-button>
              </div>
            </div>
          </template>
          
          <!-- 消息列表 -->
          <div class="chat-messages" ref="messageContainer">
            <div 
              v-for="msg in currentMessages" 
              :key="msg.id"
              :class="['message', msg.type]"
            >
              <el-avatar 
                :size="32" 
                :src="msg.type === 'customer' ? currentConversation.avatar : aiAvatar" 
              />
              <div class="message-content">
                <div class="message-header">
                  <span class="sender">{{ msg.sender }}</span>
                  <span class="time">{{ msg.time }}</span>
                </div>
                <div class="message-body">{{ msg.content }}</div>
                <div class="message-actions" v-if="msg.type === 'ai'">
                  <el-button type="primary" link size="small" @click="useReply(msg)">采用</el-button>
                  <el-button type="danger" link size="small" @click="rejectReply(msg)">驳回</el-button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 输入框 -->
          <div class="chat-input-area">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="3"
              placeholder="输入消息... (Ctrl+Enter发送)"
              @keyup.enter.ctrl="sendMessage"
            />
            <div class="input-actions">
              <el-button type="primary" @click="sendMessage" :disabled="!inputMessage.trim()">
                发送
              </el-button>
            </div>
          </div>
        </el-card>
        
        <el-card v-else class="panel-card empty-panel" :body-style="{ display: 'flex', justifyContent: 'center', alignItems: 'center' }">
          <el-empty description="选择一个会话开始处理" :image-size="120" />
        </el-card>
      </el-col>
      
      <!-- 右侧：用户信息与订单 -->
      <el-col :xs="24" :sm="7" :md="7" :lg="7">
        <div class="right-panels">
          <!-- 用户信息 -->
          <el-card class="panel-card info-panel" v-if="currentConversation">
            <template #header>
              <div class="panel-header">
                <span>客户信息</span>
                <el-button type="primary" link size="small" @click="viewFullProfile">查看完整资料</el-button>
              </div>
            </template>
            <div class="customer-profile">
              <div class="profile-header">
                <el-avatar :size="60" :src="currentConversation.avatar" />
                <div class="profile-main">
                  <div class="profile-name">{{ currentCustomer?.name }}</div>
                  <div class="profile-id">ID: {{ currentCustomer?.customerId }}</div>
                  <div class="profile-tags">
                    <el-tag size="small" type="warning" v-if="currentCustomer?.vip">VIP</el-tag>
                    <el-tag size="small" type="success">{{ currentCustomer?.level }}</el-tag>
                  </div>
                </div>
              </div>
              <el-descriptions :column="1" size="small" border class="profile-details">
                <el-descriptions-item label="手机号">{{ currentCustomer?.phone }}</el-descriptions-item>
                <el-descriptions-item label="注册时间">{{ currentCustomer?.registerTime }}</el-descriptions-item>
                <el-descriptions-item label="累计消费">¥{{ currentCustomer?.totalSpent }}</el-descriptions-item>
                <el-descriptions-item label="订单数量">{{ currentCustomer?.orderCount }}笔</el-descriptions-item>
                <el-descriptions-item label="好评率">{{ currentCustomer?.rating }}%</el-descriptions-item>
              </el-descriptions>
            </div>
          </el-card>
          
          <!-- 订单信息 -->
          <el-card class="panel-card orders-panel" v-if="currentConversation">
            <template #header>
              <div class="panel-header">
                <span>订单信息</span>
                <el-input 
                  v-model="orderSearch" 
                  placeholder="搜索订单" 
                  size="small"
                  style="width: 120px"
                  clearable
                />
              </div>
            </template>
            <div class="orders-list">
              <div 
                v-for="order in filteredOrders" 
                :key="order.id"
                class="order-item"
                @click="viewOrderDetail(order)"
              >
                <div class="order-header">
                  <span class="order-no">{{ order.orderNo }}</span>
                  <el-tag :type="getOrderStatusType(order.status)" size="small">
                    {{ order.statusText }}
                  </el-tag>
                </div>
                <div class="order-products">
                  <div v-for="product in order.products" :key="product.id" class="product-item">
                    <el-image :src="product.image" fit="cover" class="product-img" />
                    <div class="product-info">
                      <div class="product-name">{{ product.name }}</div>
                      <div class="product-spec">{{ product.spec }}</div>
                      <div class="product-price">
                        <span class="price">¥{{ product.price }}</span>
                        <span class="quantity">x{{ product.quantity }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="order-footer">
                  <span class="order-time">{{ order.createTime }}</span>
                  <span class="order-total">合计: <strong>¥{{ order.total }}</strong></span>
                </div>
                <div class="order-actions">
                  <el-button type="primary" link size="small" @click.stop="sendOrderInfo(order)">发送订单信息</el-button>
                  <el-button type="success" link size="small" @click.stop="quickReply(order)">快捷回复</el-button>
                </div>
              </div>
            </div>
            <div v-if="filteredOrders.length === 0" class="empty-orders">
              <el-empty description="暂无订单信息" :image-size="80" />
            </div>
          </el-card>
          
          <!-- 快捷操作 -->
          <el-card class="panel-card quick-actions" v-if="currentConversation">
            <template #header>
              <div class="panel-header">
                <span>快捷操作</span>
              </div>
            </template>
            <div class="quick-buttons">
              <el-button type="primary" plain size="small" @click="quickReply('发货时间')">查询发货</el-button>
              <el-button type="success" plain size="small" @click="quickReply('物流信息')">查询物流</el-button>
              <el-button type="warning" plain size="small" @click="quickReply('退换货')">退换货</el-button>
              <el-button type="info" plain size="small" @click="quickReply('优惠券')">优惠券</el-button>
              <el-button type="primary" plain size="small" @click="quickReply('商品推荐')">商品推荐</el-button>
              <el-button type="danger" plain size="small" @click="quickReply('投诉建议')">投诉建议</el-button>
            </div>
          </el-card>
          
          <!-- 未选择会话提示 -->
          <el-card v-if="!currentConversation" class="panel-card empty-panel">
            <el-empty description="选择会话查看客户信息" :image-size="100" />
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()

const goBack = () => {
  router.push('/dashboard')
}

// AI头像
const aiAvatar = 'https://api.dicebear.com/7.x/bottts/svg?seed=AI-Assistant'

// 搜索关键词
const searchKeyword = ref('')
const orderSearch = ref('')

// 当前标签页
const activeTab = ref('all')

// 未读消息数
const unreadCount = computed(() => {
  return conversations.value.reduce((sum, conv) => sum + conv.unread, 0)
})

// 会话列表
const conversations = ref([
  { 
    id: 1, 
    customerName: '张先生', 
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=1',
    platform: '淘宝', 
    shopName: '科技云旗舰店',
    lastMessage: '这个商品什么时候发货？', 
    lastTime: '10:30',
    unread: 2,
    status: 'ai',
    customerId: 'C10001'
  },
  { 
    id: 2, 
    customerName: '李女士', 
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=2',
    platform: '京东', 
    shopName: '科技云数码店',
    lastMessage: '能便宜点吗？', 
    lastTime: '10:25',
    unread: 1,
    status: 'ai',
    customerId: 'C10002'
  },
  { 
    id: 3, 
    customerName: '王小姐', 
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=3',
    platform: '拼多多', 
    shopName: '科技云生活馆',
    lastMessage: '质量怎么样？', 
    lastTime: '10:20',
    unread: 0,
    status: 'human',
    customerId: 'C10003'
  },
  { 
    id: 4, 
    customerName: '赵先生', 
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=4',
    platform: '抖音', 
    shopName: '科技云直播间',
    lastMessage: '有优惠券吗？', 
    lastTime: '10:15',
    unread: 3,
    status: 'ai',
    customerId: 'C10004'
  }
])

// 客户信息数据
const customers = ref<Record<string, any>>({
  'C10001': {
    name: '张先生',
    customerId: 'C10001',
    phone: '138****8888',
    registerTime: '2023-06-15',
    totalSpent: '12,580.00',
    orderCount: 28,
    rating: 98,
    vip: true,
    level: '金牌会员'
  },
  'C10002': {
    name: '李女士',
    customerId: 'C10002',
    phone: '139****6666',
    registerTime: '2024-01-20',
    totalSpent: '3,260.00',
    orderCount: 8,
    rating: 100,
    vip: false,
    level: '银牌会员'
  },
  'C10003': {
    name: '王小姐',
    customerId: 'C10003',
    phone: '137****9999',
    registerTime: '2023-09-10',
    totalSpent: '8,750.00',
    orderCount: 15,
    rating: 95,
    vip: true,
    level: '金牌会员'
  },
  'C10004': {
    name: '赵先生',
    customerId: 'C10004',
    phone: '136****7777',
    registerTime: '2024-03-05',
    totalSpent: '1,280.00',
    orderCount: 3,
    rating: 100,
    vip: false,
    level: '普通会员'
  }
})

// 订单数据
const orders = ref<Record<string, any[]>>({
  'C10001': [
    {
      id: 'O202401001',
      orderNo: 'TB202401001',
      status: '待发货',
      statusText: '待发货',
      createTime: '2026-04-10 14:30',
      total: '2,999.00',
      products: [
        { id: 1, name: 'iPhone 15 Pro Max', spec: '256GB 钛金属', price: '2,999.00', quantity: 1, image: 'https://via.placeholder.com/60' }
      ]
    },
    {
      id: 'O202401002',
      orderNo: 'TB202312015',
      status: 'completed',
      statusText: '已完成',
      createTime: '2025-12-15 09:20',
      total: '599.00',
      products: [
        { id: 2, name: 'AirPods Pro 2', spec: '白色', price: '599.00', quantity: 1, image: 'https://via.placeholder.com/60' }
      ]
    }
  ],
  'C10002': [
    {
      id: 'O202401003',
      orderNo: 'JD202404008',
      status: 'shipping',
      statusText: '运输中',
      createTime: '2026-04-08 16:45',
      total: '1,299.00',
      products: [
        { id: 3, name: 'iPad Air 5', spec: '64GB 星光色', price: '1,299.00', quantity: 1, image: 'https://via.placeholder.com/60' }
      ]
    }
  ],
  'C10003': [
    {
      id: 'O202401004',
      orderNo: 'PDD202404001',
      status: 'pending',
      statusText: '待付款',
      createTime: '2026-04-12 10:00',
      total: '199.00',
      products: [
        { id: 4, name: '手机壳套装', spec: '透明+防摔', price: '99.00', quantity: 2, image: 'https://via.placeholder.com/60' }
      ]
    }
  ],
  'C10004': []
})

// 当前选中的会话
const currentConversation = ref<any>(null)

// 当前客户信息
const currentCustomer = computed(() => {
  if (!currentConversation.value) return null
  return customers.value[currentConversation.value.customerId]
})

// 当前客户的订单
const currentOrders = computed(() => {
  if (!currentConversation.value) return []
  return orders.value[currentConversation.value.customerId] || []
})

// 过滤后的订单
const filteredOrders = computed(() => {
  if (!orderSearch.value) return currentOrders.value
  return currentOrders.value.filter(order => 
    order.orderNo.includes(orderSearch.value) ||
    order.products.some((p: any) => p.name.includes(orderSearch.value))
  )
})

// 过滤后的会话列表
const filteredConversations = computed(() => {
  if (!searchKeyword.value) return conversations.value
  return conversations.value.filter(conv => 
    conv.customerName.includes(searchKeyword.value) ||
    conv.shopName.includes(searchKeyword.value) ||
    conv.lastMessage.includes(searchKeyword.value)
  )
})

// 待处理会话
const pendingConversations = computed(() => {
  return filteredConversations.value.filter(conv => conv.status === 'ai' || conv.unread > 0)
})

// 消息列表
const messages = ref<any[]>([])

// 当前会话的消息
const currentMessages = computed(() => {
  if (!currentConversation.value) return []
  return messages.value.filter(msg => msg.conversationId === currentConversation.value.id)
})

// 输入消息
const inputMessage = ref('')

// 选择会话
const selectConversation = (conv: any) => {
  currentConversation.value = conv
  loadMessages(conv.id)
}

// 加载消息
const loadMessages = (conversationId: number) => {
  messages.value = [
    { id: 1, conversationId, type: 'customer', sender: '客户', content: '你好，请问这个商品什么时候发货？', time: '10:00' },
    { id: 2, conversationId, type: 'ai', sender: 'AI助手', content: '您好！该商品目前库存充足，下单后24小时内发货。', time: '10:01' },
    { id: 3, conversationId, type: 'customer', sender: '客户', content: '好的，那什么时候能收到货呢？', time: '10:05' },
    { id: 4, conversationId, type: 'ai', sender: 'AI助手', content: '根据您的收货地址，预计3-5个工作日可以送达。', time: '10:06' }
  ].filter(msg => msg.conversationId === conversationId)
}

// 发送消息
const sendMessage = () => {
  if (!inputMessage.value.trim() || !currentConversation.value) return
  
  messages.value.push({
    id: Date.now(),
    conversationId: currentConversation.value.id,
    type: 'human',
    sender: '客服',
    content: inputMessage.value,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  })
  
  inputMessage.value = ''
}

// 转人工
const transferToHuman = () => {
  if (!currentConversation.value) return
  currentConversation.value.status = 'human'
  ElMessage.success('已转接人工客服')
}

// 标记解决
const markAsResolved = () => {
  ElMessage.success('已标记为已解决')
}

// 采用AI回复
const useReply = (msg: any) => {
  ElMessage.success('已采用AI回复')
}

// 驳回AI回复
const rejectReply = (msg: any) => {
  ElMessage.info('已驳回AI回复')
}

// 查看完整资料
const viewFullProfile = () => {
  ElMessage.info('查看完整客户资料')
}

// 查看订单详情
const viewOrderDetail = (order: any) => {
  ElMessage.info('查看订单详情: ' + order.orderNo)
}

// 发送订单信息
const sendOrderInfo = (order: any) => {
  inputMessage.value = `您的订单 ${order.orderNo} 当前状态：${order.statusText}，订单金额：¥${order.total}`
}

// 快捷回复
const quickReply = (type: string) => {
  const replies: Record<string, string> = {
    '发货时间': '亲，您的订单我们会在24小时内安排发货，请耐心等待~',
    '物流信息': '亲，您的订单已发货，快递单号：SF1234567890，可在顺丰官网查询~',
    '退换货': '亲，我们支持7天无理由退换货，如有需要请联系客服处理~',
    '优惠券': '亲，目前店铺有满299减20的优惠券可以领取哦~',
    '商品推荐': '亲，根据您的购买记录，推荐以下商品给您：',
    '投诉建议': '亲，非常抱歉给您带来不好的体验，我们会认真处理您的反馈~'
  }
  inputMessage.value = replies[type] || ''
}

// 获取平台标签类型
const getPlatformType = (platform: string) => {
  const typeMap: Record<string, string> = {
    '淘宝': 'danger',
    '天猫': 'danger',
    '京东': 'primary',
    '拼多多': 'success',
    '抖音': 'warning',
    '快手': 'warning',
    '小红书': 'info'
  }
  return typeMap[platform] || 'info'
}

// 获取订单状态类型
const getOrderStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    '待发货': 'warning',
    'shipping': 'primary',
    'completed': 'success',
    'pending': 'info'
  }
  return typeMap[status] || 'info'
}
</script>

<style scoped>
.agent-workspace {
  padding: 16px;
  height: calc(100vh - 50px);
  overflow: hidden;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.workspace-container {
  height: 100%;
}

.workspace-container > .el-col {
  height: 100%;
}

.panel-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-card :deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

/* 左侧会话列表 */
.search-box {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
}

.conv-tabs {
  height: calc(100% - 60px);
}

.conv-tabs :deep(.el-tabs__content) {
  height: calc(100% - 40px);
  overflow: hidden;
}

.conv-tabs :deep(.el-tab-pane) {
  height: 100%;
}

.conversation-list {
  height: 100%;
  overflow-y: auto;
}

.conversation-item {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background 0.2s;
}

.conversation-item:hover {
  background: #f5f7fa;
}

.conversation-item.active {
  background: #ecf5ff;
}

.conv-main {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.conv-info {
  flex: 1;
  min-width: 0;
}

.conv-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.customer-name {
  font-weight: 500;
  font-size: 14px;
  color: #303133;
}

.conv-preview {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.conv-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.shop-name {
  color: #909399;
}

.conv-time {
  color: #c0c4cc;
}

.conv-badge {
  flex-shrink: 0;
}

.empty-state {
  padding: 40px 0;
}

/* 中间聊天窗口 */
.chat-panel :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.customer-basic {
  display: flex;
  align-items: center;
  gap: 10px;
}

.basic-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name-row .customer-name {
  font-weight: 600;
  font-size: 15px;
}

.platform-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #f5f7fa;
}

.message {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.message.customer {
  flex-direction: row;
}

.message.ai,
.message.human {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 75%;
  background: #fff;
  padding: 10px 14px;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.message.customer .message-content {
  background: #fff;
}

.message.ai .message-content {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
}

.message.human .message-content {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-size: 12px;
}

.message.customer .message-header {
  color: #909399;
}

.message.ai .message-header {
  color: #1890ff;
}

.message.human .message-header {
  color: #52c41a;
}

.message-body {
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
}

.message-actions {
  margin-top: 6px;
  display: flex;
  gap: 8px;
}

.chat-input-area {
  padding: 12px 16px;
  border-top: 1px solid #ebeef5;
  background: #fff;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

/* 右侧面板 */
.right-panels {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  overflow-y: auto;
}

.info-panel {
  flex-shrink: 0;
}

.customer-profile {
  padding: 8px 0;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.profile-main {
  flex: 1;
}

.profile-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.profile-id {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.profile-tags {
  display: flex;
  gap: 6px;
}

.profile-details {
  margin-top: 12px;
}

/* 订单面板 */
.orders-panel {
  flex: 0 0 auto;
  max-height: 280px;
  min-height: 150px;
}

.orders-panel :deep(.el-card__body) {
  padding: 0;
  overflow-y: auto;
}

.orders-list {
  padding: 12px;
}

.order-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.order-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.order-no {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.order-products {
  margin-bottom: 10px;
}

.product-item {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px dashed #ebeef5;
}

.product-item:last-child {
  border-bottom: none;
}

.product-img {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  flex-shrink: 0;
}

.product-info {
  flex: 1;
  min-width: 0;
}

.product-name {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.product-spec {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.product-price {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.product-price .price {
  color: #f56c6c;
  font-weight: 600;
}

.product-price .quantity {
  color: #909399;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
  font-size: 12px;
}

.order-time {
  color: #909399;
}

.order-total {
  color: #606266;
}

.order-total strong {
  color: #f56c6c;
  font-size: 14px;
}

.order-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #ebeef5;
}

.empty-orders {
  padding: 20px 0;
}

/* 快捷操作 */
.quick-actions {
  flex: 0 0 auto;
  max-height: 120px;
}

.quick-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 0;
}

.quick-buttons .el-button {
  flex: 1;
  min-width: 80px;
}

.empty-panel {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>
