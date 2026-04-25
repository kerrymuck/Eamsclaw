<template>
  <div class="ai-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #409eff;">
            <el-icon :size="28"><Cpu /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalTokens.toLocaleString() }}</div>
            <div class="stat-label">总Token消耗</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #67c23a;">
            <el-icon :size="28"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.todayTokens.toLocaleString() }}</div>
            <div class="stat-label">今日消耗</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #e6a23c;">
            <el-icon :size="28"><Money /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">¥{{ stats.totalCost.toLocaleString() }}</div>
            <div class="stat-label">累计成本</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #f56c6c;">
            <el-icon :size="28"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.alertCount }}</div>
            <div class="stat-label">告警次数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 大模型列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>大模型管理</span>
          <el-button type="primary" @click="handleAddModel">
            <el-icon><Plus /></el-icon> 新增模型
          </el-button>
        </div>
      </template>

      <el-table :data="modelList" stripe>
        <el-table-column prop="name" label="模型名称" min-width="150">
          <template #default="{ row }">
            <div class="model-info">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                {{ row.provider }}
              </el-tag>
              <span class="model-name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="modelId" label="模型ID" min-width="180" />
        <el-table-column prop="inputPrice" label="输入价格" min-width="120">
          <template #default="{ row }">
            <span class="price">¥{{ row.inputPrice }}/1K tokens</span>
          </template>
        </el-table-column>
        <el-table-column prop="outputPrice" label="输出价格" min-width="120">
          <template #default="{ row }">
            <span class="price">¥{{ row.outputPrice }}/1K tokens</span>
          </template>
        </el-table-column>
        <el-table-column prop="contextLength" label="上下文长度" min-width="120">
          <template #default="{ row }">
            {{ (row.contextLength / 1000).toFixed(0) }}K
          </template>
        </el-table-column>
        <el-table-column prop="todayUsage" label="今日调用" min-width="100" />
        <el-table-column prop="status" label="状态" min-width="80">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              active-value="active"
              inactive-value="inactive"
              @change="(val: any) => handleStatusChange(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEditModel(row)">编辑</el-button>
            <el-button link type="primary" @click="handleTest(row)">测试</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 官方价格设置 - 服务商拿货价 = 零售价 × 折扣 -->
    <el-card class="pricing-card">
      <template #header>
        <div class="card-header">
          <div>
            <span>官方AI模型价格设置</span>
            <el-tag type="warning" style="margin-left: 10px;">服务商拿货价基准</el-tag>
          </div>
          <el-button type="primary" @click="handleSavePricing">保存设置</el-button>
        </div>
      </template>

      <el-alert
        title="价格设置说明"
        description="官方零售价为服务商设置价格的基准。服务商拿货价 = 官方零售价 × 服务商等级折扣。不同等级服务商享受不同折扣。"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      />

      <el-table :data="pricingList" stripe>
        <el-table-column prop="modelName" label="模型" min-width="150" />
        <el-table-column prop="officialPrice" label="官方零售价" min-width="150">
          <template #default="{ row }">
            <el-input-number v-model="row.officialPrice" :min="0.0001" :precision="4" :step="0.001" style="width: 130px" />
          </template>
        </el-table-column>
        <el-table-column label="服务商折扣" min-width="280">
          <template #default="{ row }">
            <div class="discount-info">
              <span class="discount-tag">普通: {{ row.discounts?.normal || 100 }}%</span>
              <span class="discount-tag">铜牌: {{ row.discounts?.bronze || 85 }}%</span>
              <span class="discount-tag">银牌: {{ row.discounts?.silver || 75 }}%</span>
              <span class="discount-tag">金牌: {{ row.discounts?.gold || 60 }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 使用趋势 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>模型使用趋势</span>
          <el-radio-group v-model="chartTimeRange" size="small">
            <el-radio-button label="24h">24小时</el-radio-button>
            <el-radio-button label="7d">7天</el-radio-button>
            <el-radio-button label="30d">30天</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="usageChart" class="chart-container"></div>
    </el-card>

    <!-- 新增/编辑模型对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogType === 'add' ? '新增模型' : '编辑模型'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="模型ID" prop="modelId">
          <el-input v-model="form.modelId" placeholder="如: gpt-4-turbo" />
        </el-form-item>
        <el-form-item label="提供商" prop="provider">
          <el-select v-model="form.provider" style="width: 100%">
            <el-option label="OpenAI" value="OpenAI" />
            <el-option label="Anthropic" value="Anthropic" />
            <el-option label="百度" value="百度" />
            <el-option label="阿里" value="阿里" />
            <el-option label="智谱" value="智谱" />
            <el-option label="月之暗面" value="月之暗面" />
          </el-select>
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="form.apiKey" type="password" show-password />
        </el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="form.baseUrl" placeholder="https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="输入价格">
          <el-input-number v-model="form.inputPrice" :min="0" :precision="4" :step="0.001" style="width: 100%">
            <template #suffix>/1K tokens</template>
          </el-input-number>
        </el-form-item>
        <el-form-item label="输出价格">
          <el-input-number v-model="form.outputPrice" :min="0" :precision="4" :step="0.001" style="width: 100%">
            <template #suffix>/1K tokens</template>
          </el-input-number>
        </el-form-item>
        <el-form-item label="上下文长度">
          <el-input-number v-model="form.contextLength" :min="1000" :step="1000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="最大Tokens">
          <el-input-number v-model="form.maxTokens" :min="1000" :step="1000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { Cpu, TrendCharts, Money, Warning, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const chartTimeRange = ref('24h')
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')

const stats = reactive({
  totalTokens: 856000000,
  todayTokens: 12500000,
  totalCost: 45600,
  alertCount: 3
})

const form = reactive({
  id: '',
  name: '',
  modelId: '',
  provider: 'OpenAI',
  apiKey: '',
  baseUrl: '',
  inputPrice: 0,
  outputPrice: 0,
  contextLength: 8000,
  maxTokens: 4000,
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  modelId: [{ required: true, message: '请输入模型ID', trigger: 'blur' }],
  provider: [{ required: true, message: '请选择提供商', trigger: 'change' }]
}

const modelList = ref([
  { id: '1', name: 'GPT-4 Turbo', modelId: 'gpt-4-turbo-preview', provider: 'OpenAI', inputPrice: 0.01, outputPrice: 0.03, contextLength: 128000, todayUsage: 125000, status: 'active' },
  { id: '2', name: 'GPT-3.5 Turbo', modelId: 'gpt-3.5-turbo', provider: 'OpenAI', inputPrice: 0.0005, outputPrice: 0.0015, contextLength: 16000, todayUsage: 856000, status: 'active' },
  { id: '3', name: 'Claude 3 Opus', modelId: 'claude-3-opus', provider: 'Anthropic', inputPrice: 0.015, outputPrice: 0.075, contextLength: 200000, todayUsage: 45000, status: 'active' },
  { id: '4', name: 'Claude 3 Sonnet', modelId: 'claude-3-sonnet', provider: 'Anthropic', inputPrice: 0.003, outputPrice: 0.015, contextLength: 200000, todayUsage: 125000, status: 'active' },
  { id: '5', name: '文心一言4.0', modelId: 'ernie-bot-4', provider: '百度', inputPrice: 0.012, outputPrice: 0.012, contextLength: 8000, todayUsage: 234000, status: 'active' },
  { id: '6', name: '通义千问Max', modelId: 'qwen-max', provider: '阿里', inputPrice: 0.02, outputPrice: 0.02, contextLength: 8000, todayUsage: 156000, status: 'active' },
  { id: '7', name: 'GLM-4', modelId: 'glm-4', provider: '智谱', inputPrice: 0.01, outputPrice: 0.01, contextLength: 128000, todayUsage: 89000, status: 'active' },
  { id: '8', name: 'Kimi', modelId: 'kimi', provider: '月之暗面', inputPrice: 0.006, outputPrice: 0.006, contextLength: 200000, todayUsage: 178000, status: 'active' }
])

// 官方AI模型价格配置 - 服务商拿货价 = 零售价 × 折扣
const pricingList = ref([
  { modelName: 'GPT-4 Turbo', officialPrice: 0.215, enabled: true, discounts: { normal: 100, bronze: 85, silver: 75, gold: 60 } },
  { modelName: 'GPT-3.5 Turbo', officialPrice: 0.0215, enabled: true, discounts: { normal: 100, bronze: 85, silver: 75, gold: 60 } },
  { modelName: 'GPT-4o', officialPrice: 0.036, enabled: true, discounts: { normal: 100, bronze: 85, silver: 75, gold: 60 } },
  { modelName: 'Claude 3 Opus', officialPrice: 0.645, enabled: true, discounts: { normal: 100, bronze: 85, silver: 75, gold: 60 } },
  { modelName: 'Claude 3 Sonnet', officialPrice: 0.108, enabled: true, discounts: { normal: 100, bronze: 85, silver: 75, gold: 60 } },
  { modelName: 'Claude 3.5', officialPrice: 0.538, enabled: true, discounts: { normal: 100, bronze: 85, silver: 75, gold: 60 } },
  { modelName: '文心一言4.0', officialPrice: 0.12, enabled: true, discounts: { normal: 100, bronze: 85, silver: 75, gold: 60 } },
  { modelName: '通义千问Max', officialPrice: 0.08, enabled: true, discounts: { normal: 100, bronze: 85, silver: 75, gold: 60 } },
  { modelName: 'GLM-4', officialPrice: 0.10, enabled: true, discounts: { normal: 100, bronze: 85, silver: 75, gold: 60 } },
  { modelName: 'Kimi', officialPrice: 0.024, enabled: true, discounts: { normal: 100, bronze: 85, silver: 75, gold: 60 } },
  { modelName: '豆包Pro', officialPrice: 0.016, enabled: true, discounts: { normal: 100, bronze: 85, silver: 75, gold: 60 } }
])

const handleAddModel = () => {
  dialogType.value = 'add'
  dialogVisible.value = true
}

const handleEditModel = (row: any) => {
  dialogType.value = 'edit'
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleStatusChange = (row: any, val: any) => {
  ElMessage.success(`${row.name} 已${val === 'active' ? '启用' : '禁用'}`)
}

const handleTest = (row: any) => {
  ElMessage.success(`正在测试 ${row.name}...`)
}

const handleSubmit = () => {
  ElMessage.success(dialogType.value === 'add' ? '新增成功' : '编辑成功')
  dialogVisible.value = false
}

const handleSavePricing = () => {
  ElMessage.success('价格设置已保存')
}

// 图表
const usageChart = ref<HTMLElement>()
let usageInstance: echarts.ECharts | null = null

onMounted(() => {
  if (usageChart.value) {
    usageInstance = echarts.init(usageChart.value)
    usageInstance.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['GPT-4', 'GPT-3.5', 'Claude', '国产模型'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00']
      },
      yAxis: { type: 'value' },
      series: [
        { name: 'GPT-4', type: 'line', smooth: true, data: [120, 132, 301, 534, 890, 1230, 1210], itemStyle: { color: '#409EFF' } },
        { name: 'GPT-3.5', type: 'line', smooth: true, data: [220, 382, 591, 834, 1190, 1330, 1310], itemStyle: { color: '#67C23A' } },
        { name: 'Claude', type: 'line', smooth: true, data: [150, 232, 401, 654, 990, 1130, 1110], itemStyle: { color: '#E6A23C' } },
        { name: '国产模型', type: 'line', smooth: true, data: [320, 432, 601, 834, 1090, 1230, 1210], itemStyle: { color: '#F56C6C' } }
      ]
    })
  }
})

onUnmounted(() => {
  usageInstance?.dispose()
})
</script>

<style scoped>
.ai-container {
  padding: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 15px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.table-card, .pricing-card, .chart-card {
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
  gap: 10px;
}

.model-name {
  font-weight: 500;
}

.price {
  color: #f56c6c;
  font-weight: bold;
}

.cost-price {
  color: #f56c6c;
  font-weight: bold;
}

.profit {
  color: #67c23a;
  font-weight: bold;
}

.discount-info {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.discount-tag {
  padding: 2px 6px;
  background: #f0f9ff;
  border: 1px solid #91d5ff;
  border-radius: 4px;
  font-size: 12px;
  color: #1890ff;
}

.chart-container {
  height: 350px;
}
</style>
