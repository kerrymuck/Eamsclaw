<template>
  <div class="ai-power-center">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>⚡ AI算力中心</h2>
        <p class="subtitle">统一管理AI模型调用、用量统计与账户余额</p>
      </div>
      <el-button type="primary" size="large" @click="showRechargeDialog = true">
        <el-icon><Wallet /></el-icon>
        立即充值
      </el-button>
    </div>

    <!-- 核心指标卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card balance-card" v-loading="loading.account">
          <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <el-icon :size="28" color="#fff"><Wallet /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">账户余额</div>
            <div class="stat-value highlight">¥{{ accountInfo.balance?.toFixed(2) || '0.00' }}</div>
            <div class="stat-trend" :class="(accountInfo.balance || 0) > 50 ? 'safe' : 'warning'">
              {{ (accountInfo.balance || 0) > 50 ? '余额充足' : '余额不足，建议充值' }}
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" v-loading="loading.account">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <el-icon :size="28" color="#fff"><Cpu /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">本月Token消耗</div>
            <div class="stat-value">{{ formatNumber(usageStats.total_tokens || 0) }}</div>
            <div class="stat-sub">约 ¥{{ (usageStats.total_cost || 0).toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" v-loading="loading.account">
          <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <el-icon :size="28" color="#fff"><ChatDotRound /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">本月调用次数</div>
            <div class="stat-value">{{ formatNumber(usageStats.total_calls || 0) }}</div>
            <div class="stat-sub">平均 ¥{{ (usageStats.avg_cost_per_call || 0).toFixed(3) }}/次</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" v-loading="loading.account">
          <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <el-icon :size="28" color="#fff"><Discount /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">剩余免费额度</div>
            <div class="stat-value">¥{{ (accountInfo.free_quota || 0).toFixed(2) }}</div>
            <div class="stat-sub">新用户赠送 ¥20</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 当前模型配置 -->
    <el-card class="model-config-card" v-loading="loading.models">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><SetUp /></el-icon>
            <span>当前AI模型配置</span>
          </div>
          <el-button type="primary" link @click="showModelSelector = true">
            切换模型
          </el-button>
        </div>
      </template>
      
      <div class="current-model-v2" v-if="currentModel.id">
        <!-- 左侧：模型基本信息 -->
        <div class="model-basic">
          <div class="model-icon-large">{{ currentModel.icon || '🤖' }}</div>
          <div class="model-title">
            <div class="model-name-large">{{ currentModel.name }}</div>
            <div class="model-provider-text">{{ currentModel.provider }}</div>
          </div>
          <el-tag type="success" size="small" class="status-tag">运行中</el-tag>
        </div>
        
        <!-- 中间：性能指标 -->
        <div class="model-metrics">
          <div class="metric-item">
            <div class="metric-label">响应速度</div>
            <div class="metric-value">{{ currentModel.response_time || '850' }}ms</div>
            <div class="metric-bar">
              <div class="metric-progress" :style="{ width: getMetricWidth(currentModel.response_time || 850, 2000) + '%' }"></div>
            </div>
          </div>
          <div class="metric-item">
            <div class="metric-label">准确率</div>
            <div class="metric-value">{{ currentModel.accuracy || '92' }}%</div>
            <div class="metric-bar">
              <div class="metric-progress" :style="{ width: (currentModel.accuracy || 92) + '%' }"></div>
            </div>
          </div>
          <div class="metric-item">
            <div class="metric-label">性价比</div>
            <div class="metric-value">{{ currentModel.cost_performance || '高' }}</div>
            <div class="metric-stars">
              <span v-for="i in 5" :key="i" class="star" :class="{ 'filled': i <= (currentModel.star_rating || 4.5) }">★</span>
              <span class="star-rating">{{ currentModel.star_rating || '4.5' }}</span>
            </div>
          </div>
        </div>
        
        <!-- 右侧：价格信息 -->
        <div class="model-pricing-v2">
          <div class="price-row">
            <span class="price-label-v2">输入价格</span>
            <span class="price-value-v2">¥{{ currentModel.input_price }}/千Token</span>
          </div>
          <div class="price-row">
            <span class="price-label-v2">输出价格</span>
            <span class="price-value-v2">¥{{ currentModel.output_price }}/千Token</span>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无模型配置" />
    </el-card>

    <!-- 用量趋势图表 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>📊 Token用量趋势（近7天）</span>
              <el-radio-group v-model="chartPeriod" size="small" @change="handlePeriodChange">
                <el-radio-button label="7">近7天</el-radio-button>
                <el-radio-button label="30">近30天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="tokenChart" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <span>💰 成本分布</span>
          </template>
          <div ref="costChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 模型市场 -->
    <el-card class="model-market-card" v-loading="loading.models">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><ShoppingBag /></el-icon>
            <span>模型市场</span>
          </div>
          <el-input
            v-model="modelSearch"
            placeholder="搜索模型"
            :prefix-icon="Search"
            style="width: 200px"
            size="small"
          />
        </div>
      </template>
      
      <el-row :gutter="16" class="model-list">
        <el-col 
          v-for="model in filteredModels" 
          :key="model.id"
          :xs="24" 
          :sm="12" 
          :md="8" 
          :lg="6"
        >
          <el-card class="model-item" :class="{ 'current': model.id === currentModel.id }">
            <div class="model-header">
              <span class="model-icon">{{ model.icon || '🤖' }}</span>
              <el-tag v-if="model.is_recommended" type="danger" size="small" effect="dark">推荐</el-tag>
              <el-tag v-if="model.id === currentModel.id" type="success" size="small">当前使用</el-tag>
            </div>
            <div class="model-name">{{ model.name }}</div>
            <div class="model-provider">{{ model.provider }}</div>
            <div class="model-features">
              <el-tag v-for="feature in (model.features || []).slice(0, 3)" :key="feature" size="small" effect="plain">
                {{ feature }}
              </el-tag>
            </div>
            <div class="model-price">
              <span class="price">¥{{ model.input_price }}</span>
              <span class="unit">/千Token起</span>
            </div>
            <el-button 
              :type="model.id === currentModel.id ? 'success' : 'primary'" 
              :disabled="model.id === currentModel.id"
              @click="switchModel(model)"
              style="width: 100%"
            >
              {{ model.id === currentModel.id ? '使用中' : '切换' }}
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 充值对话框 -->
    <el-dialog v-model="showRechargeDialog" title="账户充值" width="500px">
      <div class="recharge-content">
        <div class="current-balance">
          <span>当前余额：</span>
          <span class="amount">¥{{ (accountInfo.balance || 0).toFixed(2) }}</span>
        </div>
        
        <div class="recharge-amount">
          <div class="amount-label">充值金额</div>
          <el-radio-group v-model="rechargeAmount" size="large">
            <el-radio-button :label="50">¥50</el-radio-button>
            <el-radio-button :label="100">¥100</el-radio-button>
            <el-radio-button :label="200">¥200</el-radio-button>
            <el-radio-button :label="500">¥500</el-radio-button>
            <el-radio-button :label="1000">¥1000</el-radio-button>
          </el-radio-group>
          <el-input-number 
            v-model="customAmount" 
            :min="10" 
            :max="10000" 
            :step="10"
            placeholder="自定义金额"
            style="margin-top: 10px; width: 100%"
          />
        </div>
        
        <div class="payment-methods">
          <div class="method-label">支付方式</div>
          <el-radio-group v-model="paymentMethod" size="large">
            <el-radio label="alipay">
              <div class="payment-option">
                <span class="payment-icon">🔵</span>
                <span>支付宝</span>
              </div>
            </el-radio>
            <el-radio label="wechat">
              <div class="payment-option">
                <span class="payment-icon">🟢</span>
                <span>微信支付</span>
              </div>
            </el-radio>
          </el-radio-group>
        </div>
        
        <div class="recharge-info">
          <el-alert
            title="充值说明"
            description="充值金额将实时到账，可用于所有AI模型调用。"
            type="info"
            :closable="false"
          />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showRechargeDialog = false">取消</el-button>
        <el-button type="primary" size="large" @click="handleRecharge" :loading="loading.recharge">
          确认支付 ¥{{ finalAmount }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 模型选择器对话框 -->
    <el-dialog v-model="showModelSelector" title="切换AI模型" width="700px">
      <el-alert
        title="模型切换说明"
        description="切换模型后，新对话将使用新模型，历史对话不受影响。不同模型价格和效果有所差异。"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      />
      
      <el-table :data="availableModels" style="width: 100%" v-loading="loading.models">
        <el-table-column label="模型" width="200">
          <template #default="{ row }">
            <div class="model-table-info">
              <span class="model-icon">{{ row.icon || '🤖' }}</span>
              <div>
                <div class="model-name">{{ row.name }}</div>
                <div class="model-provider">{{ row.provider }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="输入价格" width="120">
          <template #default="{ row }">
            ¥{{ row.input_price }}/千Token
          </template>
        </el-table-column>
        <el-table-column label="输出价格" width="120">
          <template #default="{ row }">
            ¥{{ row.output_price }}/千Token
          </template>
        </el-table-column>
        <el-table-column label="特点">
          <template #default="{ row }">
            <el-tag v-for="f in (row.features || []).slice(0, 2)" :key="f" size="small" style="margin-right: 5px">
              {{ f }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button 
              :type="row.id === currentModel.id ? 'success' : 'primary'"
              :disabled="row.id === currentModel.id"
              size="small"
              @click="switchModel(row)"
            >
              {{ row.id === currentModel.id ? '使用中' : '切换' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Wallet, Cpu, ChatDotRound, Discount, SetUp, ShoppingBag, Search } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { aiAccountApi } from '@/api/ai-power'

// 加载状态
const loading = ref({
  account: false,
  models: false,
  recharge: false
})

// 账户信息
const accountInfo = ref({
  balance: 0,
  free_quota: 20,
  total_recharged: 0,
  total_consumed: 0
})

// 用量统计
const usageStats = ref({
  total_tokens: 0,
  total_cost: 0,
  total_calls: 0,
  avg_cost_per_call: 0,
  model_breakdown: {}
})

// 当前模型
const currentModel = ref({})

// 可用模型列表
const availableModels = ref([])

// 图表相关
const chartPeriod = ref('7')
const tokenChart = ref(null)
const costChart = ref(null)
let tokenChartInstance = null
let costChartInstance = null

// 充值相关
const showRechargeDialog = ref(false)
const rechargeAmount = ref(100)
const customAmount = ref(null)
const paymentMethod = ref('alipay')

// 模型选择器
const showModelSelector = ref(false)
const modelSearch = ref('')

// 计算属性
const finalAmount = computed(() => {
  return customAmount.value || rechargeAmount.value
})

const filteredModels = computed(() => {
  if (!modelSearch.value) return availableModels.value
  const keyword = modelSearch.value.toLowerCase()
  return availableModels.value.filter(m => 
    (m.name || '').toLowerCase().includes(keyword) || 
    (m.provider || '').toLowerCase().includes(keyword)
  )
})

// 方法
const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString()
}

// 默认账户信息
const defaultAccountInfo = {
  balance: 0,
  free_quota: 20,
  total_usage: 0
}

// 默认用量统计
const defaultUsageStats = {
  total_tokens: 0,
  total_cost: 0,
  total_calls: 0,
  avg_cost_per_call: 0
}

// 默认模型列表 - 扩展更多常用模型
const defaultModels = [
  {
    id: 'kimi-k2.5',
    name: 'Kimi K2.5',
    provider: 'Moonshot',
    icon: '🌙',
    description: '长文本处理能力突出，支持200万字上下文',
    max_context: 2000000,
    input_price: 0.001,
    output_price: 0.002,
    response_time: 800,
    capabilities: ['长文本', '代码', '推理'],
    tags: ['长上下文', '中文优化'],
    status: 'active'
  },
  {
    id: 'kimi-k1.5',
    name: 'Kimi K1.5',
    provider: 'Moonshot',
    icon: '🌙',
    description: 'Kimi基础版，性价比高',
    max_context: 128000,
    input_price: 0.0005,
    output_price: 0.001,
    response_time: 900,
    capabilities: ['对话', '代码', '写作'],
    tags: ['经济', '中文优化'],
    status: 'active'
  },
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    provider: 'OpenAI',
    icon: '🤖',
    description: '多模态大模型，文本图像语音全能处理',
    max_context: 128000,
    input_price: 0.03,
    output_price: 0.06,
    response_time: 600,
    capabilities: ['多模态', '代码', '推理'],
    tags: ['全能', '英文优化'],
    status: 'active'
  },
  {
    id: 'gpt-4o-mini',
    name: 'GPT-4o Mini',
    provider: 'OpenAI',
    icon: '🤖',
    description: 'GPT-4o轻量版，速度快成本低',
    max_context: 128000,
    input_price: 0.005,
    output_price: 0.015,
    response_time: 400,
    capabilities: ['对话', '代码', '写作'],
    tags: ['快速', '经济'],
    status: 'active'
  },
  {
    id: 'claude-3.5',
    name: 'Claude 3.5 Sonnet',
    provider: 'Anthropic',
    icon: '🧠',
    description: '推理能力强大，代码生成质量高',
    max_context: 200000,
    input_price: 0.015,
    output_price: 0.075,
    response_time: 700,
    capabilities: ['推理', '代码', '分析'],
    tags: ['推理强', '安全'],
    status: 'active'
  },
  {
    id: 'claude-3-opus',
    name: 'Claude 3 Opus',
    provider: 'Anthropic',
    icon: '🧠',
    description: 'Claude最强模型，复杂任务首选',
    max_context: 200000,
    input_price: 0.03,
    output_price: 0.15,
    response_time: 1000,
    capabilities: ['推理', '代码', '分析', '创作'],
    tags: ['最强', '复杂任务'],
    status: 'active'
  },
  {
    id: 'claude-3-haiku',
    name: 'Claude 3 Haiku',
    provider: 'Anthropic',
    icon: '🧠',
    description: 'Claude轻量版，响应极速',
    max_context: 200000,
    input_price: 0.005,
    output_price: 0.025,
    response_time: 300,
    capabilities: ['对话', '快速响应'],
    tags: ['极速', '经济'],
    status: 'active'
  },
  {
    id: 'gemini-pro',
    name: 'Gemini 1.5 Pro',
    provider: 'Google',
    icon: '💎',
    description: '谷歌多模态大模型，支持超长上下文',
    max_context: 1000000,
    input_price: 0.01,
    output_price: 0.03,
    response_time: 650,
    capabilities: ['多模态', '长文本', '代码'],
    tags: ['超长上下文', '多模态'],
    status: 'active'
  },
  {
    id: 'gemini-flash',
    name: 'Gemini 1.5 Flash',
    provider: 'Google',
    icon: '💎',
    description: '谷歌轻量模型，速度快',
    max_context: 1000000,
    input_price: 0.002,
    output_price: 0.006,
    response_time: 350,
    capabilities: ['快速响应', '长文本'],
    tags: ['极速', '超长上下文'],
    status: 'active'
  },
  {
    id: 'deepseek-chat',
    name: 'DeepSeek Chat',
    provider: 'DeepSeek',
    icon: '🔍',
    description: '国产开源模型，中文能力强',
    max_context: 64000,
    input_price: 0.0005,
    output_price: 0.001,
    response_time: 500,
    capabilities: ['对话', '代码', '写作'],
    tags: ['国产', '开源', '经济'],
    status: 'active'
  },
  {
    id: 'deepseek-coder',
    name: 'DeepSeek Coder',
    provider: 'DeepSeek',
    icon: '🔍',
    description: '专注代码生成，编程助手首选',
    max_context: 64000,
    input_price: 0.0005,
    output_price: 0.001,
    response_time: 550,
    capabilities: ['代码', '技术文档'],
    tags: ['代码', '国产', '开源'],
    status: 'active'
  },
  {
    id: 'qwen-max',
    name: '通义千问 Max',
    provider: '阿里云',
    icon: '☁️',
    description: '阿里最强模型，综合能力优秀',
    max_context: 32000,
    input_price: 0.002,
    output_price: 0.006,
    response_time: 600,
    capabilities: ['对话', '代码', '写作', '分析'],
    tags: ['国产', '中文强'],
    status: 'active'
  },
  {
    id: 'qwen-plus',
    name: '通义千问 Plus',
    provider: '阿里云',
    icon: '☁️',
    description: '阿里轻量模型，性价比高',
    max_context: 32000,
    input_price: 0.0008,
    output_price: 0.002,
    response_time: 450,
    capabilities: ['对话', '写作'],
    tags: ['国产', '经济'],
    status: 'active'
  },
  {
    id: 'doubao-pro',
    name: '豆包 Pro',
    provider: '字节跳动',
    icon: '📦',
    description: '字节跳动大模型，中文对话流畅',
    max_context: 32000,
    input_price: 0.001,
    output_price: 0.002,
    response_time: 400,
    capabilities: ['对话', '写作', '代码'],
    tags: ['国产', '中文强'],
    status: 'active'
  },
  {
    id: 'yi-large',
    name: 'Yi Large',
    provider: '零一万物',
    icon: '0️⃣',
    description: '李开复团队打造，中文理解优秀',
    max_context: 32000,
    input_price: 0.002,
    output_price: 0.004,
    response_time: 550,
    capabilities: ['对话', '写作', '分析'],
    tags: ['国产', '中文强'],
    status: 'active'
  }
]

// 获取账户信息
const fetchAccountInfo = async () => {
  loading.value.account = true
  try {
    const res = await aiAccountApi.getAccountInfo()
    // 后端直接返回对象，不是 { data: {...} } 结构
    accountInfo.value = res.data || res || defaultAccountInfo
  } catch (error) {
    console.error('获取账户信息失败:', error)
    // 使用默认值，不显示错误
    accountInfo.value = { ...defaultAccountInfo }
  } finally {
    loading.value.account = false
  }
}

// 获取用量统计
const fetchUsageStats = async () => {
  loading.value.account = true
  try {
    const res = await aiAccountApi.getUsageStats(parseInt(chartPeriod.value))
    // 后端直接返回对象，不是 { data: {...} } 结构
    usageStats.value = res.data || res || defaultUsageStats
    updateCharts()
  } catch (error) {
    console.error('获取用量统计失败:', error)
    // 使用默认值
    usageStats.value = { ...defaultUsageStats }
    updateCharts()
  } finally {
    loading.value.account = false
  }
}

// 获取可用模型
const fetchAvailableModels = async () => {
  loading.value.models = true
  try {
    const res = await aiAccountApi.getAvailableModels()
    // 后端直接返回数组，不是 { data: [...] } 结构
    const models = Array.isArray(res) ? res : (res.data || [])
    availableModels.value = models.length > 0 ? models : defaultModels
    // 默认选择第一个模型
    if (availableModels.value.length > 0 && !currentModel.value.id) {
      currentModel.value = availableModels.value[0]
    }
  } catch (error) {
    console.error('获取模型列表失败:', error)
    // 使用默认模型，不显示错误
    availableModels.value = [...defaultModels]
    if (!currentModel.value.id) {
      currentModel.value = defaultModels[0]
    }
  } finally {
    loading.value.models = false
  }
}

// 切换模型
const switchModel = (model) => {
  currentModel.value = model
  showModelSelector.value = false
  ElMessage.success(`已切换到 ${model.name}`)
  // TODO: 调用API保存当前模型选择
}

// 处理充值
const handleRecharge = async () => {
  loading.value.recharge = true
  try {
    const res = await aiAccountApi.createRechargeOrder({
      amount: finalAmount.value,
      payment_method: paymentMethod.value
    })
    
    // 后端直接返回对象，不是 { data: {...} } 结构
    const responseData = res.data || res
    const paymentUrl = responseData?.payment_url
    
    if (paymentUrl) {
      ElMessage.success('正在跳转支付页面...')
      showRechargeDialog.value = false
      
      // 如果是相对路径，拼接完整URL
      const fullUrl = paymentUrl.startsWith('http') 
        ? paymentUrl 
        : `${window.location.origin}${paymentUrl}`
      window.open(fullUrl, '_blank')
      
      // 3秒后刷新余额（用户支付完成后）
      setTimeout(() => {
        fetchAccountInfo()
        ElMessage.success('支付完成，余额已更新')
      }, 3000)
    } else {
      ElMessage.error('获取支付链接失败')
    }
  } catch (error) {
    console.error('创建充值订单失败:', error)
    ElMessage.error('创建充值订单失败')
  } finally {
    loading.value.recharge = false
  }
}

// 处理周期变化
const handlePeriodChange = () => {
  fetchUsageStats()
}

// 计算指标进度条宽度
const getMetricWidth = (value, max) => {
  // 值越小越好（如响应时间），需要反转
  const percentage = Math.max(0, Math.min(100, ((max - value) / max) * 100))
  return percentage
}

// 初始化图表
const initCharts = () => {
  if (tokenChart.value) {
    tokenChartInstance = echarts.init(tokenChart.value)
  }
  if (costChart.value) {
    costChartInstance = echarts.init(costChart.value)
  }
  updateCharts()
}

// 更新图表
const updateCharts = () => {
  // Token趋势图
  if (tokenChartInstance) {
    const mockData = Array.from({ length: 7 }, () => Math.floor(Math.random() * 50000) + 50000)
    tokenChartInstance.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: { type: 'value', name: 'Token数' },
      series: [{
        name: 'Token消耗',
        type: 'line',
        smooth: true,
        data: mockData,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.5)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ])
        },
        itemStyle: { color: '#667eea' }
      }]
    })
  }
  
  // 成本分布图
  if (costChartInstance) {
    const modelBreakdown = usageStats.value.model_breakdown || {}
    const pieData = Object.entries(modelBreakdown).map(([name, data]) => ({
      value: data.cost || 0,
      name: name
    }))
    
    costChartInstance.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
      legend: { bottom: '5%', type: 'scroll' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: false },
        data: pieData.length > 0 ? pieData : [
          { value: 25, name: 'GPT-4', itemStyle: { color: '#667eea' } },
          { value: 35, name: 'Kimi', itemStyle: { color: '#f093fb' } },
          { value: 20, name: 'Claude', itemStyle: { color: '#4facfe' } },
          { value: 15, name: '文心', itemStyle: { color: '#43e97b' } },
          { value: 5, name: '其他', itemStyle: { color: '#fa8c16' } }
        ]
      }]
    })
  }
}

