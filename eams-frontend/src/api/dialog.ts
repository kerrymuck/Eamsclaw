import request from './request'

export const dialogApi = {
  // 获取对话列表
  getConversations: (params?: {
    status?: string
    platform?: string
    assigned_to?: string
    page?: number
    page_size?: number
  }) => request.get('/conversations', { params }),

  // 获取对话详情
  getConversation: (id: string) =>
    request.get(`/conversations/${id}`),

  // 获取对话消息
  getMessages: (conversationId: string, params?: {
    page?: number
    page_size?: number
  }) => request.get(`/conversations/${conversationId}/messages`, { params }),

  // 发送消息
  sendMessage: (conversationId: string, data: {
    content: string
    type?: 'text' | 'image'
  }) => request.post(`/conversations/${conversationId}/messages`, data),

  // 分配对话
  assignConversation: (id: string, data: {
    assigned_to: string
  }) => request.post(`/conversations/${id}/assign`, data),

  // 关闭对话
  closeConversation: (id: string) =>
    request.post(`/conversations/${id}/close`),

  // 转人工
  transferToHuman: (id: string, data?: {
    reason?: string
  }) => request.post(`/conversations/${id}/transfer`, data),

  // 添加标签
  addTag: (id: string, data: {
    tag: string
  }) => request.post(`/conversations/${id}/tags`, data),

  // 移除标签
  removeTag: (id: string, tag: string) =>
    request.delete(`/conversations/${id}/tags/${tag}`)
}
