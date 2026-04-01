<template>
  <div class="dashboard">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" :body-style="{ padding: '20px' }">
          <div class="stat-icon" :style="{ background: stat.color }">
            <el-icon :size="28"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.title }}</div>
            <div class="stat-trend" v-if="stat.trend">
              <span :class="stat.trend > 0 ? 'up' : 'down'">
                {{ stat.trend > 0 ? '↑' : '↓' }} {{ Math.abs(stat.trend) }}%
              </span>
              <span class="trend-label">较昨日</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <!-- 授权趋势 -->
      <el-col :xs="24" :sm="24" :md="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>授权激活趋势</span>
              <el-radio-group v-model="trendTimeRange" size="small">
                <el-radio-button label="7d">近7天</el-radio-button>
                <el-radio-button label="30d">近30天</el-radio-button>
                <el-radio-button label="90d">近90天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="licenseTrendChart" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <!-- 授权状态分布 -->
      <el-col :xs="24" :sm="24" :md="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>授权状态分布</span>
            </div>
          </template>
          <div ref="licenseStatusChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行图表 -->
    <el-row :gutter="20" class="charts-row">
      <!-- 收入趋势 -->
      <el-col :xs="24" :sm="24" :md="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>收入趋势</span>
              <el-radio-group v-model="revenueTimeRange" size="small">
                <el-radio-button label="7d">近7天</el-radio-button>
                <el-radio-button label="30d">近30天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="revenueChart" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <!-- AI算力使用 -->
      <el-col :xs="24" :sm="24" :md="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>AI算力使用统计</span>
            </div>
          </template>
          <div ref="aiUsageChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时动态 -->
    <el-row :gutter="20" class="activity-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Bell /></el-icon> 实时动态
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
  Key, User, Money, Cpu, Bell, Refresh, TrendCharts, CircleCheck, Warning 
} from '@element-plus/icons-vue'

const trendTimeRange = ref('7d')
const revenueTimeRange = ref('7d')

// 统计数据
const statsCards = computed(() => [
  {
    title: '总授权数',
    value: '12,580',
    icon: 'Key',
    color: '#409EFF',
    trend: 12.5
  },
  {
    title: '激活授权',
    value: '10,234',
    icon: 'CircleCheck',
    color: '#67C23A',
    trend: 8.3
  },
  {
    title: '今日新增',
    value: '156',
    icon: 'TrendCharts',
    color: '#E6A23C',
    trend: 23.1
  },
  {
    title: '即将到期',
    value: '89',
    icon: 'Warning',
    color: '#F56C6C',
    trend: -5.2
  },
  {
    title: '服务商数',
    value: '328',
    icon: 'User',
    color: '#909399',
    trend: 5.8
  },
  {
    title: '累计收入',
    value: '¥2.8M',
    icon: 'Money',
    color: '#67C23A',
    trend: 15.6
  },
  {
    title: 'AI调用量',
    value: '8.5M',
    icon: 'Cpu',
    color: '#409EFF',
    trend: 32.4
  },
  {
    title: '在线商户',
    value: '1,256',
    icon: 'User',
    color: '#E6A23C',
    trend: 18.9
  }
])

// 实时动态
const recentActivities = ref([
  { content: '新授权码生成：服务商「科技云」购买了 50 个企业版授权', time: '2分钟前', type: 'primary' },
  { content: '授权激活：商户「小明电商」激活了专业版授权', time: '5分钟前', type: 'success' },
  { content: '充值到账：服务商「智慧零售」充值 ¥50,000', time: '8分钟前', type: 'warning' },
  { content: 'AI算力告警：OpenAI GPT-4 调用量达到 80% 阈值', time: '15分钟前', type: 'danger' },
  { content: '授权到期提醒：32 个授权将在 7 天内到期', time: '30分钟前', type: 'info' },
  { content: '新服务商入驻：「未来电商」完成注册审核', time: '1小时前', type: 'success' }
])

// 图表引用
const licenseTrendChart = ref<HTMLElement>()
const licenseStatusChart = ref<HTMLElement>()
const revenueChart = ref<HTMLElement>()
const aiUsageChart = ref<HTMLElement>()

let licenseTrendInstance: echarts.ECharts | null = null
let licenseStatusInstance: echarts.ECharts | null = null
let revenueInstance: echarts.ECharts | null = null
let aiUsageInstance: echarts.ECharts | null = null

