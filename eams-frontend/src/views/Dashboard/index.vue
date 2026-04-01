<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col 
        :xs="24" 
        :sm="12" 
        :md="6" 
        :lg="6" 
        v-for="stat in statsCards" 
        :key="stat.title"
        class="stat-col"
      >
        <el-card class="stat-card" :body-style="{ padding: '20px' }">
          <div class="stat-icon" :style="{ background: stat.color }">
            <el-icon :size="28"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.title }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :sm="24" :md="24" :lg="12" class="chart-col">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>24小时对话趋势</span>
              <el-radio-group v-model="timeRange" size="small">
                <el-radio-button label="today">今日</el-radio-button>
                <el-radio-button label="week">本周</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="hourlyChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="24" :lg="12" class="chart-col">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>意图分布</span>
            </div>
          </template>
          <div ref="intentChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 平台分布和满意度 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :sm="24" :md="24" :lg="12" class="chart-col">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>平台分布</span>
            </div>
          </template>
          <div ref="platformChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="24" :lg="12" class="chart-col">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>满意度评分</span>
            </div>
          </template>
          <div class="satisfaction">
            <div class="score">{{ mockStore.dashboard.satisfaction_score }}</div>
            <el-rate
              :model-value="mockStore.dashboard.satisfaction_score"
              disabled
              show-score
              text-color="#ff9900"
            />
            <div class="detail">
              <div class="feedback-item">
                <span class="label">好评</span>
                <el-progress :percentage="85" status="success" :stroke-width="16" />
                <span class="count">{{ mockStore.dashboard.positive_feedback }}</span>
              </div>
              <div class="feedback-item">
                <span class="label">中评</span>
                <el-progress :percentage="12" :stroke-width="16" />
                <span class="count">{{ mockStore.dashboard.neutral_feedback }}</span>
              </div>
              <div class="feedback-item">
                <span class="label">差评</span>
                <el-progress :percentage="3" status="exception" :stroke-width="16" />
                <span class="count">{{ mockStore.dashboard.negative_feedback }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时会话动态 -->
    <el-row :gutter="20" class="activity-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Bell /></el-icon> 实时会话动态
                <el-tag type="success" effect="dark" class="live-tag">LIVE</el-tag>
              </span>
              <el-button type="primary" size="small" @click="refreshData">
                <el-icon><Refresh /></el-icon> 刷新
              </el-button>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in recentActivities"
              :key="index"
              :type="activity.type"
              :timestamp="activity.time"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import { 
  ChatDotRound, CircleCheck, User, Timer, 
  Bell, Refresh 
} from '@element-plus/icons-vue'
import { useMockStore } from '@/stores/mock'

const mockStore = useMockStore()
const timeRange = ref('today')

const statsCards = computed(() => [
  {
    title: '总会话数',
    value: mockStore.dashboard.total_conversations,
    icon: 'ChatDotRound',
    color: '#409EFF'
  },
  {
    title: '已解决',
    value: mockStore.dashboard.resolved_conversations,
    icon: 'CircleCheck',
    color: '#67C23A'
  },
  {
    title: '进行中',
    value: mockStore.dashboard.active_conversations,
    icon: 'User',
    color: '#E6A23C'
  },
  {
    title: '平均响应',
    value: mockStore.dashboard.avg_response_time,
    icon: 'Timer',
    color: '#F56C6C'
  }
])

const recentActivities = ref([
  { content: '买家小王 发起了新对话', time: '2分钟前', type: 'primary' },
  { content: 'AI自动回复了 买家李女士 的咨询', time: '5分钟前', type: 'success' },
  { content: '买家张先生 的会话已转人工', time: '8分钟前', type: 'warning' },
  { content: '买家小王 的会话已结束', time: '15分钟前', type: 'info' },
  { content: '系统：日统计报告已生成', time: '1小时前', type: 'info' }
])

const hourlyChart = ref<HTMLElement>()
const intentChart = ref<HTMLElement>()
const platformChart = ref<HTMLElement>()

let hourlyInstance: echarts.ECharts | null = null
let intentInstance: echarts.ECharts | null = null
let platformInstance: echarts.ECharts | null = null

const initCharts = () => {
  // 24小时趋势图
  if (hourlyChart.value) {
    hourlyInstance = echarts.init(hourlyChart.value)
    hourlyInstance.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: mockStore.dashboard.hourly_stats.map((item: any) => item.hour)
      },
      yAxis: { type: 'value' },
      series: [{
        name: '会话数',
        type: 'line',
        smooth: true,
        data: mockStore.dashboard.hourly_stats.map((item: any) => item.count),
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        },
        itemStyle: { color: '#409EFF' }
      }]
    })
  }

  // 意图分布饼图
  if (intentChart.value) {
    intentInstance = echarts.init(intentChart.value)
    intentInstance.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
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
        emphasis: {
          label: { show: true, fontSize: 16, fontWeight: 'bold' }
        },
        data: mockStore.dashboard.intent_distribution
      }]
    })
  }

  // 平台分布饼图
  if (platformChart.value) {
    platformInstance = echarts.init(platformChart.value)
    platformInstance.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      series: [{
        type: 'pie',
        radius: '60%',
        data: mockStore.dashboard.platform_distribution,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  }
}

const handleResize = () => {
  hourlyInstance?.resize()
  intentInstance?.resize()
  platformInstance?.resize()
}

const refreshData = () => {
  // 模拟刷新数据
  recentActivities.value.unshift({
    content: '数据已刷新',
    time: '刚刚',
    type: 'success'
  })
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  hourlyInstance?.dispose()
  intentInstance?.dispose()
  platformInstance?.dispose()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

/* 统计卡片响应式 */
.stats-row {
  margin-bottom: 20px;
}

.stat-col {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 15px;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

/* 图表区域 */
.charts-row {
  margin-bottom: 20px;
}

.chart-col {
  margin-bottom: 20px;
}

.chart-card {
  height: 100%;
}

.chart-container {
  height: 300px;
  min-height: 250px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.satisfaction {
  text-align: center;
  padding: 20px 0;
}

.score {
  font-size: 56px;
  font-weight: bold;
  color: #409EFF;
  line-height: 1;
}

.detail {
  margin-top: 30px;
  padding: 0 20px;
}

.feedback-item {
  display: flex;
  align-items: center;
  margin: 15px 0;
  gap: 10px;
}

.feedback-item .label {
  width: 40px;
  text-align: right;
  color: #606266;
  flex-shrink: 0;
}

.feedback-item :deep(.el-progress) {
  flex: 1;
  min-width: 0;
}

.feedback-item .count {
  width: 50px;
  text-align: left;
  color: #909399;
  flex-shrink: 0;
}

.live-tag {
  margin-left: 10px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }
  
  .stat-card {
    padding: 15px;
  }
  
  .stat-icon {
    width: 48px;
    height: 48px;
  }
  
  .stat-value {
    font-size: 22px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .chart-container {
    height: 250px;
  }
  
  .score {
    font-size: 40px;
  }
  
  .detail {
    padding: 0 10px;
  }
  
  .feedback-item {
    gap: 8px;
  }
  
  .feedback-item .label {
    width: 35px;
    font-size: 12px;
  }
  
  .feedback-item .count {
    width: 40px;
    font-size: 12px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* 平板适配 */
@media screen and (min-width: 769px) and (max-width: 1024px) {
  .chart-container {
    height: 280px;
  }
}
</style>
