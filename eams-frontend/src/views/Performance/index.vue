<template>
  <div class="performance-center">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>📊 绩效管理</h2>
        <p class="subtitle">客服团队数据可视化，量化考核有据可依</p>
      </div>
      <div class="header-actions">
        <el-radio-group v-model="timeRange" size="large">
          <el-radio-button label="today">今日</el-radio-button>
          <el-radio-button label="week">本周</el-radio-button>
          <el-radio-button label="month">本月</el-radio-button>
        </el-radio-group>
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          导出报表
        </el-button>
      </div>
    </div>

    <!-- 团队概览 -->
    <el-row :gutter="16" class="overview-row">
      <el-col :xs="12" :sm="6" :md="4" v-for="stat in teamStats" :key="stat.label">
        <el-card class="stat-card" :class="stat.type">
          <div class="stat-icon">{{ stat.icon }}</div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-compare" :class="stat.trend">
              {{ stat.compare }}
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>📈 客服工作量趋势</span>
              <el-radio-group v-model="chartMetric" size="small">
                <el-radio-button label="conversations">对话数</el-radio-button>
                <el-radio-button label="response">响应时长</el-radio-button>
                <el-radio-button label="satisfaction">满意度</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="workloadChart" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <span>🏆 客服绩效排名</span>
          </template>
          <div class="ranking-list">
            <div v-for="(item, index) in rankingList" :key="item.id" class="rank-item">
              <div class="rank-number" :class="{ 'top3': index < 3 }">{{ index + 1 }}</div>
              <el-avatar :size="40" :src="item.avatar">{{ item.name.charAt(0) }}</el-avatar>
              <div class="rank-info">
                <div class="name">{{ item.name }}</div>
                <div class="score">综合评分 {{ item.score }}分</div>
              </div>
              <div class="rank-metrics">
                <div class="metric">
                  <span class="label">响应</span>
                  <span class="value">{{ item.avgResponse }}s</span>
                </div>
                <div class="metric">
                  <span class="label">解决</span>
                  <span class="value">{{ item.resolveRate }}%</span>
                </div>
                <div class="metric">
                  <span class="label">满意</span>
                  <span class="value">{{ item.satisfaction }}%</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 客服明细表格 -->
    <el-card class="detail-card">
      <template #header>
        <div class="card-header">
          <span>👥 客服绩效明细</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索客服"
              :prefix-icon="Search"
              style="width: 200px"
              size="small"
            />
            <el-button type="primary" size="small" @click="showSettingsDialog = true">
              <el-icon><Setting /></el-icon>
              考核设置
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="filteredAgents" stripe v-loading="loading">
        <el-table-column label="客服" min-width="150" fixed="left">
          <template #default="{ row }">
            <div class="agent-info">
              <el-avatar :size="36" :src="row.avatar">{{ row.name.charAt(0) }}</el-avatar>
              <div class="agent-detail">
                <div class="name">{{ row.name }}</div>
                <div class="role">{{ row.role }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="在线时长" width="120" align="center">
          <template #default="{ row }">
            <div class="time-cell">{{ row.onlineTime }}</div>
          </template>
        </el-table-column>
        
        <el-table-column label="对话数" width="100" align="center">
          <template #default="{ row }">
            <div class="number-cell">{{ row.conversations }}</div>
          </template>
        </el-table-column>
        
        <el-table-column label="平均响应" width="120" align="center">
          <template #default="{ row }">
            <div class="response-cell" :class="getResponseClass(row.avgResponse)">
              {{ row.avgResponse }}s
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="解决率" width="120" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.resolveRate" :color="getProgressColor" :show-text="false" style="width: 80px" />
            <div class="rate-text">{{ row.resolveRate }}%</div>
          </template>
        </el-table-column>
        
        <el-table-column label="满意度" width="120" align="center">
          <template #default="{ row }">
            <div class="satisfaction-cell">
              <el-rate :model-value="row.satisfaction / 20" disabled show-score text-color="#ff9900" score-template="{value}" />
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="工单处理" width="120" align="center">
          <template #default="{ row }">
            <div class="ticket-cell">
              <span class="completed">{{ row.ticketsResolved }}</span>
              <span class="total">/{{ row.ticketsTotal }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="综合评分" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <div class="score-cell" :class="getScoreClass(row.score)">
              {{ row.score }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next"
        />
      </div>
    </el-card>

    <!-- 考核设置对话框 -->
    <el-dialog v-model="showSettingsDialog" title="绩效考核设置" width="600px">
      <el-form :model="settingsForm" label-width="120px">
        <el-divider>权重配置</el-divider>
        <el-form-item label="响应时长">
          <el-slider v-model="settingsForm.responseWeight" :min="0" :max="100" show-input />
          <div class="setting-tip">首次响应时间权重，建议20-30%</div>
        </el-form-item>
        <el-form-item label="解决率">
          <el-slider v-model="settingsForm.resolveWeight" :min="0" :max="100" show-input />
          <div class="setting-tip">问题解决率权重，建议30-40%</div>
        </el-form-item>
        <el-form-item label="满意度">
          <el-slider v-model="settingsForm.satisfactionWeight" :min="0" :max="100" show-input />
          <div class="setting-tip">客户满意度权重，建议30-40%</div>
        </el-form-item>
        <el-form-item label="工作量">
          <el-slider v-model="settingsForm.workloadWeight" :min="0" :max="100" show-input />
          <div class="setting-tip">对话数量权重，建议10-20%</div>
        </el-form-item>
        
        <el-divider>达标标准</el-divider>
        <el-form-item label="响应时长标准">
          <el-input-number v-model="settingsForm.responseStandard" :min="5" :max="300" :step="5">
            <template #suffix>秒</template>
          </el-input-number>
          <div class="setting-tip">平均首次响应时间应小于此值</div>
        </el-form-item>
        <el-form-item label="解决率标准">
          <el-input-number v-model="settingsForm.resolveStandard" :min="50" :max="100" :step="5">
            <template #suffix>%</template>
          </el-input-number>
          <div class="setting-tip">问题解决率应高于此值</div>
        </el-form-item>
        <el-form-item label="满意度标准">
          <el-input-number v-model="settingsForm.satisfactionStandard" :min="3" :max="5" :step="0.1">
            <template #suffix>分</template>
          </el-input-number>
          <div class="setting-tip">客户满意度应高于此值（5分制）</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSettingsDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
      </template>
    </el-dialog>

    <!-- 客服详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="客服绩效详情" width="800px">
      <div v-if="currentAgent" class="agent-detail-panel">
        <div class="detail-header">
          <el-avatar :size="64" :src="currentAgent.avatar">{{ currentAgent.name.charAt(0) }}</el-avatar>
          <div class="header-info">
            <h3>{{ currentAgent.name }}</h3>
            <p>{{ currentAgent.role }} | 入职时间：{{ currentAgent.joinDate }}</p>
          </div>
          <div class="header-score">
            <div class="score-value">{{ currentAgent.score }}</div>
            <div class="score-label">综合评分</div>
          </div>
        </div>
        
        <el-row :gutter="20" class="detail-stats">
          <el-col :span="8" v-for="item in detailStats" :key="item.label">
            <div class="detail-stat-item">
              <div class="stat-value">{{ item.value }}</div>
              <div class="stat-label">{{ item.label }}</div>
              <div class="stat-compare" :class="item.trend">{{ item.compare }}</div>
            </div>
          </el-col>
        </el-row>
        
        <el-card class="trend-card">
          <template #header>
            <span>近7天绩效趋势</span>
          </template>
          <div ref="trendChart" class="trend-chart"></div>
        </el-card>
        
        <el-card class="evaluation-card">
          <template #header>
            <span>💬 客户评价</span>
          </template>
          <div class="evaluation-list">
            <div v-for="item in currentAgent.evaluations" :key="item.id" class="evaluation-item">
              <div class="eval-header">
                <el-rate :model-value="item.rating" disabled show-score />
                <span class="eval-time">{{ item.time }}</span>
              </div>
              <p class="eval-content">{{ item.content }}</p>
              <div class="eval-tags">
                <el-tag v-for="tag in item.tags" :key="tag" size="small">{{ tag }}</el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search, Setting } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const timeRange = ref('today')
const chartMetric = ref('conversations')
const searchKeyword = ref('')
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(8)

const showSettingsDialog = ref(false)
const showDetailDialog = ref(false)
const currentAgent = ref<any>(null)

const settingsForm = ref({
  responseWeight: 25,
  resolveWeight: 35,
  satisfactionWeight: 30,
  workloadWeight: 10,
  responseStandard: 30,
  resolveStandard: 85,
  satisfactionStandard: 4.5
})

// 团队统计数据
const teamStats = ref([
  { icon: '👥', label: '在线客服', value: 8, compare: '较昨日 +1', trend: 'up', type: '' },
  { icon: '💬', label: '今日对话', value: 3256, compare: '较昨日 +12%', trend: 'up', type: '' },
  { icon: '⚡', label: '平均响应', value: '18s', compare: '较昨日 -3s', trend: 'up', type: 'success' },
  { icon: '✅', label: '解决率', value: '92.5%', compare: '较昨日 +2.3%', trend: 'up', type: 'success' },
  { icon: '⭐', label: '满意度', value: '4.8', compare: '较昨日 +0.1', trend: 'up', type: 'success' },
  { icon: '🎫', label: '待处理工单', value: 23, compare: '较昨日 -5', trend: 'down', type: 'warning' }
])

// 排名数据
const rankingList = ref([
  { id: '1', name: '张三', avatar: '', score: 96, avgResponse: 12, resolveRate: 98, satisfaction: 98 },
  { id: '2', name: '李四', avatar: '', score: 94, avgResponse: 15, resolveRate: 95, satisfaction: 96 },
  { id: '3', name: '王五', avatar: '', score: 92, avgResponse: 18, resolveRate: 93, satisfaction: 95 },
  { id: '4', name: '赵六', avatar: '', score: 88, avgResponse: 22, resolveRate: 90, satisfaction: 92 },
  { id: '5', name: '钱七', avatar: '', score: 85, avgResponse: 25, resolveRate: 88, satisfaction: 90 }
])

// 客服明细数据
const agents = ref([
  { id: '1', name: '张三', role: '高级客服', avatar: '', onlineTime: '8h 32m', conversations: 156, avgResponse: 12, resolveRate: 98, satisfaction: 98, ticketsResolved: 23, ticketsTotal: 25, score: 96, joinDate: '2023-06-01' },
  { id: '2', name: '李四', role: '资深客服', avatar: '', onlineTime: '7h 45m', conversations: 142, avgResponse: 15, resolveRate: 95, satisfaction: 96, ticketsResolved: 20, ticketsTotal: 22, score: 94, joinDate: '2023-08-15' },
  { id: '3', name: '王五', role: '客服专员', avatar: '', onlineTime: '8h 10m', conversations: 138, avgResponse: 18, resolveRate: 93, satisfaction: 95, ticketsResolved: 18, ticketsTotal: 20, score: 92, joinDate: '2024-01-10' },
  { id: '4', name: '赵六', role: '客服专员', avatar: '', onlineTime: '6h 50m', conversations: 98, avgResponse: 22, resolveRate: 90, satisfaction: 92, ticketsResolved: 15, ticketsTotal: 18, score: 88, joinDate: '2024-02-20' },
  { id: '5', name: '钱七', role: '实习客服', avatar: '', onlineTime: '5h 30m', conversations: 76, avgResponse: 25, resolveRate: 88, satisfaction: 90, ticketsResolved: 10, ticketsTotal: 14, score: 85, joinDate: '2024-03-01' }
])

const filteredAgents = computed(() => {
  if (!searchKeyword.value) return agents.value
  return agents.value.filter(a => a.name.includes(searchKeyword.value))
})

const getResponseClass = (time: number) => {
  if (time <= 15) return 'excellent'
  if (time <= 30) return 'good'
  if (time <= 60) return 'normal'
  return 'poor'
}

const getScoreClass = (score: number) => {
  if (score >= 95) return 'excellent'
  if (score >= 85) return 'good'
  if (score >= 70) return 'normal'
  return 'poor'
}

const getProgressColor = (percentage: number) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 80) return '#e6a23c'
  return '#f56c6c'
}

