import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

// WebSocket连接状态
export enum ConnectionStatus {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

// WebSocket消息类型
export enum MessageType {
  // 系统消息
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  ERROR = 'error',
  PING = 'ping',
  PONG = 'pong',
  
  // 业务消息
  NEW_MESSAGE = 'new_message',
  MESSAGE_SENT = 'message_sent',
  CONVERSATION_ASSIGNED = 'conversation_assigned',
  CONVERSATION_CLOSED = 'conversation_closed',
  TYPING = 'typing',
  CUSTOMER_STATUS = 'customer_status',
  ORDER_UPDATE = 'order_update',
  AI_SUGGESTION = 'ai_suggestion',
  
  // 订阅消息
  SUBSCRIBED = 'subscribed',
  UNSUBSCRIBED = 'unsubscribed'
}

// WebSocket消息接口
export interface WSMessage {
  type: MessageType | string
  data: any
  timestamp?: string
}

// WebSocket配置
interface WSConfig {
  url: string
  token: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
}

class WebSocketService {
  private ws: WebSocket | null = null
  private config: WSConfig
  private reconnectAttempts = 0
  private heartbeatTimer: NodeJS.Timeout | null = null
  private reconnectTimer: NodeJS.Timeout | null = null
  private messageHandlers: Map<string, Set<(data: any) => void>> = new Map()
  
  // 响应式状态
  public status = ref<ConnectionStatus>(ConnectionStatus.DISCONNECTED)
  public isConnected = computed(() => this.status.value === ConnectionStatus.CONNECTED)
  
  constructor(config: WSConfig) {
    this.config = {
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
      heartbeatInterval: 30000,
      ...config
    }
  }
  
  // 连接WebSocket
  public connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected')
      return
    }
    
    this.status.value = ConnectionStatus.CONNECTING
    
