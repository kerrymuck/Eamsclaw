<template>
  <div class="chat-widget" :class="{ open: isOpen, minimized: isMinimized }">
    <!-- 悬浮按钮 -->
    <div v-if="!isOpen" class="float-button" @click="openChat">
      <div class="float-icon">💬</div>
      <div class="float-badge" v-if="unreadCount > 0">{{ unreadCount }}</div>
    </div>
    
    <!-- 聊天窗口 -->
    <div v-else class="chat-window">
      <!-- 头部 -->
      <header class="chat-header">
        <div class="shop-info">
          <img :src="shopInfo.logo" class="shop-logo" v-if="shopInfo.logo">
          <div class="shop-logo placeholder" v-else>{{ shopInfo.name[0] }}</div>
          <div class="shop-detail">
            <h3>{{ shopInfo.name }}</h3>
            <div class="shop-meta">
              <span class="platform-tag" :style="{ background: platformColor }">
                {{ platformIcon }} {{ platformName }}
              </span>
              <span class="status">
                <span class="status-dot" :class="{ online: isOnline }"></span>
                {{ isOnline ? '在线' : '离线' }}
              </span>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <button class="action-btn" @click="toggleMinimize" title="最小化">─</button>
          <button class="action-btn" @click="closeChat" title="关闭">×</button>
        </div>
      </header>
      
      <!-- 店铺公告 -->
      <div class="shop-notice" v-if="shopInfo.notice">
        <span>📢</span>
        <span>{{ shopInfo.notice }}</span>
      </div>
      
      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <div class="message-date" v-if="messages.length > 0">{{ todayDate }}</div>
        
        <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.type]">
          <div v-if="msg.type === 'system'" class="system-message">{{ msg.content }}</div>
          <div v-else class="message-wrapper">
            <div class="avatar" v-if="msg.type === 'ai'">
              <img :src="shopInfo.logo" v-if="shopInfo.logo">
              <span v-else>🤖</span>
            </div>
            <div class="message-content">
              <div class="sender-name" v-if="msg.type === 'ai'">{{ shopInfo.name }}</div>
              <div class="bubble" :class="msg.type">{{ msg.content }}</div>
              <div class="message-time">{{ msg.time }}</div>
            </div>
          </div>
        </div>
        
        <div v-if="isTyping" class="typing-indicator">
          <div class="avatar"><span>🤖</span></div>
          <div class="typing-bubble"><span></span><span></span><span></span></div>
        </div>
      </div>
      
      <!-- 快捷问题 -->
      <div class="quick-questions" v-if="showQuickQuestions">
        <div class="quick-title">💡 常见问题</div>
        <div class="quick-list">
          <button v-for="q in quickQuestions" :key="q.id" class="quick-btn" @click="sendQuick(q.text)">
            {{ q.text }}
          </button>
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="input-area">
        <div class="input-toolbar">
          <button class="tool-btn" @click="selectImage" title="图片">🖼️</button>
          <button class="tool-btn" @click="showOrders" title="我的订单">📦</button>
        </div>
        <div class="input-box">
          <textarea v-model="inputMessage" placeholder="请输入您的问题..." rows="1"
            @keydown.enter.prevent="sendMessage" @input="autoResize" ref="textareaRef"></textarea>
          <button class="send-btn" :disabled="!inputMessage.trim()" @click="sendMessage">发送</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'

const props = defineProps<{
  shopId: string
  platform: string
}>()

const isOpen = ref(false)
const isMinimized = ref(false)
const isOnline = ref(true)
const isTyping = ref(false)
const unreadCount = ref(2)
const showQuickQuestions = ref(true)
const inputMessage = ref('')
const messageListRef = ref<HTMLElement>()
const textareaRef = ref<HTMLTextAreaElement>()

const shopInfo = ref({
  name: '龙猫数码旗舰店',
  logo: '',
  notice: '🎉 新春大促，全场满299减50！',
})

const platformConfig: Record<string, { name: string; icon: string; color: string }> = {
  // 阿里系
  taobao: { name: '淘宝', icon: '🍑', color: '#ff5000' },
  tmall: { name: '天猫', icon: '🐱', color: '#ff0036' },
  alibaba: { name: '1688', icon: '🔶', color: '#ff6a00' },
  aliexpress: { name: '速卖通', icon: '🌍', color: '#ff4747' },
  // 其他国内平台
  jd: { name: '京东', icon: '🐕', color: '#e4393c' },
  pdd: { name: '拼多多', icon: '🟥', color: '#e02e24' },
  douyin: { name: '抖店', icon: '🎵', color: '#000000' },
  xiaohongshu: { name: '小红书', icon: '📕', color: '#ff2442' },
}

