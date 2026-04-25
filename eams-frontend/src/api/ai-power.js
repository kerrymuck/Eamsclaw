import request from '@/api/request'

// AI账户API
export const aiAccountApi = {
  // 获取账户信息
  getAccountInfo() {
    return request({
      url: '/v1/ai/account',
      method: 'get'
    })
  },

  // 获取用量统计
  getUsageStats(days = 30) {
    return request({
      url: '/v1/ai/usage',
      method: 'get',
      params: { days }
    })
  },

  // 获取用量明细
  getUsageDetails(params) {
    return request({
      url: '/v1/ai/usage/details',
      method: 'get',
      params
    })
  },

  // 获取可用模型列表
  getAvailableModels() {
    return request({
      url: '/v1/ai/models',
      method: 'get'
    })
  },

  // 获取交易记录
  getTransactions(params) {
    return request({
      url: '/v1/ai/transactions',
      method: 'get',
      params
    })
  },

  // 创建充值订单
  createRechargeOrder(data) {
    return request({
      url: '/v1/ai/recharge',
      method: 'post',
      data
    })
  },

  // AI聊天（带计费）
  chat(data) {
    return request({
      url: '/v1/ai/chat',
      method: 'post',
      data
    })
  }
}

export default aiAccountApi