    try {
      const wsUrl = `${this.config.url}?token=${this.config.token}`
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = this.handleOpen.bind(this)
      this.ws.onmessage = this.handleMessage.bind(this)
      this.ws.onclose = this.handleClose.bind(this)
      this.ws.onerror = this.handleError.bind(this)
    } catch (error) {
      console.error('WebSocket connection error:', error)
      this.status.value = ConnectionStatus.ERROR
      this.scheduleReconnect()
    }
  }
  
  // 断开连接
  public disconnect(): void {
    this.clearTimers()
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    this.status.value = ConnectionStatus.DISCONNECTED
    this.reconnectAttempts = 0
  }
  
  // 发送消息
  public send(type: string, data: any): boolean {
    if (!this.isConnected.value) {
      console.warn('WebSocket not connected')
      return false
    }
    
    try {
      const message: WSMessage = {
        type,
        data,
        timestamp: new Date().toISOString()
      }
      
      this.ws!.send(JSON.stringify(message))
      return true
    } catch (error) {
      console.error('Send message error:', error)
      return false
    }
  }
  
  // 订阅会话消息
  public subscribeConversation(conversationId: string): void {
    this.send('subscribe_conversation', { conversation_id: conversationId })
  }
  
  // 取消订阅会话
  public unsubscribeConversation(conversationId: string): void {
    this.send('unsubscribe_conversation', { conversation_id: conversationId })
  }
  
  // 发送消息到会话
  public sendMessage(conversationId: string, content: string, messageType = 'text'): void {
    this.send('send_message', {
      conversation_id: conversationId,
      content,
      message_type: messageType
    })
  }
  
  // 发送正在输入状态
  public sendTyping(conversationId: string, isTyping: boolean): void {
    this.send('typing', {
      conversation_id: conversationId,
      is_typing: isTyping
    })
  }
  
  // 请求AI回复建议
  public requestAIReply(
    conversationId: string,
    customerMessage: string,
    platform: string,
    customerId: string
  ): void {
    this.send('ai_reply', {
      conversation_id: conversationId,
      message: customerMessage,
      platform,
      customer_id: customerId
    })
  }
  
  // 注册消息处理器
  public on(type: string, handler: (data: any) => void): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set())
    }
    
    this.messageHandlers.get(type)!.add(handler)
    
    // 返回取消订阅函数
    return () => {
      this.messageHandlers.get(type)?.delete(handler)
    }
  }
  
  // 处理连接打开
  private handleOpen(): void {
    console.log('WebSocket connected')
    this.status.value = ConnectionStatus.CONNECTED
    this.reconnectAttempts = 0
    
    // 启动心跳
    this.startHeartbeat()
    
    ElMessage.success('实时连接已建立')
  }
  
  // 处理消息
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WSMessage = JSON.parse(event.data)
      
      // 处理pong消息
      if (message.type === MessageType.PONG) {
        return
      }
      
      // 调用注册的处理器
      const handlers = this.messageHandlers.get(message.type)
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message.data)
          } catch (error) {
            console.error('Message handler error:', error)
          }
        })
      }
      
      // 处理特定消息类型
      this.handleSpecificMessage(message)
    } catch (error) {
      console.error('Parse message error:', error)
    }
  }
  
  // 处理特定消息类型
  private handleSpecificMessage(message: WSMessage): void {
    switch (message.type) {
      case MessageType.CONNECTED:
        console.log('Server confirmed connection:', message.data)
        break
        
      case MessageType.ERROR:
        console.error('Server error:', message.data)
        ElMessage.error(message.data?.message || '服务器错误')
        break
        
      case MessageType.NEW_MESSAGE:
        // 新消息通知，播放提示音
        this.playNotificationSound()
        break
        
      case MessageType.AI_SUGGESTION:
        // AI回复建议
        console.log('AI suggestion received:', message.data)
        break
    }
  }
  
  // 处理连接关闭
  private handleClose(event: CloseEvent): void {
    console.log('WebSocket closed:', event.code, event.reason)
    
    this.clearTimers()
    this.status.value = ConnectionStatus.DISCONNECTED
    
    // 非正常关闭，尝试重连
    if (event.code !== 1000 && event.code !== 1001) {
      this.scheduleReconnect()
    }
  }
  
  // 处理错误
  private handleError(error: Event): void {
    console.error('WebSocket error:', error)
    this.status.value = ConnectionStatus.ERROR
  }
  
  // 启动心跳
  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected.value) {
        this.send(MessageType.PING, { timestamp: Date.now() })
      }
    }, this.config.heartbeatInterval)
  }
  
  // 安排重连
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts!) {
      console.error('Max reconnect attempts reached')
      ElMessage.error('连接失败，请刷新页面重试')
      return
    }
    
    this.status.value = ConnectionStatus.RECONNECTING
    this.reconnectAttempts++
    
    console.log(`Reconnecting... attempt ${this.reconnectAttempts}`)
    
    this.reconnectTimer = setTimeout(() => {
      this.connect()
    }, this.config.reconnectInterval)
  }
  
  // 清除定时器
  private clearTimers(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }
  
  // 播放通知声音
  private playNotificationSound(): void {
    // 检查用户是否开启了声音
    const soundEnabled = localStorage.getItem('notification_sound') !== 'false'
    if (!soundEnabled) return
    
    try {
      const audio = new Audio('/sounds/notification.mp3')
      audio.volume = 0.5
      audio.play().catch(() => {
        // 自动播放被阻止，忽略错误
      })
    } catch (error) {
      console.error('Play sound error:', error)
    }
  }
}

// 全局WebSocket服务实例
let wsService: WebSocketService | null = null

// 初始化WebSocket服务
export function initWebSocketService(token: string): WebSocketService {
  const wsUrl = import.meta.env.VITE_WS_URL || 'wss://your-api.com/ws/chat'
  
  wsService = new WebSocketService({
    url: wsUrl,
    token
  })
  
  return wsService
}

// 获取WebSocket服务实例
export function getWebSocketService(): WebSocketService | null {
  return wsService
}

// Vue组合式函数
export function useWebSocket() {
  const service = getWebSocketService()
  
  if (!service) {
    console.warn('WebSocket service not initialized')
    return {
      status: ref(ConnectionStatus.DISCONNECTED),
      isConnected: ref(false),
      connect: () => {},
      disconnect: () => {},
      send: () => false,
      subscribeConversation: () => {},
      unsubscribeConversation: () => {},
      sendMessage: () => {},
      sendTyping: () => {},
      requestAIReply: () => {},
      on: () => () => {}
    }
  }
  
  return {
    status: service.status,
    isConnected: service.isConnected,
    connect: service.connect.bind(service),
    disconnect: service.disconnect.bind(service),
    send: service.send.bind(service),
    subscribeConversation: service.subscribeConversation.bind(service),
    unsubscribeConversation: service.unsubscribeConversation.bind(service),
    sendMessage: service.sendMessage.bind(service),
    sendTyping: service.sendTyping.bind(service),
    requestAIReply: service.requestAIReply.bind(service),
    on: service.on.bind(service)
  }
}

export default WebSocketService
