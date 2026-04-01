<template>
  <div class="conversations">
    <!-- 移动端返回按钮 -->
    <div v-if="isMobile && showChat" class="mobile-back">
      <el-button @click="backToList" :icon="ArrowLeft">返回列表</el-button>
    </div>
    
    <el-row :gutter="20" class="conversation-row">
      <!-- 会话列表 -->
      <el-col 
        :xs="24" 
        :sm="24" 
        :md="8" 
        :lg="8"
        class="list-col"
        :class="{ 'mobile-hidden': isMobile && showChat }"
      >
        <el-card class="list-card">
          <template #header>
            <div class="card-header">
              <span>会话列表</span>
              <el-radio-group v-model="filterStatus" size="small" class="filter-group">
                <el-radio-button label="active">进行中</el-radio-button>
                <el-radio-button label="pending_handoff">待人工</el-radio-button>
                <el-radio-button label="closed">已关闭</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户"
            :prefix-icon="Search"
            class="search-input"
          />
          
          <div class="conversation-list">
            <div
              v-for="conv in filteredConversations"
              :key="conv.id"
              class="conversation-item"
              :class="{ active: currentConversation?.id === conv.id, 'has-unread': conv.unread_count > 0 }"
              @click="selectConversation(conv)"
            >
              <div class="conv-header">
                <span class="username">{{ conv.platform_user_name }}</span>
                <el-tag size="small" :type="getStatusType(conv.status)">
                  {{ getStatusText(conv.status) }}
                </el-tag>
              </div>
              <div class="conv-preview">{{ conv.last_message_preview || '暂无消息' }}</div>
              <div class="conv-meta">
                <span class="platform">
                  <el-tag size="small" effect="plain">{{ conv.platform }}</el-tag>
                </span>
                <span class="time">{{ formatTime(conv.last_message_at) }}</span>
              </div>
              <el-badge
                v-if="conv.unread_count > 0"
                :value="conv.unread_count"
                class="unread-badge"
              />
            </div>
            <el-empty v-if="filteredConversations.length === 0" description="暂无会话" />
          </div>
        </el-card>
      </el-col>
      
      <!-- 聊天窗口 -->
      <el-col 
        :xs="24" 
        :sm="24" 
        :md="16" 
        :lg="16"
        class="chat-col"
        :class="{ 'mobile-full': isMobile && showChat, 'mobile-hidden': isMobile && !showChat }"
      >
        <div v-if="currentConversation" class="chat-window">
          <!-- 头部 -->
          <div class="chat-header">
            <div class="user-info">
              <el-avatar :size="40" :icon="UserFilled" />
              <div class="user-details">
                <div class="username">{{ currentConversation.platform_user_name }}</div>
                <div class="platform">{{ currentConversation.platform }} | {{ currentConversation.platform_user_id }}</div>
              </div>
            </div>
            <div class="actions">
              <el-button 
                type="warning" 
                size="small" 
                @click="handleHandoff"
                v-if="currentConversation.status === 'active'"
                :loading="handoffLoading"
              >
                <el-icon><Phone /></el-icon>
                <span class="btn-text">转人工</span>
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                @click="handleClose"
                v-if="currentConversation.status !== 'closed'"
                :loading="closeLoading"
              >
                <el-icon><CircleClose /></el-icon>
                <span class="btn-text">结束</span>
              </el-button>
            </div>
          </div>
          
          <!-- 消息列表 -->
          <div class="message-list" ref="messageListRef">
            <div
              v-for="msg in currentConversation.messages"
              :key="msg.id"
              class="message"
              :class="msg.direction"
            >
              <div class="message-content">
                <div class="message-sender" v-if="msg.sender_type === 'ai'">
                  <el-tag size="small" type="success">AI</el-tag>
                </div>
                <div class="message-sender" v-else-if="msg.sender_type === 'agent'">
                  <el-tag size="small" type="primary">客服</el-tag>
                </div>
                <div class="message-sender" v-else-if="msg.sender_type === 'system'">
                  <el-tag size="small" type="info">系统</el-tag>
                </div>
                <div class="message-bubble" :class="msg.sender_type">{{ msg.content }}</div>
                <div class="message-time">{{ formatTime(msg.created_at) }}</div>
              </div>
            </div>
          </div>
          
          <!-- 输入区 -->
          <div class="input-area" v-if="currentConversation.status !== 'closed'">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="isMobile ? 2 : 3"
              placeholder="输入消息... (Ctrl+Enter发送)"
              @keyup.ctrl.enter="sendMessage"
            />
            <div class="input-actions">
              <el-button type="primary" @click="sendMessage" :loading="sending" :disabled="!inputMessage.trim()">
                发送
              </el-button>
            </div>
          </div>
          
          <!-- 会话已结束提示 -->
          <div v-else class="closed-notice">
            <el-alert type="info" :closable="false">
              <template #title>
                <el-icon><InfoFilled /></el-icon> 会话已结束
              </template>
            </el-alert>
          </div>
        </div>
        
        <el-empty v-else description="选择一个会话开始聊天">
          <template #image>
            <el-icon :size="60" color="#909399"><ChatDotRound /></el-icon>
          </template>
        </el-empty>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { Search, UserFilled, Phone, CircleClose, InfoFilled, ChatDotRound, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useMockStore } from '@/stores/mock'