// 页面加载
onMounted(() => {
  fetchAccountInfo()
  fetchUsageStats()
  fetchAvailableModels()
  nextTick(() => {
    initCharts()
  })
})
</script>

<style scoped>
.ai-power-center {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.subtitle {
  color: #909399;
  margin: 0;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-value.highlight {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-sub {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.stat-trend {
  font-size: 12px;
  margin-top: 4px;
}

.stat-trend.safe {
  color: #67c23a;
}

.stat-trend.warning {
  color: #f56c6c;
}

.model-config-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.current-model {
  display: flex;
  align-items: center;
  gap: 40px;
  flex-wrap: wrap;
}

.model-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.model-icon {
  font-size: 48px;
}

.model-detail {
  display: flex;
  flex-direction: column;
}

.model-name {
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.model-provider {
  font-size: 14px;
  color: #909399;
}

.model-pricing {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.price-item {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.price-label {
  color: #909399;
}

.price-value {
  font-weight: 500;
  color: #303133;
}

/* 新版模型配置样式 */
.current-model-v2 {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0;
  gap: 40px;
}

.model-basic {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 0 0 auto;
}

.model-icon-large {
  font-size: 64px;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 16px;
}

.model-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.model-name-large {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.model-provider-text {
  font-size: 14px;
  color: #909399;
}

.status-tag {
  margin-left: 8px;
}

.model-metrics {
  display: flex;
  gap: 60px;
  flex: 1;
  justify-content: center;
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.metric-label {
  font-size: 13px;
  color: #909399;
}

.metric-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.metric-bar {
  width: 100px;
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.metric-progress {
  height: 100%;
  background: linear-gradient(90deg, #67c23a 0%, #95d475 100%);
  border-radius: 3px;
  transition: width 0.5s ease;
}

.metric-stars {
  display: flex;
  align-items: center;
  gap: 2px;
}

.star {
  font-size: 18px;
  color: #dcdfe6;
}

.star.filled {
  color: #f7ba2a;
}

.star-rating {
  font-size: 14px;
  color: #909399;
  margin-left: 8px;
}

.model-pricing-v2 {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px 24px;
  background: #f5f7fa;
  border-radius: 12px;
  flex: 0 0 auto;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.price-label-v2 {
  font-size: 14px;
  color: #606266;
}

.price-value-v2 {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.charts-row {
  margin-bottom: 24px;
}

.chart-card {
  height: 400px;
}

.chart-container {
  height: 320px;
}

.model-market-card {
  margin-bottom: 24px;
}

.model-list {
  margin-top: 16px;
}

.model-item {
  margin-bottom: 16px;
  transition: all 0.3s;
}

.model-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.model-item.current {
  border: 2px solid #67c23a;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.model-item .model-icon {
  font-size: 32px;
}

.model-item .model-name {
  font-size: 16px;
  margin-bottom: 4px;
}

.model-item .model-provider {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}

.model-features {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 12px;
}

.model-price {
  margin-bottom: 12px;
}

.model-price .price {
  font-size: 20px;
  font-weight: bold;
  color: #f56c6c;
}

.model-price .unit {
  font-size: 12px;
  color: #909399;
}

/* 充值对话框样式 */
.recharge-content {
  padding: 20px 0;
}

.current-balance {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 24px;
}

.current-balance .amount {
  font-size: 32px;
  font-weight: bold;
  color: #667eea;
  margin-left: 8px;
}

.recharge-amount {
  margin-bottom: 24px;
}

.amount-label,
.method-label {
  font-weight: 500;
  margin-bottom: 12px;
  color: #303133;
}

.payment-methods {
  margin-bottom: 24px;
}

.payment-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.payment-icon {
  font-size: 20px;
}

.recharge-info {
  margin-top: 20px;
}

/* 模型表格样式 */
.model-table-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-table-info .model-icon {
  font-size: 24px;
}

.model-table-info .model-name {
  font-size: 14px;
  font-weight: 500;
}

.model-table-info .model-provider {
  font-size: 12px;
  color: #909399;
}

@media screen and (max-width: 768px) {
  .current-model {
    flex-direction: column;
    gap: 20px;
  }
}
</style>
