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
        <el-card class="stat-card balance-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <el-icon :size="28" color="#fff"><Wallet /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">账户余额</div>
            <div class="stat-value highlight">¥{{ accountInfo.balance.toFixed(2) }}</div>
            <div class="stat-trend" :class="accountInfo.balance > 50 ? 'safe' : 'warning'">
              {{ accountInfo.balance > 50 ? '余额充足' : '余额不足，建议充值' }}
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <el-icon :size="28" color="#fff"><Cpu /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">本月Token消耗</div>
            <div class="stat-value">{{ formatNumber(usageStats.monthTokens) }}</div>
            <div class="stat-sub">约 ¥{{ usageStats.monthCost.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <el-icon :size="28" color="#fff"><ChatDotRound /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">本月对话次数</div>
            <div class="stat-value">{{ formatNumber(usageStats.monthConversations) }}</div>
            <div class="stat-sub">平均 ¥{{ usageStats.avgCostPerConv.toFixed(3) }}/次</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <el-icon :size="28" color="#fff"><Discount /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">剩余免费额度</div>
            <div class="stat-value">¥{{ accountInfo.freeQuota.toFixed(2) }}</div>
            <div class="stat-sub">新用户赠送 ¥20</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 当前模型配置 -->
    <el-card class="model-config-card">
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
      
      <div class="current-model">
        <div class="model-info">
          <div class="model-icon">{{ currentModel.icon }}</div>
          <div class="model-detail">
            <div class="model-name">{{ currentModel.name }}</div>
            <div class="model-provider">{{ currentModel.provider }}</div>
          </div>
          <el-tag :type="currentModel.status === 'active' ? 'success' : 'warning'" size="small">
            {{ currentModel.status === 'active' ? '运行中' : '配置中' }}
          </el-tag>
        </div>
        
        <div class="model-metrics">
          <div class="metric-item">
            <div class="metric-label">响应速度</div>
            <div class="metric-value">{{ currentModel.responseTime }}ms</div>
            <el-progress :percentage="currentModel.speedScore" :color="speedColor" :show-text="false" />
          </div>
          <div class="metric-item">
            <div class="metric-label">准确率</div>
            <div class="metric-value">{{ currentModel.accuracy }}%</div>
            <el-progress :percentage="currentModel.accuracy" :color="accuracyColor" :show-text="false" />
          </div>
          <div class="metric-item">
            <div class="metric-label">性价比</div>
            <div class="metric-value">{{ currentModel.costEfficiency }}</div>
            <el-rate :model-value="currentModel.costEfficiencyScore" disabled show-score text-color="#ff9900" />
          </div>
        </div>
        
        <div class="model-pricing">
          <div class="price-item">
            <span class="price-label">输入价格</span>
            <span class="price-value">¥{{ currentModel.inputPrice }}/千Token</span>
          </div>
          <div class="price-item">
            <span class="price-label">输出价格</span>
            <span class="price-value">¥{{ currentModel.outputPrice }}/千Token</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 用量趋势图表 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>📊 Token用量趋势（近7天）</span>
              <el-radio-group v-model="chartPeriod" size="small">
                <el-radio-button label="7d">近7天</el-radio-button>
                <el-radio-button label="30d">近30天</el-radio-button>
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
    <el-card class="model-market-card">
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
              <span class="model-icon">{{ model.icon }}</span>
              <el-tag v-if="model.isNew" type="danger" size="small" effect="dark">NEW</el-tag>
              <el-tag v-if="model.id === currentModel.id" type="success" size="small">当前使用</el-tag>
            </div>
            <div class="model-name">{{ model.name }}</div>
            <div class="model-provider">{{ model.provider }}</div>
            <div class="model-features">
              <el-tag v-for="feature in model.features" :key="feature" size="small" effect="plain">
                {{ feature }}
              </el-tag>
            </div>
            <div class="model-price">
              <span class="price">¥{{ model.inputPrice }}</span>
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
          <span class="amount">¥{{ accountInfo.balance.toFixed(2) }}</span>
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
            <el-radio label="bank">
              <div class="payment-option">
                <span class="payment-icon">🏦</span>
                <span>对公转账</span>
              </div>
            </el-radio>
          </el-radio-group>
        </div>
        
        <div class="recharge-info">
          <el-alert
            title="充值说明"
            description="充值金额将实时到账，可用于所有AI模型调用。发票可在充值完成后申请。"
            type="info"
            :closable="false"
          />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showRechargeDialog = false">取消</el-button>
        <el-button type="primary" size="large" @click="handleRecharge">
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
      
      <el-table :data="availableModels" style="width: 100%">
        <el-table-column label="模型" width="200">
          <template #default="{ row }">
            <div class="model-table-info">
              <span class="model-icon">{{ row.icon }}</span>
              <div>
                <div class="model-name">{{ row.name }}</div>
                <div class="model-provider">{{ row.provider }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="输入价格" width="120">
          <template #default="{ row }">
            ¥{{ row.inputPrice }}/千Token
          </template>
        </el-table-column>
        <el-table-column label="输出价格" width="120">
          <template #default="{ row }">
            ¥{{ row.outputPrice }}/千Token
          </template>
        </el-table-column>
        <el-table-column label="特点">
          <template #default="{ row }">
            <el-tag v-for="f in row.features.slice(0, 2)" :key="f" size="small" style="margin-right: 5px">
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

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Wallet, Cpu, ChatDotRound, Discount, SetUp, ShoppingBag, Search } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// 账户信息
const accountInfo = ref({
  balance: 156.80,
  freeQuota: 20.00,
  totalRecharged: 500.00,
  totalConsumed: 363.20
})

// 用量统计
const usageStats = ref({
  monthTokens: 1256800,
  monthCost: 45.68,
  monthConversations: 3256,
  avgCostPerConv: 0.014
})

// 当前模型
const currentModel = ref({
  id: 'kimi-k2.5',
  name: 'Kimi K2.5',
  provider: 'Moonshot',
  icon: '🌙',
  status: 'active',
  responseTime: 850,
  speedScore: 85,
  accuracy: 92,
  costEfficiency: '高',
  costEfficiencyScore: 4.5,
  inputPrice: 0.012,
  outputPrice: 0.024,
  features: ['长文本', '中文优化', '高性价比']
})

// 可用模型列表
const availableModels = ref([
  { id: 'gpt-4', name: 'GPT-4', provider: 'OpenAI', icon: '🤖', inputPrice: 0.215, outputPrice: 0.645, features: ['最强推理', '代码生成', '多语言'], isNew: false },
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'OpenAI', icon: '⚡', inputPrice: 0.036, outputPrice: 0.108, features: ['速度快', '多模态', '性价比高'], isNew: true },
  { id: 'claude-3.5', name: 'Claude 3.5', provider: 'Anthropic', icon: '🧠', inputPrice: 0.108, outputPrice: 0.538, features: ['长上下文', '安全', '创作'], isNew: false },
  { id: 'kimi-k2.5', name: 'Kimi K2.5', provider: 'Moonshot', icon: '🌙', inputPrice: 0.012, outputPrice: 0.024, features: ['长文本', '中文优化', '高性价比'], isNew: false },
  { id: 'wenxin-4', name: '文心一言4.0', provider: '百度', icon: '🔴', inputPrice: 0.060, outputPrice: 0.120, features: ['中文强', '搜索', '知识'], isNew: false },
  { id: 'qwen-max', name: '通义千问Max', provider: '阿里', icon: '🟠', inputPrice: 0.040, outputPrice: 0.080, features: ['中文强', '代码', '推理'], isNew: false },
  { id: 'doubao-pro', name: '豆包Pro', provider: '字节', icon: '🟢', inputPrice:0.008, outputPrice: 0.016, features: ['超低价', '中文', '年轻'], isNew: true },
  { id: 'glm-4', name: 'GLM-4', provider: '智谱', icon: '🔵', inputPrice: 0.050, outputPrice: 0.100, features: ['国产', '开源', '多轮'], isNew: false }
])

// 图表相关
const chartPeriod = ref('7d')
const tokenChart = ref<HTMLElement>()
const costChart = ref<HTMLElement>()

// 充值相关
const showRechargeDialog = ref(false)
const rechargeAmount = ref(100)
const customAmount = ref<number>()
const paymentMethod = ref('alipay')

// 模型选择器
const showModelSelector = ref(false)
const modelSearch = ref('')

// 计算属性
const speedColor = computed(() => {
  const score = currentModel.value.speedScore
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
})

const accuracyColor = computed(() => {
  const acc = currentModel.value.accuracy
  if (acc >= 90) return '#67c23a'
  if (acc >= 75) return '#e6a23c'
  return '#f56c6c'
})

const finalAmount = computed(() => {
  return customAmount.value || rechargeAmount.value
})

const filteredModels = computed(() => {
  if (!modelSearch.value) return availableModels.value
  const keyword = modelSearch.value.toLowerCase()
  return availableModels.value.filter(m => 
    m.name.toLowerCase().includes(keyword) || 
    m.provider.toLowerCase().includes(keyword)
  )
})

// 方法
const formatNumber = (num: number) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString()
}

