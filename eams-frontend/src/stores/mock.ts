import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

// 模拟数据
const MOCK_CONVERSATIONS = [
  {
    id: 'conv-1',
    platform_user_name: '买家小王',
    platform_user_id: 'TB123456',
    platform: '淘宝',
    status: 'active',
    last_message_preview: '这个商品什么时候发货？',
    last_message_at: new Date(Date.now() - 5 * 60000).toISOString(),
    unread_count: 2,
    messages: [
      {
        id: 'msg-1',
        direction: 'in',
        content: '这个商品什么时候发货？',
        created_at: new Date(Date.now() - 10 * 60000).toISOString(),
        sender_type: 'user'
      },
      {
        id: 'msg-2',
        direction: 'out',
        content: '亲，一般24小时内发货哦~',
        created_at: new Date(Date.now() - 8 * 60000).toISOString(),
        sender_type: 'ai'
      },
      {
        id: 'msg-3',
        direction: 'in',
        content: '好的，谢谢！',
        created_at: new Date(Date.now() - 5 * 60000).toISOString(),
        sender_type: 'user'
      }
    ]
  },
  {
    id: 'conv-2',
    platform_user_name: '买家李女士',
    platform_user_id: 'JD789012',
    platform: '京东',
    status: 'pending_handoff',
    last_message_preview: '我要投诉你们的服务！',
    last_message_at: new Date(Date.now() - 15 * 60000).toISOString(),
    unread_count: 1,
    messages: [
      {
        id: 'msg-4',
        direction: 'in',
        content: '我要投诉你们的服务！',
        created_at: new Date(Date.now() - 20 * 60000).toISOString(),
        sender_type: 'user'
      },
      {
        id: 'msg-5',
        direction: 'out',
        content: '非常抱歉给您带来不好的体验，我已经为您转接人工客服处理。',
        created_at: new Date(Date.now() - 18 * 60000).toISOString(),
        sender_type: 'ai'
      }
    ]
  },
  {
    id: 'conv-3',
    platform_user_name: '买家张先生',
    platform_user_id: 'PDD345678',
    platform: '拼多多',
    status: 'active',
    last_message_preview: '有优惠券吗？',
    last_message_at: new Date(Date.now() - 30 * 60000).toISOString(),
    unread_count: 0,
    messages: [
      {
        id: 'msg-6',
        direction: 'in',
        content: '有优惠券吗？',
        created_at: new Date(Date.now() - 35 * 60000).toISOString(),
        sender_type: 'user'
      },
      {
        id: 'msg-7',
        direction: 'out',
        content: '亲，新用户可以领取10元优惠券，点击下方链接领取哦~',
        created_at: new Date(Date.now() - 33 * 60000).toISOString(),
        sender_type: 'ai'
      }
    ]
  }
]

const MOCK_DASHBOARD = {
  total_conversations: 1234,
  resolved_conversations: 1100,
  active_conversations: 56,
  avg_response_time: '2.3s',
  satisfaction_score: 4.8,
  positive_feedback: 856,
  neutral_feedback: 120,
  negative_feedback: 24,
  hourly_stats: Array.from({ length: 24 }, (_, i) => ({
    hour: `${i}:00`,
    count: Math.floor(Math.random() * 50) + 10
  })),
  intent_distribution: [
    { name: '物流查询', value: 335 },
    { name: '商品咨询', value: 310 },
    { name: '价格优惠', value: 234 },
    { name: '退换货', value: 135 },
    { name: '其他', value: 148 }
  ],
  platform_distribution: [
    { name: '淘宝', value: 580 },
    { name: '京东', value: 384 },
    { name: '拼多多', value: 300 }
  ]
}

const MOCK_KNOWLEDGE_CATEGORIES = [
  {
    id: 'cat-1',
    name: '售前咨询',
    children: [
      { id: 'cat-1-1', name: '商品信息' },
      { id: 'cat-1-2', name: '价格优惠' }
    ]
  },
  {
    id: 'cat-2',
    name: '售后服务',
    children: [
      { id: 'cat-2-1', name: '退换货' },
      { id: 'cat-2-2', name: '物流查询' }
    ]
  },
  {
    id: 'cat-3',
    name: '常见问题',
    children: []
  }
]