const platformName = computed(() => platformConfig[props.platform]?.name || '官方')
const platformIcon = computed(() => platformConfig[props.platform]?.icon || '🏪')
const platformColor = computed(() => platformConfig[props.platform]?.color || '#409eff')
const todayDate = computed(() => {
  const date = new Date()
  return `${date.getMonth() + 1}月${date.getDate()}日`
})

const quickQuestions = ref([
  { id: 1, text: '什么时候发货？' },
  { id: 2, text: '支持退换货吗？' },
  { id: 3, text: '有优惠活动吗？' },
  { id: 4, text: '发什么快递？' },
])

const messages = ref([
  {
    type: 'ai',
    content: '您好！欢迎光临龙猫数码旗舰店，我是您的智能客服助手。请问有什么可以帮助您的？😊',
    time: '12:30',
  },
])

const openChat = () => { isOpen.value = true; isMinimized.value = false; scrollToBottom() }
const closeChat = () => { isOpen.value = false; isMinimized.value = false }
const toggleMinimize = () => { isMinimized.value = !isMinimized.value }

const autoResize = () => {
  const textarea = textareaRef.value
  if (textarea) {
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px'
  }
}

const sendMessage = async () => {
  const text = inputMessage.value.trim()
  if (!text) return
  
  messages.value.push({
    type: 'user',
    content: text,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
  })
  
  inputMessage.value = ''
  if (textareaRef.value) textareaRef.value.style.height = 'auto'
  showQuickQuestions.value = false
  scrollToBottom()
  
  isTyping.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  isTyping.value = false
  
  messages.value.push({
    type: 'ai',
    content: '收到您的问题，正在为您查询相关信息...',
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
  })
  scrollToBottom()
}

const sendQuick = (text: string) => {
  inputMessage.value = text
  sendMessage()
}

const selectImage = () => {}
const showOrders = () => {}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  })
}
</script>

<style scoped>
.chat-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.float-button {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  transition: all 0.3s;
}

.float-button:hover { transform: scale(1.1); }

.float-icon { font-size: 28px; }

.float-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 24px;
  height: 24px;
  background: #ff4d4f;
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-window {
  width: 380px;
  height: 600px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.shop-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.shop-logo {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.shop-logo.placeholder {
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
}

.shop-detail h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
}

.shop-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.platform-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #fff;
}

.status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  opacity: 0.9;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
}

.status-dot.online {
  background: #52c41a;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.header-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.shop-notice {
  padding: 10px 16px;
  background: #fff7e6;
  border-bottom: 1px solid #ffd591;
  font-size: 13px;
  color: #d46b08;
  display: flex;
  align-items: center;
  gap: 8px;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f5f5;
}

.message-date {
  text-align: center;
  color: #999;
  font-size: 12px;
  margin: 16px 0;
}

.system-message {
  text-align: center;
  color: #999;
  font-size: 12px;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 16px;
  display: inline-block;
  margin: 8px auto;
}

.message { margin-bottom: 16px; }

.message-wrapper {
  display: flex;
  gap: 8px;
}

.message.user .message-wrapper {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
}

.message-content {
  max-width: 75%;
}

.sender-name {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.bubble {
  padding: 12px 16px;
  border-radius: 16px;
  word-break: break-word;
}

.bubble.ai {
  background: #fff;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.bubble.user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.typing-bubble {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 16px;
  border-bottom-left-radius: 4px;
}

.typing-bubble span {
  width: 8px;
  height: 8px;
  background: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-bubble span:nth-child(2) { animation-delay: 0.2s; }
.typing-bubble span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-10px); }
}

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
  padding: 6px 12px;
  background: #f0f0f0;
  border: none;
  border-radius: 16px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-btn:hover {
  background: #667eea;
  color: #fff;
}

.input-area {
  background: #fff;
  border-top: 1px solid #e8e8e8;
  padding: 12px;
}

.input-toolbar {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.tool-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  opacity: 0.7;
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
  padding: 8px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 16px;
  font-size: 14px;
  cursor: pointer;
}

.send-btn:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
}
</style>