const exportReport = () => {
  ElMessage.success('绩效报表导出成功')
}

const saveSettings = () => {
  ElMessage.success('考核设置已保存')
  showSettingsDialog.value = false
}

const viewDetail = (row: any) => {
  currentAgent.value = {
    ...row,
    evaluations: [
      { id: '1', rating: 5, time: '2024-03-23 14:30', content: '客服态度很好，问题解决很快，非常满意！', tags: ['响应快', '态度好'] },
      { id: '2', rating: 5, time: '2024-03-23 11:20', content: '专业高效，一次就解决了我的问题', tags: ['专业', '高效'] },
      { id: '3', rating: 4, time: '2024-03-22 16:45', content: '整体不错，就是回复稍微慢了一点', tags: ['有耐心'] }
    ]
  }
  showDetailDialog.value = true
  nextTick(() => initTrendChart())
}

const detailStats = computed(() => [
  { value: currentAgent.value?.conversations, label: '今日对话', compare: '+12%', trend: 'up' },
  { value: currentAgent.value?.avgResponse + 's', label: '平均响应', compare: '-3s', trend: 'up' },
  { value: currentAgent.value?.satisfaction + '%', label: '满意度', compare: '+2%', trend: 'up' }
])

const workloadChart = ref<HTMLElement>()
const trendChart = ref<HTMLElement>()

