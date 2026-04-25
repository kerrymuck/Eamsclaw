<template>
  <div class="ai-power-management">
    <div class="page-header">
      <h2>🤖 AI算力管理</h2>
      <p class="subtitle">管理AI算力使用情况和价格配置</p>
    </div>

    <!-- 算力统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="stat-card">
          <div class="stat-icon purple">⚡</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalTokens }}</div>
            <div class="stat-label">总Token消耗</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="stat-card">
          <div class="stat-icon blue">💰</div>
          <div class="stat-info">
            <div class="stat-value">¥{{ stats.totalCost }}</div>
            <div class="stat-label">累计费用</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="stat-card">
          <div class="stat-icon green">📊</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.monthTokens }}</div>
            <div class="stat-label">本月消耗</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 官方价格与拿货价说明 -->
    <el-card class="price-info-card">
      <template #header>
        <span>💡 我的AI算力价格权限</span>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="服务商等级">{{ providerInfo.level }}</el-descriptions-item>
        <el-descriptions-item label="享受折扣">{{ providerInfo.discount }}%</el-descriptions-item>
        <el-descriptions-item label="拿货价计算">官方零售价 × {{ providerInfo.discount }}%</el-descriptions-item>
        <el-descriptions-item label="设置限制" :span="3">
          <el-alert
            title="您设置的价格不能低于拿货价（官方零售价 × 您的折扣）"
            type="warning"
            :closable="false"
            show-icon
          />
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 模型价格配置 -->
    <el-card class="price-card">
      <template #header>
        <div class="card-header">
          <div>
            <span>AI模型价格配置</span>
            <el-tag type="info" style="margin-left: 10px;">设置的价格将显示在商户后台</el-tag>
          </div>
          <el-button type="primary" @click="savePrices">保存配置</el-button>
        </div>
      </template>

      <el-table :data="modelPrices" style="width: 100%" v-loading="loading">
        <el-table-column prop="model" label="模型名称" min-width="180">
          <template #default="{ row }">
            <div class="model-info">
              <span class="model-name">{{ row.name }}</span>
              <el-tag size="small" :type="row.enabled ? 'success' : 'info'">
                {{ row.enabled ? '启用' : '禁用' }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="官方零售价" min-width="120">
          <template #default="{ row }">
            <span class="official-price">¥{{ row.officialPrice }}</span>
          </template>
        </el-table-column>
        <el-table-column label="我的拿货价" min-width="120">
          <template #default="{ row }">
            <span class="cost-price">¥{{ row.purchasePrice.toFixed(4) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="输入价格" min-width="180">
          <template #default="{ row }">
            <el-input-number
              v-model="row.inputPrice"
              :min="row.purchasePrice"
              :precision="4"
              :step="0.001"
              style="width: 120px"
              @change="(val: number) => validatePrice(row, val, 'input')"
            />
            <span class="price-hint" v-if="row.inputPrice <= row.purchasePrice" style="color: #f56c6c; margin-left: 5px;">不得低于拿货价</span>
          </template>
        </el-table-column>
        <el-table-column label="输出价格" min-width="180">
          <template #default="{ row }">
            <el-input-number
              v-model="row.outputPrice"
              :min="row.purchasePrice * 2"
              :precision="4"
              :step="0.001"
              style="width: 120px"
              @change="(val: number) => validatePrice(row, val, 'output')"
            />
            <span class="price-hint" v-if="row.outputPrice <= row.purchasePrice * 2" style="color: #f56c6c; margin-left: 5px;">不得低于拿货价</span>
          </template>
        </el-table-column>
        <el-table-column label="利润率" min-width="100">
          <template #default="{ row }">
            <span class="profit-rate">{{ calculateProfitRate(row) }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 使用统计 -->
    <el-card class="usage-card">
      <template #header>
        <span>使用统计</span>
      </template>
      <el-table :data="usageStats" stripe>
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="model" label="模型" min-width="150" />
        <el-table-column prop="inputTokens" label="输入Tokens" width="150" />
        <el-table-column prop="outputTokens" label="输出Tokens" width="150" />
        <el-table-column prop="cost" label="费用" width="120">
          <template #default="{ row }">
            <span class="cost">¥{{ row.cost }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const stats = ref({
  totalTokens: '8,520,000',
  totalCost: '12,580',
  monthTokens: '1,250,000'
})

// 服务商信息
const providerInfo = reactive({
  level: '银牌服务商',
  discount: 75,  // 75% = 7.5折
  levelCode: 'silver'
})

const loading = ref(false)

// 官方AI模型价格配置（从超管后台同步）
const officialPrices = ref([
  { name: 'GPT-4', officialPrice: 0.215 },
  { name: 'GPT-3.5-Turbo', officialPrice: 0.0215 },
  { name: 'GPT-4o', officialPrice: 0.036 },
  { name: 'Claude-3-Opus', officialPrice: 0.645 },
  { name: 'Claude-3-Sonnet', officialPrice: 0.108 },
  { name: 'Claude-3.5', officialPrice: 0.538 },
  { name: '文心一言4.0', officialPrice: 0.12 },
  { name: '通义千问Max', officialPrice: 0.08 },
  { name: 'GLM-4', officialPrice: 0.10 },
  { name: 'Kimi', officialPrice: 0.024 },
  { name: '豆包Pro', officialPrice: 0.016 }
])

// 服务商设置的模型价格（带拿货价计算）
const modelPrices = ref([
  { name: 'GPT-4', officialPrice: 0.215, purchasePrice: 0.16125, inputPrice: 0.20, outputPrice: 0.40, enabled: true },
  { name: 'GPT-3.5-Turbo', officialPrice: 0.0215, purchasePrice: 0.016125, inputPrice: 0.025, outputPrice: 0.05, enabled: true },
  { name: 'GPT-4o', officialPrice: 0.036, purchasePrice: 0.027, inputPrice: 0.04, outputPrice: 0.08, enabled: true },
  { name: 'Claude-3-Opus', officialPrice: 0.645, purchasePrice: 0.48375, inputPrice: 0.60, outputPrice: 1.20, enabled: true },
  { name: 'Claude-3-Sonnet', officialPrice: 0.108, purchasePrice: 0.081, inputPrice: 0.12, outputPrice: 0.24, enabled: true },
  { name: 'Claude-3.5', officialPrice: 0.538, purchasePrice: 0.4035, inputPrice: 0.50, outputPrice: 1.00, enabled: true },
  { name: '文心一言4.0', officialPrice: 0.12, purchasePrice: 0.09, inputPrice: 0.12, outputPrice: 0.24, enabled: true },
  { name: '通义千问Max', officialPrice: 0.08, purchasePrice: 0.06, inputPrice: 0.10, outputPrice: 0.20, enabled: true },
  { name: 'GLM-4', officialPrice: 0.10, purchasePrice: 0.075, inputPrice: 0.10, outputPrice: 0.20, enabled: true },
  { name: 'Kimi', officialPrice: 0.024, purchasePrice: 0.018, inputPrice: 0.03, outputPrice: 0.06, enabled: true },
  { name: '豆包Pro', officialPrice: 0.016, purchasePrice: 0.012, inputPrice: 0.02, outputPrice: 0.04, enabled: true }
])

// 计算拿货价（官方零售价 × 服务商折扣）
const calculatePurchasePrice = (officialPrice: number) => {
  return officialPrice * (providerInfo.discount / 100)
}

// 初始化拿货价
const initPurchasePrices = () => {
  modelPrices.value.forEach(model => {
    const official = officialPrices.value.find(o => o.name === model.name)
    if (official) {
      model.purchasePrice = calculatePurchasePrice(official.officialPrice)
    }
  })
}

// 验证价格不能低于拿货价
const validatePrice = (row: any, val: number, type: 'input' | 'output') => {
  const minPrice = type === 'input' ? row.purchasePrice : row.purchasePrice * 2
  if (val < minPrice) {
    ElMessage.warning(`${type === 'input' ? '输入' : '输出'}价格不能低于拿货价 ¥${minPrice.toFixed(4)}`)
    if (type === 'input') {
      row.inputPrice = minPrice
    } else {
      row.outputPrice = minPrice
    }
  }
}

// 计算利润率
const calculateProfitRate = (row: any) => {
  const inputProfit = ((row.inputPrice - row.purchasePrice) / row.purchasePrice * 100)
  const outputProfit = ((row.outputPrice - row.purchasePrice * 2) / (row.purchasePrice * 2) * 100)
  return ((inputProfit + outputProfit) / 2).toFixed(1)
}

const usageStats = ref([
  { date: '2026-04-10', model: 'GPT-4', inputTokens: '125,000', outputTokens: '45,000', cost: '6.45' },
  { date: '2026-04-10', model: 'GPT-3.5-Turbo', inputTokens: '320,000', outputTokens: '180,000', cost: '0.84' },
  { date: '2026-04-09', model: 'GPT-4', inputTokens: '98,000', outputTokens: '32,000', cost: '4.86' }
])

const savePrices = () => {
  // 验证所有价格不低于拿货价
  for (const model of modelPrices.value) {
    if (model.inputPrice < model.purchasePrice) {
      ElMessage.error(`${model.name} 输入价格不能低于拿货价 ¥${model.purchasePrice.toFixed(4)}`)
      return
    }
    if (model.outputPrice < model.purchasePrice * 2) {
      ElMessage.error(`${model.name} 输出价格不能低于拿货价 ¥${(model.purchasePrice * 2).toFixed(4)}`)
      return
    }
  }
  ElMessage.success('价格配置已保存，已同步到商户后台')
}

// 初始化
initPurchasePrices()
</script>

<style scoped>
.ai-power-management {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
}

.subtitle {
  color: #909399;
  margin: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 12px;
}

.stat-icon.purple { background: #f9f0ff; color: #722ed1; }
.stat-icon.blue { background: #e6f7ff; color: #1677ff; }
.stat-icon.green { background: #f6ffed; color: #52c41a; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.price-info-card {
  margin-bottom: 20px;
}

.price-card, .usage-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-name {
  font-weight: 500;
}

.official-price {
  color: #909399;
  text-decoration: line-through;
}

.cost-price {
  color: #e6a23c;
  font-weight: bold;
}

.profit-rate {
  color: #67c23a;
  font-weight: bold;
}

.price-hint {
  font-size: 12px;
}

.cost {
  color: #ff4d4f;
  font-weight: 500;
}
</style>
