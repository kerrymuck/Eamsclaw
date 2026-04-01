<template>
  <div class="chat-page">
    <el-card class="chat-card">
      <div class="chat-layout">
        <!-- 会话列表 -->
        <div class="conversation-list" :class="{ collapsed: !showList && isMobile }">
          <div class="list-header">
            <el-input
              v-model="searchQuery"
              placeholder="搜索会话..."
              :prefix-icon="Search"
              clearable
              size="small"
            />
            <el-radio-group v-model="filterStatus" size="small">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="unread">未读</el-radio-button>
            </el-radio-group>
          </div>
          
          <div class="list-content">
            <div
              v-for="conv in filteredConversations"
              :key="conv.id"
              :class="['conv-item', { active: currentConv?.id === conv.id, unread: conv.unread }]"
              @click="selectConv(conv)"
            >
              <el-badge :value="conv.unread" :hidden="!conv.unread">
                <el-avatar :size="40" :src="conv.avatar" />
              </el-badge>
              <div class="conv-info">
                <div class="conv-header">
                  <span class="buyer-name">{{ conv.buyer }}</span>
                  <span class="conv-time">{{ conv.time }}</span>
                </div>
                <div class="conv-preview">{{ conv.lastMessage }}</div>
                <div class="conv-tags">
                  <el-tag size="small" :type="getPlatformType(conv.platform)">{{ conv.platform }}</el-tag>
                  <el-tag v-if="conv.isAI" size="small" type="info">AI接待</el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 聊天窗口 -->
        <div class="chat-window" v-if="currentConv || !isMobile">
          <div v-if="!currentConv" class="empty-chat">
            <el-icon :size="64" color="#ddd"><ChatDotRound /></el-icon>
            <p>选择一个会话开始聊天</p>
          </div>
          
          <template v-else>
            <!-- 聊天头部 -->
            <div class="chat-header">
              <div class="header-left">
                <el-button v-if="isMobile" :icon="ArrowLeft" link @click="showList = true" />
                <el-avatar :size="36" :src="currentConv.avatar" />
                <div class="header-info">
                  <span class="buyer-name">{{ currentConv.buyer }}</span>
                  <el-tag size="small" :type="getPlatformType(currentConv.platform)">
                    {{ currentConv.platform }}
                  </el-tag>
                </div>
              </div>
              <div class="header-actions">
                <el-button :icon="User" link>转人工</el-button>
                <el-button :icon="Document" link>查看订单</el-button>
                <el-dropdown>
                  <el-button :icon="More" link />
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item>标记为待跟进</el-dropdown-item>
                      <el-dropdown-item>加入黑名单</el-dropdown-item>
                      <el-dropdown-item divided>结束会话</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>

            <!-- 消息列表 -->
            <div class="message-list" ref="messageListRef">
              <div v-for="msg in messages" :key="msg.id" :class="['message', msg.type]">
                <div class="message-content">
                  <div v-if="msg.type === 'buyer'" class="avatar">
                    <el-avatar :size="32" :src="currentConv.avatar" />
                  </div>
                  <div class="message-body">
                    <div class="message-bubble">{{ msg.content }}</div>
                    <div class="message-time">{{ msg.time }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 快捷回复 -->
            <div class="quick-replies" v-if="quickReplies.length > 0">
              <el-scrollbar>
                <div class="quick-list">
                  <el-tag
                    v-for="reply in quickReplies"
                    :key="reply"
                    class="quick-tag"
                    @click="useQuickReply(reply)"
                  >
                    {{ reply }}
                  </el-tag>
                </div>
              </el-scrollbar>
            </div>

            <!-- 输入区域 -->
            <div class="input-area">
              <div class="input-toolbar">
                <el-button :icon="Picture" link />
                <el-button :icon="Folder" link />
                <el-button :icon="Collection" link @click="showKnowledge = true">知识库</el-button>
              </div>
              <div class="input-box">
                <el-input
                  v-model="inputMessage"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入消息..."
                  @keydown.enter.prevent="sendMessage"
                />
                <div class="input-actions">
                  <el-button type="primary" @click="sendMessage" :disabled="!inputMessage.trim()">
                    发送
                  </el-button>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </el-card>

    <!-- 知识库弹窗 -->
    <el-dialog v-model="showKnowledge" title="知识库" width="600px">
      <el-input
        v-model="knowledgeSearch"
        placeholder="搜索知识库..."
        :prefix-icon="Search"
        clearable
      />
      <el-tree
        :data="knowledgeTree"
        :props="{ label: 'title', children: 'children' }"
        @node-click="useKnowledge"
        style="margin-top: 16px; max-height: 400px; overflow-y: auto;"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import {
  Search, ChatDotRound, ArrowLeft, User, Document, More,
  Picture, Folder, Collection
} from '@element-plus/icons-vue'

const searchQuery = ref('')
const filterStatus = ref('all')
const currentConv = ref<any>(null)
const inputMessage = ref('')
const messageListRef = ref<HTMLElement>()
const showList = ref(true)
const isMobile = ref(window.innerWidth < 768)
const showKnowledge = ref(false)
const knowledgeSearch = ref('')

const conversations = ref([
  { id: 1, buyer: '张先生', avatar: '', platform: '淘宝', lastMessage: '这个商品有优惠吗？', time: '2分钟前', unread: 2, isAI: false },
  { id: 2, buyer: '李女士', avatar: '', platform: '京东', lastMessage: '什么时候发货？', time: '5分钟前', unread: 1, isAI: true },
  { id: 3, buyer: '王先生', avatar: '', platform: '拼多多', lastMessage: '申请退款怎么操作？', time: '8分钟前', unread: 0, isAI: false },
  { id: 4, buyer: '赵女士', avatar: '', platform: '淘宝', lastMessage: '可以开发票吗？', time: '12分钟前', unread: 0, isAI: true },
  { id: 5, buyer: '陈先生', avatar: '', platform: '京东', lastMessage: '质量问题怎么处理？', time: '20分钟前', unread: 0, isAI: false }
])

const messages = ref([
  { id: 1, type: 'buyer', content: '你好，请问这个商品有优惠吗？', time: '14:30' },
  { id: 2, type: 'ai', content: '您好！目前该商品正在参与满减活动，满299减30，满599减80。', time: '14:30' },
  { id: 3, type: 'buyer', content: '那我再看看其他商品一起买', time: '14:32' },
  { id: 4, type: 'buyer', content: '这个有现货吗？', time: '14:35' }
])

const quickReplies = ref([
  '您好，请问有什么可以帮您？',
  '亲，这款商品有现货的',
  '满99元包邮哦',
  '支持7天无理由退换货',
  '下午4点前下单当天发货'
])

const knowledgeTree = ref([
  {
    title: '售前咨询',
    children: [
      { title: '商品是否有货？', content: '亲，这款商品有现货，下单后24小时内发货。' },
      { title: '有什么优惠活动？', content: '目前店铺满299减30，满599减80，还有新人首单立减20元。' },
      { title: '发什么快递？', content: '默认发中通快递，如需顺丰请联系客服补差价。' }
    ]
  },
  {
    title: '售后服务',
    children: [
      { title: '如何申请退款？', content: '在"我的订单"中找到对应订单，点击"申请售后"即可。' },
      { title: '退换货流程', content: '支持7天无理由退换货，请保持商品完好并联系客服获取退货地址。' },
      { title: '质量问题处理', content: '如收到商品有质量问题，请提供照片联系客服，我们包退包换。' }
    ]
  }
])

const filteredConversations = computed(() => {
  let result = conversations.value
  if (searchQuery.value) {
    result = result.filter(c => c.buyer.includes(searchQuery.value) || c.lastMessage.includes(searchQuery.value))
  }
  if (filterStatus.value === 'unread') {
    result = result.filter(c => c.unread > 0)
  }
  return result
})

const getPlatformType = (platform: string) => {
  const map: Record<string, string> = { '淘宝': 'danger', '京东': 'danger', '拼多多': 'success' }
  return map[platform] || 'info'
}

const selectConv = (conv: any) => {
  currentConv.value = conv
  conv.unread = 0
  if (isMobile.value) {
    showList.value = false
  }
  scrollToBottom()
}

const sendMessage = () => {
  const text = inputMessage.value.trim()
  if (!text) return
  
  messages.value.push({
    id: Date.now(),
    type: 'merchant',
    content: text,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  })
  
  inputMessage.value = ''
  scrollToBottom()
}

const useQuickReply = (reply: string) => {
  inputMessage.value = reply
}

const useKnowledge = (data: any) => {
  if (data.content) {
    inputMessage.value = data.content
    showKnowledge.value = false
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 140px);
}

.chat-card {
  height: 100%;
}

.chat-card :deep(.el-card__body) {
  height: 100%;
  padding: 0;
}

.chat-layout {
  display: flex;
  height: 100%;
}

/* 会话列表 */
.conversation-list {
  width: 320px;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.conversation-list.collapsed {
  display: none;
}

.list-header {
  padding: 12px;
  border-bottom: 1px solid #e8e8e8;
}

.list-header .el-input {
  margin-bottom: 8px;
}

.list-content {
  flex: 1;
  overflow-y: auto;
}

.conv-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #f0f0f0;
}

.conv-item:hover {
  background: #f0f0f0;
}

.conv-item.active {
  background: #e6f7ff;
}

.conv-item.unread .buyer-name {
  font-weight: 600;
}

.conv-info {
  flex: 1;
  margin-left: 12px;
  min-width: 0;
}

.conv-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.buyer-name {
  font-size: 14px;
  color: #333;
}

.conv-time {
  font-size: 12px;
  color: #999;
}

.conv-preview {
  font-size: 13px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.conv-tags {
  display: flex;
  gap: 4px;
}

/* 聊天窗口 */
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #e8e8e8;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f5f5;
}

.message {
  margin-bottom: 16px;
}

.message-content {
  display: flex;
  gap: 8px;
}

.message.merchant .message-content {
  flex-direction: row-reverse;
}

.message-body {
  max-width: 70%;
}

.message-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  background: #fff;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}

.message.merchant .message-bubble {
  background: #1677ff;
  color: #fff;
}

.message.ai .message-bubble {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}

/* 快捷回复 */
.quick-replies {
  padding: 8px 16px;
  border-top: 1px solid #e8e8e8;
  background: #fff;
}

.quick-list {
  display: flex;
  gap: 8px;
  white-space: nowrap;
}

.quick-tag {
  cursor: pointer;
}

.quick-tag:hover {
  background: #e6f7ff;
  border-color: #1677ff;
  color: #1677ff;
}

/* 输入区域 */
.input-area {
  padding: 12px 16px;
  border-top: 1px solid #e8e8e8;
  background: #fff;
}

.input-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.input-box {
  display: flex;
  gap: 12px;
}

.input-box .el-textarea {
  flex: 1;
}

.input-actions {
  display: flex;
  align-items: flex-end;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .chat-page {
    height: calc(100vh - 100px);
  }
  
  .conversation-list {
    width: 100%;
    border-right: none;
  }
  
  .chat-window {
    width: 100%;
  }
  
  .message-body {
    max-width: 80%;
  }
  
  .header-actions {
    display: none;
  }
}
</style>