import dayjs from 'dayjs'

const mockStore = useMockStore()

const filterStatus = ref('active')
const searchQuery = ref('')
const currentConversation = ref<any>(null)
const inputMessage = ref('')
const sending = ref(false)
const handoffLoading = ref(false)
const closeLoading = ref(false)
const messageListRef = ref<HTMLElement>()
const isMobile = ref(false)
const showChat = ref(false)

// 检查屏幕尺寸
const checkScreenSize = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

const filteredConversations = computed(() => {
  return mockStore.conversations.filter(conv => {
    const matchStatus = conv.status === filterStatus.value
    const matchSearch = !searchQuery.value || 
      conv.platform_user_name.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchStatus && matchSearch
  })
})

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    active: 'success',
    pending_handoff: 'warning',
    closed: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    active: '进行中',
    pending_handoff: '待人工',
    closed: '已关闭'
  }
  return texts[status] || status
}

const formatTime = (time: string) => {
  if (!time) return ''
  return dayjs(time).format('HH:mm')
}

const selectConversation = (conv: any) => {
  currentConversation.value = conv
  showChat.value = true
  // 清除未读
  if (conv.unread_count > 0) {
    conv.unread_count = 0
  }
  scrollToBottom()
}

const backToList = () => {
  showChat.value = false
  currentConversation.value = null
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || !currentConversation.value) return
  
  sending.value = true
  try {
    await mockStore.sendMessage(
      currentConversation.value.id,
      inputMessage.value,
      'agent'
    )
    inputMessage.value = ''
    scrollToBottom()
  } finally {
    sending.value = false
  }
}

const handleHandoff = async () => {
  if (!currentConversation.value) return
  
  handoffLoading.value = true
  try {
    await mockStore.transferToHuman(currentConversation.value.id)
  } finally {
    handoffLoading.value = false
  }
}

const handleClose = async () => {
  if (!currentConversation.value) return
  
  closeLoading.value = true
  try {
    await mockStore.closeConversation(currentConversation.value.id)
  } finally {
    closeLoading.value = false
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// 监听消息变化自动滚动
watch(() => currentConversation.value?.messages?.length, () => {
  scrollToBottom()
})
</script>

<style scoped>
.conversations {
  padding: 20px;
  height: calc(100vh - 100px);
}

.conversation-row {
  height: 100%;
  margin: 0 !important;
}

.list-col, .chat-col {
  height: 100%;
  padding: 0 10px;
}

.list-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.mobile-back {
  margin-bottom: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-group {
  flex-wrap: wrap;
}

.search-input {
  margin-bottom: 10px;
}

.conversation-list {
  overflow-y: auto;
  flex: 1;
  max-height: calc(100% - 120px);
}

.conversation-item {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
}

.conversation-item:hover,
.conversation-item.active {
  background-color: #f5f7fa;
}

.conversation-item.has-unread {
  background-color: #f0f9ff;
}

.conv-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.username {
  font-weight: bold;
  font-size: 14px;
}

.conv-preview {
  color: #909399;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conv-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 12px;
  color: #c0c4cc;
}

.unread-badge {
  position: absolute;
  top: 12px;
  right: 12px;
}

/* 聊天窗口 */
.chat-window {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.chat-header {
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  .username {
    font-weight: bold;
    font-size: 16px;
  }
  .platform {
    color: #909399;
    font-size: 12px;
  }
}

.actions {
  display: flex;
  gap: 8px;
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
  
  &.in {
    justify-content: flex-start;
    .message-bubble {
      background: #fff;
      border: 1px solid #ebeef5;
    }
  }
  
  &.out {
    justify-content: flex-end;
    .message-content {
      align-items: flex-end;
    }
    .message-bubble {
      background: #409EFF;
      color: #fff;
    }
    .message-bubble.ai {
      background: #67C23A;
    }
    .message-bubble.system {
      background: #909399;
    }
  }
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.message-sender {
  margin-bottom: 4px;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 8px;
  word-break: break-word;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.input-area {
  padding: 16px;
  border-top: 1px solid #ebeef5;
  background: #fff;
}

.input-actions {
  margin-top: 8px;
  text-align: right;
}

.closed-notice {
  padding: 16px;
  border-top: 1px solid #ebeef5;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .conversations {
    padding: 10px;
    height: calc(100vh - 80px);
  }
  
  .list-col, .chat-col {
    padding: 0;
  }
  
  .mobile-hidden {
    display: none !important;
  }
  
  .mobile-full {
    position: fixed;
    top: 60px;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 100;
    background: #f0f2f5;
    padding: 10px;
    height: calc(100vh - 60px);
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-group {
    width: 100%;
    justify-content: flex-start;
  }
  
  .chat-header {
    padding: 10px;
  }
  
  .user-details .username {
    font-size: 14px;
  }
  
  .actions .btn-text {
    display: none;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .message-bubble {
    padding: 10px 12px;
    font-size: 14px;
  }
  
  .input-area {
    padding: 10px;
  }
}

/* 平板适配 */
@media screen and (min-width: 769px) and (max-width: 1024px) {
  .message-content {
    max-width: 75%;
  }
}
</style>