const initWorkloadChart = () => {
  if (!workloadChart.value) return
  const chart = echarts.init(workloadChart.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['张三', '李四', '王五', '赵六', '钱七'] },
    xAxis: { type: 'category', data: ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00'] },
    yAxis: { type: 'value' },
    series: [
      { name: '张三', type: 'line', smooth: true, data: [12, 18, 25, 20, 28, 32, 26, 22, 18, 15] },
      { name: '李四', type: 'line', smooth: true, data: [10, 15, 22, 18, 25, 28, 24, 20, 16, 12] },
      { name: '王五', type: 'line', smooth: true, data: [8, 14, 20, 16, 22, 26, 22, 18, 14, 10] }
    ]
  })
}

const initTrendChart = () => {
  if (!trendChart.value) return
  const chart = echarts.init(trendChart.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
    yAxis: { type: 'value', min: 80, max: 100 },
    series: [
      { name: '综合评分', type: 'line', smooth: true, data: [92, 93, 94, 93, 95, 96, 96], itemStyle: { color: '#667eea' }, areaStyle: { opacity: 0.3 } },
      { name: '解决率', type: 'line', smooth: true, data: [94, 95, 96, 95, 97, 98, 98], itemStyle: { color: '#43e97b' } },
      { name: '满意度', type: 'line', smooth: true, data: [90, 91, 92, 93, 94, 95, 96], itemStyle: { color: '#f093fb' } }
    ]
  })
}

