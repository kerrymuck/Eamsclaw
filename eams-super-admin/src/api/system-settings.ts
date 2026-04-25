import request from '@/api/request'

export const systemSettingsApi = {
  // 获取所有设置
  getSettings(group?: string) {
    return request({
      url: '/admin/settings',
      method: 'get',
      params: { group }
    })
  },

  // 获取单个设置
  getSetting(key: string) {
    return request({
      url: `/admin/settings/${key}`,
      method: 'get'
    })
  },

  // 保存设置
  saveSetting(data: {
    key: string
    value: string
    group?: string
    description?: string
    is_encrypted?: boolean
  }) {
    return request({
      url: '/admin/settings',
      method: 'post',
      data
    })
  },

  // 批量保存设置
  batchSaveSettings(settings: Record<string, string>, group: string = 'general') {
    return request({
      url: '/admin/settings/batch',
      method: 'post',
      data: { settings, group }
    })
  },

  // 获取分组设置
  getSettingsByGroup(group: string) {
    return request({
      url: `/admin/settings/group/${group}`,
      method: 'get'
    })
  },

  // 删除设置
  deleteSetting(key: string) {
    return request({
      url: `/admin/settings/${key}`,
      method: 'delete'
    })
  }
}