import request from './request'

export const knowledgeApi = {
  // 获取分类列表
  getCategories: () =>
    request.get('/knowledge/categories'),

  // 创建分类
  createCategory: (data: {
    name: string
    parent_id?: string
  }) => request.post('/knowledge/categories', data),

  // 更新分类
  updateCategory: (id: string, data: {
    name: string
  }) => request.put(`/knowledge/categories/${id}`, data),

  // 删除分类
  deleteCategory: (id: string) =>
    request.delete(`/knowledge/categories/${id}`),

  // 获取条目列表
  getEntries: (params?: {
    category_id?: string
    keyword?: string
    page?: number
    page_size?: number
  }) => request.get('/knowledge/entries', { params }),

  // 获取条目详情
  getEntry: (id: string) =>
    request.get(`/knowledge/entries/${id}`),

  // 创建条目
  createEntry: (data: {
    category_id: string
    question: string
    answer: string
    keywords?: string[]
    similar_questions?: string[]
  }) => request.post('/knowledge/entries', data),

  // 更新条目
  updateEntry: (id: string, data: {
    category_id?: string
    question?: string
    answer?: string
    keywords?: string[]
    similar_questions?: string[]
  }) => request.put(`/knowledge/entries/${id}`, data),

  // 删除条目
  deleteEntry: (id: string) =>
    request.delete(`/knowledge/entries/${id}`),

  // 搜索知识库
  search: (params: {
    q: string
    limit?: number
  }) => request.get('/knowledge/search', { params })
}
