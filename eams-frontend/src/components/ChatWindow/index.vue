<template>
  <div class="chat-window">
    <!-- 头部 -->
    <div class="chat-header">
      <div class="user-info">
        <el-avatar :size="40" :icon="UserFilled" />
        <div class="user-details">
          <div class="username">{{ conversation.platform_user_name }}</div>
          <div class="platform">{{ conversation.platform }} | {{ conversation.platform_user_id }}</div>
        </div>
      </div>
      <div class="actions">
        <el-button type="warning" size="small" @click="$emit('handoff')" v-if="conversation.status === 'active'">
          转人工
        </el-button>
        <el-button type="danger" size="small" @click="$emit('close')" v-if="conversation.status !== 'closed'">
          结束会话
        </el-button>
      </div>
    </div>
    
    <!-- 消息列表 -->
    <div class="message-list" ref="messageListRef" v-loading="loading">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="message"
        :class="msg.direction"
      >
        <div class="message-content">
          <div class="message-bubble">{{ msg.content }}</div>
          <div class="message-time">{{ formatTime(msg.created_at) }}</div>
        </div>
      </div>
      <el-empty v-if="messages.length === 0" description="暂无消息" />
    </div>
    
    <!-- 输入区 -->
    <div class="input-area" v-if="conversation.status !== 'closed'">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        placeholder="输入消息..."
        @keyup.enter.ctrl="sendMessage"
      />
      <div class="input-actions">
        <el-button type="primary" @click="sendMessage" :disabled="!inputMessage.trim()">
          发送 (Ctrl+Enter)
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, watch } from 'vue'
import { UserFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { dialogApi } from '@/api/dialog'
import dayjs from 'dayjs'

const props = defineProps<{
  conversation: any
}>()

const emit = defineEmits(['send', 'handoff', 'close'])

const inputMessage = ref('')
const messageListRef = ref<HTMLElement>()
const messages = ref<any[]>([])
const loading = ref(false)

const loadMessages = async () => {
  if (!props.conversation) return
  loading.value = true
  try {
    const res: any = await dialogApi.getMessages(props.conversation.id)
    if (res.code === 1) {
      messages.value = res.data.items || []
      scrollToBottom()
    }
  } catch (error) {
    ElMessage.error('加载消息失败')
  } finally {
    loading.value = false
  }
}

const formatTime = (time: string) => {
  if (!time) return ''
  return dayjs(time).format('HH:mm')
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  
  const content = inputMessage.value
  emit('send', content)
  
  // 本地添加消息
  messages.value.push({
    id: Date.now().toString(),
    content: content,
    direction: 'out',
    created_at: new Date().toISOString()
  })
  
  inputMessage.value = ''
  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    messageListRef.value?.scrollTo(0, messageListRef.value.scrollHeight)
  })
}

// 监听会话变化
watch(() => props.conversation, (newVal) => {
  if (newVal) {
    loadMessages()
  }
}, { immediate: true })

onMounted(() => {
  loadMessages()
})
</script>

<style scoped>
.chat-window {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 4px;
}

.chat-header {
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
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
    .message-bubble {
      background: #409EFF;
      color: #fff;
    }
  }
}

.message-content {
  max-width: 70%;
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
  text-align: right;
}

.input-area {
  padding: 16px;
  border-top: 1px solid #ebeef5;
}

.input-actions {
  margin-top: 8px;
  text-align: right;
}
</style>
