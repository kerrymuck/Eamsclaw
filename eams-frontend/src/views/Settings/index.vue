<template>
  <div class="settings">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- AI设置 -->
      <el-tab-pane label="AI配置" name="ai">
        <el-form :model="aiForm" label-width="140px" style="max-width: 700px">
          <el-form-item label="AI模型">
            <el-select v-model="aiForm.model" style="width: 100%" @change="handleModelChange">
              <el-option-group label="OpenAI">
                <el-option label="GPT-4" value="gpt-4" />
                <el-option label="GPT-4o" value="gpt-4o" />
                <el-option label="GPT-3.5 Turbo" value="gpt-3.5-turbo" />
              </el-option-group>
              <el-option-group label="Anthropic">
                <el-option label="Claude 3.5 Sonnet" value="claude-3.5-sonnet" />
                <el-option label="Claude 3 Opus" value="claude-3-opus" />
              </el-option-group>
              <el-option-group label="国产模型">
                <el-option label="Kimi K2.5 (Moonshot)" value="kimi-k2.5" />
                <el-option label="文心一言4.0 (百度)" value="wenxin-4" />
                <el-option label="通义千问Max (阿里)" value="qwen-max" />
                <el-option label="豆包Pro (字节)" value="doubao-pro" />
                <el-option label="GLM-4 (智谱)" value="glm-4" />
              </el-option-group>
            </el-select>
          </el-form-item>
          
          <!-- API Key 配置 - 根据模型动态显示 -->
          <el-divider>API 密钥配置</el-divider>
          
          <el-form-item :label="apiKeyLabel" v-if="apiKeyLabel">
            <el-input 
              v-model="aiForm.apiKey" 
              type="password" 
              show-password
              :placeholder="apiKeyPlaceholder"
            />
            <div class="form-tip">
              <el-link type="primary" :href="apiKeyDocUrl" target="_blank">
                如何获取 {{ currentProvider }} API Key?
              </el-link>
            </div>
          </el-form-item>
          
          <!-- 可选参数 -->
          <el-form-item label="Base URL" v-if="showBaseUrl">
            <el-input v-model="aiForm.baseUrl" placeholder="可选，用于自定义API地址或代理" />
          </el-form-item>
          
          <el-form-item label="Organization ID" v-if="showOrgId">
            <el-input v-model="aiForm.organizationId" placeholder="可选，OpenAI组织ID" />
          </el-form-item>
          
          <el-divider>模型参数</el-divider>
          
          <el-form-item label="温度">
            <el-slider v-model="aiForm.temperature" :min="0" :max="1" :step="0.1" show-stops />
            <div class="form-tip">值越高，回答越随机创意；值越低，回答越确定保守</div>
          </el-form-item>
          <el-form-item label="最大回复长度">
            <el-input-number v-model="aiForm.max_tokens" :min="100" :max="4000" :step="100" />
          </el-form-item>
          <el-form-item label="自动转人工">
            <el-switch v-model="aiForm.auto_handoff" />
          </el-form-item>
          <el-form-item label="转人工阈值" v-if="aiForm.auto_handoff">
            <el-input-number v-model="aiForm.handoff_threshold" :min="1" :max="5" />
            <span style="margin-left: 10px; color: #909399">次未解决后转人工</span>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveAI">保存配置</el-button>
            <el-button @click="testConnection">测试连接</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <!-- 平台对接 -->
      <el-tab-pane label="平台对接" name="platform">
        <PlatformSettings />
      </el-tab-pane>
      
      <!-- 成员管理 -->
      <el-tab-pane label="成员管理" name="members">
        <div style="margin-bottom: 20px">
          <el-button type="primary" @click="showAddMember = true">邀请成员</el-button>
        </div>
        <el-table :data="members">
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="nickname" label="昵称" />
          <el-table-column prop="role" label="角色">
            <template #default="{ row }">
              <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
                {{ row.role === 'admin' ? '管理员' : '客服' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                {{ row.status === 'active' ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="primary" link @click="editMember(row)">编辑</el-button>
              <el-button type="danger" link @click="removeMember(row)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      
      <!-- 授权码信息 -->
      <el-tab-pane label="授权码信息" name="license">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>授权码详情</span>
              <el-tag :type="licenseInfo.status === 'active' ? 'success' : 'danger'">
                {{ licenseInfo.status === 'active' ? '已激活' : '已过期' }}
              </el-tag>
            </div>
          </template>
          
          <div class="license-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="授权码">{{ licenseInfo.code }}</el-descriptions-item>
              <el-descriptions-item label="授权类型">{{ licenseInfo.type }}</el-descriptions-item>
              <el-descriptions-item label="所属服务商">{{ licenseInfo.provider }}</el-descriptions-item>
              <el-descriptions-item label="激活时间">{{ licenseInfo.activateTime }}</el-descriptions-item>
              <el-descriptions-item label="到期时间">
                <span :class="{ 'expired': isLicenseExpired }">{{ licenseInfo.expireTime }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="剩余天数">
                <el-tag :type="licenseInfo.remainingDays > 30 ? 'success' : licenseInfo.remainingDays > 7 ? 'warning' : 'danger'">
                  {{ licenseInfo.remainingDays }} 天
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
            
            <!-- 绑定店铺信息 -->
            <div class="bound-shops-section" style="margin-top: 24px;">
              <div class="section-header" style="margin-bottom: 16px;">
                <span style="font-weight: 600; font-size: 16px;">绑定店铺信息</span>
                <el-tag type="info" size="small">共 {{ boundShops.length }} 个店铺</el-tag>
              </div>
              <el-table :data="boundShops" border style="width: 100%">
                <el-table-column prop="shopName" label="店铺名称" min-width="150" />
                <el-table-column prop="platform" label="所属平台" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getPlatformType(row.platform)" size="small">
                      {{ row.platform }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="shopId" label="店铺ID" width="150" />
                <el-table-column prop="bindTime" label="绑定时间" width="160" />
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                      {{ row.status === 'active' ? '正常' : '已解绑' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="120" fixed="right">
                  <template #default="{ row }">
                    <el-button type="primary" link size="small" @click="viewShopDetail(row)">查看</el-button>
                    <el-button type="danger" link size="small" @click="unbindShop(row)">解绑</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div class="license-actions" style="margin-top: 20px;">
              <el-button type="primary" @click="handleRenewLicense">续期授权</el-button>
              <el-button @click="handleTransferLicense">转移授权</el-button>
            </div>
          </div>
        </el-card>
        
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>授权历史</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in licenseHistory"
              :key="index"
              :type="activity.type"
              :timestamp="activity.time"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-tab-pane>
      
      <!-- 版本信息 -->
      <el-tab-pane label="版本信息" name="version">
        <el-card style="max-width: 600px">
          <template #header>
            <div class="card-header">
              <span>当前版本</span>
              <el-tag type="success">v{{ versionInfo.currentVersion }}</el-tag>
            </div>
          </template>
          
          <div class="version-info">
            <div class="info-row">
              <span class="label">版本号：</span>
              <span class="value">v{{ versionInfo.currentVersion }}</span>
            </div>
            <div class="info-row">
              <span class="label">发布日期：</span>
              <span class="value">{{ versionInfo.publishDate }}</span>
            </div>
            <div class="info-row">
              <span class="label">更新内容：</span>
              <ul class="update-list">
                <li v-for="(item, index) in versionInfo.updateContent" :key="index">{{ item }}</li>
              </ul>
            </div>
            <div class="info-row">
              <span class="label">最新版本：</span>
              <span class="value">
                <template v-if="versionInfo.checking">
                  <el-icon class="is-loading"><Loading /></el-icon> 检查中...
                </template>
                <template v-else-if="versionInfo.hasUpdate">
                  <el-tag type="warning">v{{ versionInfo.latestVersion }}</el-tag>
                  <el-button type="primary" size="small" style="margin-left: 12px;" @click="handleUpdate">
                    立即更新
                  </el-button>
                </template>
                <template v-else>
                  <el-tag type="success">已是最新</el-tag>
                </template>
              </span>
            </div>
            <div class="info-row" v-if="versionInfo.hasUpdate">
              <span class="label">更新说明：</span>
              <span class="value description">{{ versionInfo.latestDescription }}</span>
            </div>
          </div>
          
          <div style="margin-top: 20px; text-align: center;">
            <el-button 
              :icon="Refresh" 
              :loading="versionInfo.checking"
              @click="checkUpdate"
            >
              检查更新
            </el-button>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 邀请成员对话框 -->
    <el-dialog v-model="showAddMember" title="邀请成员" width="400px">
      <el-form :model="memberForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="memberForm.username" placeholder="输入用户名或邮箱" />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="memberForm.role">
            <el-radio label="agent">客服</el-radio>
            <el-radio label="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddMember = false">取消</el-button>
        <el-button type="primary" @click="inviteMember">邀请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, Refresh } from '@element-plus/icons-vue'
import PlatformSettings from './Platform.vue'

const activeTab = ref('ai')

// AI设置
const aiForm = ref({
  model: 'kimi-k2.5',
  apiKey: '',
  baseUrl: '',
  organizationId: '',
  temperature: 0.7,
  max_tokens: 500,
  auto_handoff: true,
  handoff_threshold: 3
})

// 模型提供商配置
const modelProviders: Record<string, { name: string; apiKeyName: string; apiKeyPlaceholder: string; docUrl: string; showBaseUrl: boolean; showOrgId: boolean }> = {
  'gpt-4': { name: 'OpenAI', apiKeyName: 'OpenAI API Key', apiKeyPlaceholder: 'sk-...', docUrl: 'https://platform.openai.com/api-keys', showBaseUrl: true, showOrgId: true },
  'gpt-4o': { name: 'OpenAI', apiKeyName: 'OpenAI API Key', apiKeyPlaceholder: 'sk-...', docUrl: 'https://platform.openai.com/api-keys', showBaseUrl: true, showOrgId: true },
  'gpt-3.5-turbo': { name: 'OpenAI', apiKeyName: 'OpenAI API Key', apiKeyPlaceholder: 'sk-...', docUrl: 'https://platform.openai.com/api-keys', showBaseUrl: true, showOrgId: true },
  'claude-3.5-sonnet': { name: 'Anthropic', apiKeyName: 'Anthropic API Key', apiKeyPlaceholder: 'sk-ant-...', docUrl: 'https://console.anthropic.com/settings/keys', showBaseUrl: true, showOrgId: false },
  'claude-3-opus': { name: 'Anthropic', apiKeyName: 'Anthropic API Key', apiKeyPlaceholder: 'sk-ant-...', docUrl: 'https://console.anthropic.com/settings/keys', showBaseUrl: true, showOrgId: false },
  'kimi-k2.5': { name: 'Moonshot', apiKeyName: 'Moonshot API Key', apiKeyPlaceholder: 'sk-...', docUrl: 'https://platform.moonshot.cn/console/api-keys', showBaseUrl: true, showOrgId: false },
  'wenxin-4': { name: '百度', apiKeyName: '百度 API Key', apiKeyPlaceholder: '请输入百度千帆API Key', docUrl: 'https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application', showBaseUrl: false, showOrgId: false },
  'qwen-max': { name: '阿里', apiKeyName: 'DashScope API Key', apiKeyPlaceholder: 'sk-...', docUrl: 'https://dashscope.console.aliyun.com/apiKey', showBaseUrl: false, showOrgId: false },
  'doubao-pro': { name: '字节', apiKeyName: '豆包 API Key', apiKeyPlaceholder: '请输入豆包API Key', docUrl: 'https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey', showBaseUrl: false, showOrgId: false },
  'glm-4': { name: '智谱', apiKeyName: '智谱 API Key', apiKeyPlaceholder: '请输入智谱AI API Key', docUrl: 'https://open.bigmodel.cn/usercenter/apikeys', showBaseUrl: true, showOrgId: false }
}

// 计算当前模型提供商信息
const currentProvider = computed(() => {
  return modelProviders[aiForm.value.model]?.name || ''
})

const apiKeyLabel = computed(() => {
  return modelProviders[aiForm.value.model]?.apiKeyName || ''
})

const apiKeyPlaceholder = computed(() => {
  return modelProviders[aiForm.value.model]?.apiKeyPlaceholder || ''
})

const apiKeyDocUrl = computed(() => {
  return modelProviders[aiForm.value.model]?.docUrl || ''
})

const showBaseUrl = computed(() => {
  return modelProviders[aiForm.value.model]?.showBaseUrl || false
})

const showOrgId = computed(() => {
  return modelProviders[aiForm.value.model]?.showOrgId || false
})

const handleModelChange = () => {
  // 切换模型时清空相关配置
  aiForm.value.apiKey = ''
  aiForm.value.baseUrl = ''
  aiForm.value.organizationId = ''
}

const saveAI = () => {
  ElMessage.success('AI配置保存成功')
}

const testConnection = () => {
  ElMessage.info('正在测试连接...')
  setTimeout(() => {
    ElMessage.success('连接成功')
  }, 1500)
}

// 成员管理
const members = ref<any[]>([])
const showAddMember = ref(false)
const memberForm = ref({ username: '', role: 'agent' })

const inviteMember = () => {
  ElMessage.success('邀请已发送')
  showAddMember.value = false
  memberForm.value = { username: '', role: 'agent' }
}

const editMember = (row: any) => {
  // TODO: 编辑成员
}

const removeMember = (row: any) => {
  ElMessageBox.confirm('确定要移除该成员吗？', '提示', { type: 'warning' })
    .then(() => {
      ElMessage.success('已移除')
    })
}

// 授权码信息
const licenseInfo = ref({
  code: 'EAMS-PRO-2026-X8K9M2N4P5',
  type: '专业版',
  provider: '科技云',
  status: 'active',
  activateTime: '2026-01-15 10:30:00',
  expireTime: '2027-01-15 10:30:00',
  remainingDays: 280
})

// 绑定店铺信息
const boundShops = ref([
  { shopName: '科技云旗舰店', platform: '淘宝', shopId: 'TB123456', bindTime: '2026-01-15 10:35:00', status: 'active' },
  { shopName: '科技云数码店', platform: '京东', shopId: 'JD789012', bindTime: '2026-01-20 14:22:00', status: 'active' },
  { shopName: '科技云生活馆', platform: '拼多多', shopId: 'PDD345678', bindTime: '2026-02-01 09:15:00', status: 'active' },
  { shopName: '科技云海外店', platform: '天猫国际', shopId: 'TMG901234', bindTime: '2026-02-10 16:45:00', status: 'active' }
])

// 获取平台标签类型
const getPlatformType = (platform: string) => {
  const typeMap: Record<string, string> = {
    '淘宝': 'danger',
    '天猫': 'danger',
    '天猫国际': 'danger',
    '京东': 'primary',
    '拼多多': 'success',
    '抖音': 'warning',
    '快手': 'warning',
    '小红书': 'info',
    '亚马逊': 'primary',
    'eBay': 'success',
    'Shopee': 'warning',
    'Lazada': 'info'
  }
  return typeMap[platform] || 'info'
}

// 查看店铺详情
const viewShopDetail = (row: any) => {
  ElMessage.info(`查看店铺: ${row.shopName}`)
}

// 解绑店铺
const unbindShop = (row: any) => {
  ElMessageBox.confirm(`确定要解绑店铺「${row.shopName}」吗？解绑后该店铺将无法使用智能客服功能。`, '提示', { type: 'warning' })
    .then(() => {
      ElMessage.success('店铺解绑成功')
    })
}

const isLicenseExpired = computed(() => {
  return new Date(licenseInfo.value.expireTime) < new Date()
})

const licenseHistory = ref([
  { content: '授权码续期成功，延长1年', time: '2026-01-15 10:30:00', type: 'success' },
  { content: '授权码激活成功', time: '2026-01-15 10:30:00', type: 'primary' },
  { content: '授权码生成', time: '2026-01-15 09:00:00', type: 'info' }
])

const handleRenewLicense = () => {
  ElMessageBox.confirm('确定要续期授权码吗？续期后将延长1年有效期', '提示', { type: 'info' })
    .then(() => {
      ElMessage.success('续期申请已提交，请联系服务商确认')
    })
}

const handleTransferLicense = () => {
  ElMessageBox.prompt('请输入新的商户ID', '转移授权', {
    confirmButtonText: '确认转移',
    cancelButtonText: '取消',
    inputPattern: /^.+$/,
    inputErrorMessage: '商户ID不能为空'
  }).then(({ value }) => {
    ElMessage.success(`授权码转移申请已提交至商户 ${value}`)
  })
}

// 版本信息
const versionInfo = ref({
  currentVersion: '1.2.3',
  publishDate: '2026-04-01',
  updateContent: [
    '优化AI客服响应速度',
    '新增多平台店铺同步功能',
    '修复已知问题'
  ],
  checking: false,
  hasUpdate: false,
  latestVersion: '',
  latestDescription: ''
})

// 检查更新
const checkUpdate = async () => {
  versionInfo.value.checking = true
  setTimeout(() => {
    versionInfo.value.checking = false
    versionInfo.value.hasUpdate = true
    versionInfo.value.latestVersion = '1.3.0'
    versionInfo.value.latestDescription = '新增智能工单分配功能，优化AI对话体验'
  }, 1500)
}

// 处理更新
const handleUpdate = () => {
  ElMessage.success('正在下载更新...')
}

onMounted(() => {
  // TODO: 加载设置数据
})
</script>

<style scoped>
.settings {
  padding: 20px;
}

.platform-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.license-info .expired {
  color: #f56c6c;
}

.license-actions {
  display: flex;
  gap: 12px;
}

.version-info {
  padding: 8px 0;
}

.info-row {
  display: flex;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  width: 100px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #333;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.info-row .value.description {
  color: #666;
  line-height: 1.6;
}

.update-list {
  margin: 0;
  padding-left: 20px;
  color: #333;
}

.update-list li {
  margin: 5px 0;
}

.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
