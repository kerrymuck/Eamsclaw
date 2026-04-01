<template>
  <div class="platform-settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <div>
            <span>🔌 平台对接设置</span>
            <span style="color: #909399; font-size: 14px; margin-left: 10px">
              配置各电商平台的API连接和授权
            </span>
          </div>
          <el-button type="primary" @click="showAddPlatform = true">
            <el-icon><Plus /></el-icon> 添加平台
          </el-button>
        </div>
      </template>
      
      <!-- 平台列表 -->
      <el-table :data="platformAuths" v-loading="loading" stripe>
        <el-table-column label="平台" width="150">
          <template #default="{ row }">
            <div class="platform-info">
              <span class="platform-icon">{{ row.platform_icon }}</span>
              <span>{{ row.platform_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="店铺信息" min-width="200">
          <template #default="{ row }">
            <div class="shop-info">
              <el-avatar :size="32" :src="row.platform_shop_logo" v-if="row.platform_shop_logo">
                {{ row.platform_shop_name?.charAt(0) }}
              </el-avatar>
              <div class="shop-detail">
                <div class="shop-name">{{ row.platform_shop_name || '-' }}</div>
                <div class="shop-id">ID: {{ row.platform_shop_id }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="授权状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.auth_status)">
              {{ getStatusText(row.auth_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="授权时间" width="180">
          <template #default="{ row }">
            <span v-if="row.authorized_at">
              {{ formatDate(row.authorized_at) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="过期时间" width="180">
          <template #default="{ row }">
            <div v-if="row.expires_at">
              <span :class="{ 'text-danger': isExpiringSoon(row.expires_at) }">
                {{ formatDate(row.expires_at) }}
              </span>
              <el-tag v-if="isExpiringSoon(row.expires_at)" type="danger" size="small" style="margin-left: 5px">
                即将过期
              </el-tag>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.auth_status === 'pending' || row.auth_status === 'expired'"
              type="primary" 
              link 
              @click="handleAuth(row)"
            >
              <el-icon><Link /></el-icon> 去授权
            </el-button>
            <el-button 
              v-if="row.auth_status === 'authorized'"
              type="primary" 
              link 
              @click="refreshToken(row)"
            >
              <el-icon><Refresh /></el-icon> 刷新令牌
            </el-button>
            <el-button type="primary" link @click="editConfig(row)">
              <el-icon><Setting /></el-icon> 配置
            </el-button>
            <el-button type="danger" link @click="revokeAuth(row)">
              <el-icon><CircleClose /></el-icon> 撤销
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加平台对话框 -->
    <el-dialog v-model="showAddPlatform" title="添加平台对接" width="600px">
      <el-steps :active="addStep" finish-status="success" simple style="margin-bottom: 20px">
        <el-step title="选择平台" />
        <el-step title="配置API" />
        <el-step title="授权" />
      </el-steps>
      
      <!-- 步骤1：选择平台 -->
      <div v-if="addStep === 0">
        <el-form label-width="100px">
          <el-form-item label="选择平台">
            <el-select v-model="newPlatform.platform_type" placeholder="请选择平台" style="width: 100%">
              <el-option-group label="国内电商">
                <el-option 
                  v-for="p in domesticPlatforms" 
                  :key="p.id" 
                  :label="p.icon + ' ' + p.name" 
                  :value="p.id"
                />
              </el-option-group>
              <el-option-group label="跨境电商">
                <el-option 
                  v-for="p in crossborderPlatforms" 
                  :key="p.id" 
                  :label="p.icon + ' ' + p.name" 
                  :value="p.id"
                />
              </el-option-group>
            </el-select>
          </el-form-item>
        </el-form>
        <div class="platform-preview" v-if="selectedPlatformInfo">
          <el-card>
            <div class="preview-header">
              <span class="preview-icon">{{ selectedPlatformInfo.icon }}</span>
              <span class="preview-name">{{ selectedPlatformInfo.name }}</span>
            </div>
            <div class="preview-desc">{{ selectedPlatformInfo.description }}</div>
            <div class="preview-features">
              <el-tag v-for="feature in selectedPlatformInfo.features" :key="feature" size="small">
                {{ feature }}
              </el-tag>
            </div>
          </el-card>
        </div>
      </div>
      
      <!-- 步骤2：配置API -->
      <div v-if="addStep === 1">
        <el-alert
          title="API配置说明"
          description="请前往对应平台的开放平台获取AppKey和AppSecret。这些信息将用于调用平台API。"
          type="info"
          show-icon
          :closable="false"
          style="margin-bottom: 20px"
        />
        <el-form :model="apiConfigForm" label-width="120px">
          <el-form-item label="AppKey">
            <el-input v-model="apiConfigForm.app_key" placeholder="请输入AppKey" />
          </el-form-item>
          <el-form-item label="AppSecret">
            <el-input 
              v-model="apiConfigForm.app_secret" 
              type="password" 
              placeholder="请输入AppSecret"
              show-password
            />
          </el-form-item>
          <el-form-item label="API地址">
            <el-input v-model="apiConfigForm.api_base_url" placeholder="https://..." />
          </el-form-item>
          <el-form-item label="授权回调地址">
            <el-input v-model="apiConfigForm.callback_url" placeholder="https://your-app.com/callback" />
            <div class="form-tip">需要在平台开放平台配置此回调地址</div>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 步骤3：授权 -->
      <div v-if="addStep === 2">
        <div class="auth-guide">
          <el-result
            icon="info"
            title="即将跳转到平台授权页面"
            sub-title="点击确定后将跳转到平台授权页面，请使用店铺主账号登录并授权"
          >
            <template #extra>
              <div class="auth-steps">
                <div class="auth-step">
                  <el-icon><CircleCheck /></el-icon>
                  <span>1. 使用店铺主账号登录</span>
                </div>
                <div class="auth-step">
                  <el-icon><CircleCheck /></el-icon>
                  <span>2. 确认授权范围</span>
                </div>
                <div class="auth-step">
                  <el-icon><CircleCheck /></el-icon>
                  <span>3. 完成授权返回</span>
                </div>
              </div>
            </template>
          </el-result>
        </div>
      </div>
      
      <template #footer>
        <el-button v-if="addStep > 0" @click="addStep--">上一步</el-button>
        <el-button v-if="addStep < 2" type="primary" @click="nextStep">下一步</el-button>
        <el-button v-if="addStep === 2" type="primary" @click="startAuth">确定授权</el-button>
      </template>
    </el-dialog>
    
    <!-- 配置详情对话框 -->
    <el-dialog v-model="showConfigDetail" title="平台配置详情" width="700px">
      <el-tabs v-model="activeConfigTab">
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="configDetail" label-width="120px">
            <el-form-item label="平台">
              <span>{{ configDetail.platform_name }}</span>
            </el-form-item>
            <el-form-item label="平台店铺ID">
              <el-input v-model="configDetail.platform_shop_id" disabled />
            </el-form-item>
            <el-form-item label="店铺名称">
              <el-input v-model="configDetail.platform_shop_name" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="API配置" name="api">
          <el-form :model="configDetail.api_config" label-width="120px">
            <el-form-item label="AppKey">
              <el-input v-model="configDetail.api_config.app_key" />
            </el-form-item>
            <el-form-item label="AppSecret">
              <el-input v-model="configDetail.api_config.app_secret" type="password" show-password />
            </el-form-item>
            <el-form-item label="API地址">
              <el-input v-model="configDetail.api_config.api_base_url" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="同步设置" name="sync">
          <el-form label-width="150px">
            <el-form-item label="自动同步消息">
              <el-switch v-model="configDetail.sync_config.auto_sync_messages" />
            </el-form-item>
            <el-form-item label="自动同步订单">
              <el-switch v-model="configDetail.sync_config.auto_sync_orders" />
            </el-form-item>
            <el-form-item label="同步间隔（分钟）">
              <el-slider v-model="configDetail.sync_config.sync_interval_minutes" :min="1" :max="60" show-stops />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="Webhook" name="webhook">
          <el-form label-width="120px">
            <el-form-item label="Webhook地址">
              <el-input :value="webhookUrl" readonly>
                <template #append>
                  <el-button @click="copyWebhookUrl">
                    <el-icon><CopyDocument /></el-icon>
                  </el-button>
                </template>
              </el-input>
              <div class="form-tip">将此地址配置到平台开放平台的消息推送设置中</div>
            </el-form-item>
            <el-form-item label="订阅事件">
              <el-checkbox-group v-model="configDetail.webhook_config.subscribed_events">
                <el-checkbox label="message">消息通知</el-checkbox>
                <el-checkbox label="order">订单变更</el-checkbox>
                <el-checkbox label="logistics">物流更新</el-checkbox>
                <el-checkbox label="refund">退款售后</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="showConfigDetail = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Plus, Link, Refresh, Setting, CircleClose, CircleCheck, CopyDocument } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllPlatforms } from '@/config/platforms'
import { useMockStore } from '@/stores/mock'

const mockStore = useMockStore()
const loading = ref(false)
const showAddPlatform = ref(false)
const showConfigDetail = ref(false)
const addStep = ref(0)
const activeConfigTab = ref('basic')

// 平台列表
const allPlatforms = getAllPlatforms()
const domesticPlatforms = computed(() => allPlatforms.filter(p => p.category === 'domestic'))
const crossborderPlatforms = computed(() => allPlatforms.filter(p => p.category === 'crossborder'))

// 新平台配置
const newPlatform = ref({
  platform_type: ''
})

const selectedPlatformInfo = computed(() => {
  return allPlatforms.find(p => p.id === newPlatform.value.platform_type)
})

// API配置表单
const apiConfigForm = ref({
  app_key: '',
  app_secret: '',
  api_base_url: '',
  callback_url: ''
})

// 平台授权列表（模拟数据）
const platformAuths = ref([
  {
    id: '1',
    platform_type: 'taobao',
    platform_name: '淘宝',
    platform_icon: '🛒',
    platform_shop_id: 'TB123456',
    platform_shop_name: '示例淘宝店',
    platform_shop_logo: '',
    auth_status: 'authorized',
    authorized_at: '2024-03-20T10:00:00',
    expires_at: '2024-04-20T10:00:00',
    api_config: {
      app_key: 'mock_app_key',
      app_secret: 'mock_app_secret',
      api_base_url: 'https://eco.taobao.com/router/rest'
    },
    sync_config: {
      auto_sync_messages: true,
      auto_sync_orders: true,
      sync_interval_minutes: 5
    },
    webhook_config: {
      subscribed_events: ['message', 'order']
    }
  },
  {
    id: '2',
    platform_type: 'jd',
    platform_name: '京东',
    platform_icon: '🐕',
    platform_shop_id: 'JD789012',
    platform_shop_name: '示例京东店',
    platform_shop_logo: '',
    auth_status: 'pending',
    authorized_at: null,
    expires_at: null,
    api_config: {},
    sync_config: {
      auto_sync_messages: true,
      auto_sync_orders: true,
      sync_interval_minutes: 5
    },
    webhook_config: {
      subscribed_events: ['message']
    }
  }
])

// 配置详情
const configDetail = ref<any>({})
const webhookUrl = computed(() => {
  if (!configDetail.value.id) return ''
  return `${window.location.origin}/api/webhooks/platform/${configDetail.value.id}`
})

// 状态显示
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'authorized': 'success',
    'pending': 'warning',
    'expired': 'danger',
    'revoked': 'info',
    'error': 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    'authorized': '已授权',
    'pending': '待授权',
    'expired': '已过期',
    'revoked': '已撤销',
    'error': '授权失败'
  }
  return map[status] || status
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const isExpiringSoon = (expiresAt: string) => {
  const expires = new Date(expiresAt).getTime()
  const now = Date.now()
  const threeDays = 3 * 24 * 60 * 60 * 1000
  return expires - now < threeDays && expires > now
}

// 操作
const nextStep = () => {
  if (addStep.value === 0 && !newPlatform.value.platform_type) {
    ElMessage.warning('请选择平台')
    return
  }
  if (addStep.value === 1 && (!apiConfigForm.value.app_key || !apiConfigForm.value.app_secret)) {
    ElMessage.warning('请填写完整的API配置')
    return
  }
  addStep.value++
}

const startAuth = () => {
  // 模拟跳转到平台授权页面
  ElMessage.success('正在跳转到授权页面...')
  showAddPlatform.value = false
  addStep.value = 0
  
  // 模拟授权成功后的回调
  setTimeout(() => {
    ElMessage.success('平台授权成功！')
  }, 2000)
}

const handleAuth = (row: any) => {
  ElMessage.info(`正在跳转到${row.platform_name}授权页面...`)
}

const refreshToken = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定刷新 ${row.platform_name} 的授权令牌吗？`, '提示')
    ElMessage.success('令牌刷新成功')
    // 更新过期时间
    const newExpires = new Date()
    newExpires.setDate(newExpires.getDate() + 30)
    row.expires_at = newExpires.toISOString()
  } catch {
    // 取消
  }
}

const editConfig = (row: any) => {
  configDetail.value = JSON.parse(JSON.stringify(row))
  showConfigDetail.value = true
}

const saveConfig = () => {
  ElMessage.success('配置保存成功')
  showConfigDetail.value = false
}

const revokeAuth = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定撤销 ${row.platform_name} 的授权吗？撤销后将无法接收该平台的订单和消息。`,
      '警告',
      { type: 'warning' }
    )
    row.auth_status = 'revoked'
    ElMessage.success('授权已撤销')
  } catch {
    // 取消
  }
}

const copyWebhookUrl = () => {
  navigator.clipboard.writeText(webhookUrl.value)
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped>
.platform-settings {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.platform-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.platform-icon {
  font-size: 24px;
}

.shop-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.shop-detail {
  display: flex;
  flex-direction: column;
}

.shop-name {
  font-weight: 500;
}

.shop-id {
  font-size: 12px;
  color: #909399;
}

.text-danger {
  color: #f56c6c;
}

.platform-preview {
  margin-top: 20px;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.preview-icon {
  font-size: 40px;
}

.preview-name {
  font-size: 18px;
  font-weight: 500;
}

.preview-desc {
  color: #606266;
  margin-bottom: 12px;
}

.preview-features {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.auth-guide {
  padding: 20px 0;
}

.auth-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
  text-align: left;
  margin-top: 20px;
}

.auth-step {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.auth-step .el-icon {
  color: #67c23a;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