const MOCK_KNOWLEDGE_ENTRIES = [
  {
    id: 'entry-1',
    question: '什么时候发货？',
    answer: '亲，一般24小时内发货，特殊商品可能需要48小时。您可以在订单详情中查看物流信息。',
    category_name: '物流查询',
    keywords: ['发货', '物流', '快递']
  },
  {
    id: 'entry-2',
    answer: '是的，我们支持7天无理由退换货。商品需保持原包装完好，不影响二次销售。',
    question: '支持7天无理由吗？',
    category_name: '退换货',
    keywords: ['退换货', '7天', '无理由']
  },
  {
    id: 'entry-3',
    question: '有优惠券吗？',
    answer: '亲，新用户可以领取10元优惠券，老用户关注店铺可领取5元优惠券。',
    category_name: '价格优惠',
    keywords: ['优惠券', '优惠', '折扣']
  }
]

export const useMockStore = defineStore('mock', () => {
  // State
  const conversations = ref(MOCK_CONVERSATIONS)
  const dashboard = ref(MOCK_DASHBOARD)
  const categories = ref(MOCK_KNOWLEDGE_CATEGORIES)
  const entries = ref(MOCK_KNOWLEDGE_ENTRIES)
  
  // Getters
  const activeConversations = computed(() => 
    conversations.value.filter(c => c.status === 'active')
  )
  
  const pendingHandoffConversations = computed(() => 
    conversations.value.filter(c => c.status === 'pending_handoff')
  )
  
  // Actions
  const getConversation = (id: string) => {
    return conversations.value.find(c => c.id === id)
  }
  
  const sendMessage = async (conversationId: string, content: string, senderType: 'ai' | 'agent' = 'agent') => {
    const conversation = getConversation(conversationId)
    if (!conversation) return
    
    const newMessage = {
      id: `msg-${Date.now()}`,
      direction: 'out',
      content,
      created_at: new Date().toISOString(),
      sender_type: senderType
    }
    
    conversation.messages.push(newMessage)
    conversation.last_message_preview = content
    conversation.last_message_at = newMessage.created_at
    
    // 模拟AI自动回复
    if (senderType === 'agent') {
      setTimeout(() => {
        const aiReply = generateAIReply(content)
        conversation.messages.push({
          id: `msg-${Date.now() + 1}`,
          direction: 'out',
          content: aiReply,
          created_at: new Date().toISOString(),
          sender_type: 'ai'
        })
        conversation.last_message_preview = aiReply
        conversation.last_message_at = new Date().toISOString()
        conversation.unread_count += 1
      }, 2000)
    }
    
    return newMessage
  }
  
  const transferToHuman = async (conversationId: string) => {
    const conversation = getConversation(conversationId)
    if (!conversation) return
    
    conversation.status = 'pending_handoff'
    
    // 添加系统消息
    conversation.messages.push({
      id: `msg-${Date.now()}`,
      direction: 'out',
      content: '已为您转接人工客服，请稍等...',
      created_at: new Date().toISOString(),
      sender_type: 'system'
    })
    
    ElMessage.success('已转人工')
  }
  
  const closeConversation = async (conversationId: string) => {
    const conversation = getConversation(conversationId)
    if (!conversation) return
    
    conversation.status = 'closed'
    
    conversation.messages.push({
      id: `msg-${Date.now()}`,
      direction: 'out',
      content: '会话已结束，感谢您的咨询！',
      created_at: new Date().toISOString(),
      sender_type: 'system'
    })
    
    ElMessage.success('会话已结束')
  }
  
  // AI回复生成（简单模拟）
  const generateAIReply = (userMessage: string): string => {
    const replies = [
      '亲，我已经收到您的问题，让我为您查询一下。',
      '好的，这个问题我可以帮您解决。',
      '亲，关于这个问题，您可以参考以下信息...',
      '了解了，让我为您提供详细的解答。',
      '亲，这个问题比较常见，我来为您解答。'
    ]
    return replies[Math.floor(Math.random() * replies.length)]
  }
  
  return {
    conversations,
    dashboard,
    categories,
    entries,
    activeConversations,
    pendingHandoffConversations,
    getConversation,
    sendMessage,
    transferToHuman,
    closeConversation
  }
})