const initCharts = () => {
  // 授权趋势图
  if (licenseTrendChart.value) {
    licenseTrendInstance = echarts.init(licenseTrendChart.value)
    licenseTrendInstance.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['新增授权', '激活授权', '到期授权'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['03-25', '03-26', '03-27', '03-28', '03-29', '03-30', '03-31']
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '新增授权',
          type: 'line',
          smooth: true,
          data: [120, 132, 101, 134, 90, 230, 210],
          itemStyle: { color: '#409EFF' }
        },
        {
          name: '激活授权',
          type: 'line',
          smooth: true,
          data: [220, 182, 191, 234, 290, 330, 310],
          itemStyle: { color: '#67C23A' }
        },
        {
          name: '到期授权',
          type: 'line',
          smooth: true,
          data: [150, 232, 201, 154, 190, 330, 410],
          itemStyle: { color: '#F56C6C' }
        }
      ]
    })
  }

  // 授权状态分布
  if (licenseStatusChart.value) {
    licenseStatusInstance = echarts.init(licenseStatusChart.value)
    licenseStatusInstance.setOption({
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
        data: [
          { value: 10234, name: '已激活', itemStyle: { color: '#67C23A' } },
          { value: 1567, name: '未激活', itemStyle: { color: '#909399' } },
          { value: 589, name: '已过期', itemStyle: { color: '#F56C6C' } },
          { value: 190, name: '已禁用', itemStyle: { color: '#E6A23C' } }
        ]
      }]
    })
  }

  // 收入趋势
  if (revenueChart.value) {
    revenueInstance = echarts.init(revenueChart.value)
    revenueInstance.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['授权收入', 'AI算力收入', '增值服务'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['03-25', '03-26', '03-27', '03-28', '03-29', '03-30', '03-31']
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '授权收入',
          type: 'bar',
          stack: 'total',
          data: [320, 302, 301, 334, 390, 330, 320],
          itemStyle: { color: '#409EFF' }
        },
        {
          name: 'AI算力收入',
          type: 'bar',
          stack: 'total',
          data: [120, 132, 101, 134, 90, 230, 210],
          itemStyle: { color: '#67C23A' }
        },
        {
          name: '增值服务',
          type: 'bar',
          stack: 'total',
          data: [220, 182, 191, 234, 290, 330, 310],
          itemStyle: { color: '#E6A23C' }
        }
      ]
    })
  }

  // AI算力使用
  if (aiUsageChart.value) {
    aiUsageInstance = echarts.init(aiUsageChart.value)
    aiUsageInstance.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['GPT-4', 'GPT-3.5', 'Claude', '文心一言'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00']
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: 'GPT-4',
          type: 'line',
          smooth: true,
          areaStyle: { opacity: 0.3 },
          data: [120, 132, 301, 534, 890, 1230, 1210],
          itemStyle: { color: '#409EFF' }
        },
        {
          name: 'GPT-3.5',
          type: 'line',
          smooth: true,
          areaStyle: { opacity: 0.3 },
          data: [220, 382, 591, 834, 1190, 1330, 1310],
          itemStyle: { color: '#67C23A' }
        },
        {
          name: 'Claude',
          type: 'line',
          smooth: true,
          areaStyle: { opacity: 0.3 },
          data: [150, 232, 401, 654, 990, 1130, 1110],
          itemStyle: { color: '#E6A23C' }
        },
        {
          name: '文心一言',
          type: 'line',
          smooth: true,
          areaStyle: { opacity: 0.3 },
          data: [80, 132, 201, 334, 590, 730, 710],
          itemStyle: { color: '#F56C6C' }
        }
      ]
    })
  }
}

const handleResize = () => {
  licenseTrendInstance?.resize()
  licenseStatusInstance?.resize()
  revenueInstance?.resize()
  aiUsageInstance?.resize()
}

const refreshData = () => {
  recentActivities.value.unshift({
    content: '数据已刷新 - ' + new Date().toLocaleTimeString(),
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
  licenseTrendInstance?.dispose()
  licenseStatusInstance?.dispose()
  revenueInstance?.dispose()
  aiUsageInstance?.dispose()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
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
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
  min-width: 0;
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

.stat-trend {
  font-size: 12px;
  margin-top: 4px;
}

.stat-trend .up {
  color: #67C23A;
}

.stat-trend .down {
  color: #F56C6C;
}

.trend-label {
  color: #c0c4cc;
  margin-left: 4px;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 320px;
  min-height: 280px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.live-tag {
  margin-left: 10px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.activity-row {
  margin-bottom: 20px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .chart-container {
    height: 250px;
  }
  
  .stat-value {
    font-size: 20px;
  }
}
</style>