const switchModel = (model: any) => {
  currentModel.value = { ...currentModel.value, ...model }
  showModelSelector.value = false
  ElMessage.success(`已切换到 ${model.name}`)
}

const handleRecharge = () => {
  const amount = finalAmount.value
  ElMessage.success(`正在跳转${paymentMethod.value === 'alipay' ? '支付宝' : paymentMethod.value === 'wechat' ? '微信支付' : '对公转账'}支付 ¥${amount}...`)
  showRechargeDialog.value = false
  // 模拟充值成功
  setTimeout(() => {
    accountInfo.value.balance += amount
    ElMessage.success(`充值成功！¥${amount} 已到账`)
  }, 2000)
}

// 初始化图表
const initCharts = () => {
  // Token趋势图
  if (tokenChart.value) {
    const chart = echarts.init(tokenChart.value)
    chart.setOption({
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
        data: [120000, 145000, 138000, 162000, 178000, 195000, 186000],
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
  if (costChart.value) {
    const chart = echarts.init(costChart.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: '5%' },
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
        data: [
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

onMounted(() => {
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

.model-metrics {
  display: flex;
  gap: 40px;
  flex: 1;
}

.metric-item {
  text-align: center;
  min-width: 120px;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
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
  
  .model-metrics {
    flex-direction: column;
    gap: 20px;
    width: 100%;
  }
  
  .metric-item {
    width: 100%;
  }
}
</style>
