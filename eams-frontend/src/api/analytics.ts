import request from './request'

export const analyticsApi = {
  // 获取仪表盘数据
  getDashboard: () =>
    request.get('/analytics/dashboard'),

  // 获取日报
  getDailyReport: (params?: {
    start_date?: string
    end_date?: string
  }) => request.get('/analytics/daily', { params }),

  // 获取小时报
  getHourlyReport: (params?: {
    date?: string
  }) => request.get('/analytics/hourly', { params }),

  // 获取意图分布
  getIntentDistribution: (params?: {
    start_date?: string
    end_date?: string
  }) => request.get('/analytics/intents', { params }),

  // 获取客服绩效
  getAgentPerformance: (params?: {
    start_date?: string
    end_date?: string
  }) => request.get('/analytics/agents', { params })
}