onMounted(() => {
  nextTick(() => initWorkloadChart())
})
</script>

<style scoped>
.performance-center { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left h2 { margin: 0 0 8px 0; }
.subtitle { color: #909399; margin: 0; }
.header-actions { display: flex; gap: 12px; }
.overview-row { margin-bottom: 20px; }
.stat-card { display: flex; align-items: center; padding: 16px; transition: all 0.3s; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.stat-icon { font-size: 32px; margin-right: 12px; }
.stat-info { flex: 1; }
.stat-value { font-size: 24px; font-weight: bold; color: #303133; }
.stat-label { font-size: 13px; color: #909399; margin-top: 2px; }
.stat-compare { font-size: 12px; margin-top: 4px; }
.stat-compare.up { color: #67c23a; }
.stat-compare.down { color: #f56c6c; }
.charts-row { margin-bottom: 20px; }
.chart-card { height: 450px; }
.chart-container { height: 360px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.ranking-list { max-height: 360px; overflow-y: auto; }
.rank-item { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #ebeef5; }
.rank-item:last-child { border-bottom: none; }
.rank-number { width: 28px; height: 28px; border-radius: 50%; background: #f5f7fa; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #909399; margin-right: 12px; }
.rank-number.top3 { background: linear-gradient(135deg, #ffd700 0%, #ffb700 100%); color: #fff; }
.rank-info { flex: 1; margin-left: 12px; }
.rank-info .name { font-weight: 500; color: #303133; }
.rank-info .score { font-size: 12px; color: #909399; }
.rank-metrics { display: flex; gap: 16px; }
.rank-metrics .metric { text-align: center; }
.rank-metrics .metric .label { font-size: 11px; color: #909399; display: block; }
.rank-metrics .metric .value { font-size: 13px; color: #303133; font-weight: 500; }
.detail-card { margin-bottom: 20px; }
.agent-info { display: flex; align-items: center; gap: 10px; }
.agent-detail .name { font-weight: 500; color: #303133; }
.agent-detail .role { font-size: 12px; color: #909399; }
.time-cell { color: #606266; }
.number-cell { font-weight: 500; color: #303133; }
.response-cell { font-weight: 500; }
.response-cell.excellent { color: #67c23a; }
.response-cell.good { color: #409eff; }
.response-cell.normal { color: #e6a23c; }
.response-cell.poor { color: #f56c6c; }
.rate-text { font-size: 12px; color: #606266; margin-top: 4px; }
.satisfaction-cell { display: flex; justify-content: center; }
.ticket-cell .completed { font-weight: 500; color: #67c23a; }
.ticket-cell .total { color: #909399; }
.score-cell { font-size: 20px; font-weight: bold; }
.score-cell.excellent { color: #67c23a; }
.score-cell.good { color: #409eff; }
.score-cell.normal { color: #e6a23c; }
.score-cell.poor { color: #f56c6c; }
.pagination { display: flex; justify-content: flex-end; margin-top: 20px; }
.setting-tip { font-size: 12px; color: #909399; margin-top: 4px; }
.agent-detail-panel { padding: 20px; }
.detail-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid #ebeef5; }
.header-info h3 { margin: 0 0 4px 0; }
.header-info p { margin: 0; color: #909399; font-size: 14px; }
.header-score { margin-left: auto; text-align: center; }
.header-score .score-value { font-size: 48px; font-weight: bold; color: #667eea; line-height: 1; }
.header-score .score-label { font-size: 14px; color: #909399; margin-top: 4px; }
.detail-stats { margin-bottom: 20px; }
.detail-stat-item { text-align: center; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.detail-stat-item .stat-value { font-size: 24px; font-weight: bold; color: #303133; }
.detail-stat-item .stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
.detail-stat-item .stat-compare { font-size: 12px; margin-top: 4px; }
.detail-stat-item .stat-compare.up { color: #67c23a; }
.trend-card { margin-bottom: 20px; }
.trend-chart { height: 250px; }
.evaluation-card .evaluation-list { max-height: 300px; overflow-y: auto; }
.evaluation-item { padding: 16px; border-bottom: 1px solid #ebeef5; }
.evaluation-item:last-child { border-bottom: none; }
.eval-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.eval-time { font-size: 12px; color: #909399; }
.eval-content { color: #606266; margin: 8px 0; line-height: 1.6; }
.eval-tags { display: flex; gap: 8px; flex-wrap: wrap; }
</style>
