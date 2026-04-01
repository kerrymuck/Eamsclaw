<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :xs="12" :sm="12" :md="6" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" :body-style="{ padding: isMobile ? '16px' : '20px' }">
          <div class="stat-icon" :style="{ background: stat.color }">
            <el-icon :size="isMobile ? 20 : 24"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.title }}</div>
            <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
              {{ stat.trend > 0 ? '↑' : '↓' }} {{ Math.abs(stat.trend) }}%
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :sm="24" :md="16" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>会话趋势</span>
              <el-radio-group v-model="timeRange" size="small">
                <el-radio-button label="today">今日</el-radio-button>
                <el-radio-button label="week">本周</el-radio-button>
                <el-radio-button label="month">本月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="8" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>会话来源</span>
            </div>
          </template>
          <div ref="sourceChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时会话和快捷操作 -->
    <el-row :gutter="16" class="bottom-row">
      <el-col :xs="24" :sm="24" :md="16" :lg="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Bell /></el-icon>
                实时会话
                <el-tag type="success" effect="dark" size="small" class="live-tag">LIVE</el-tag>
              </span>
              <el-button type="primary" size="small" @click="goToChat">
                进入消息中心
              </el-button>
            </div>
          </template>
          <el-table :data="conversations" style="width: 100%" v-if="!isMobile">
            <el-table-column prop="buyer" label="买家" min-width="120">
              <template #default="{ row }">
                <div class="buyer-info">
                  <el-avatar :size="32" :src="row.avatar" />
                  <span>{{ row.buyer }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="platform" label="平台" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="row.platformType">{{ row.platform }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="最新消息" min-width="200" show-overflow-tooltip />
            <el-table-column prop="time" label="时间" width="100" />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default>
                <el-button type="primary" link size="small">回复</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 移动端列表 -->
          <div v-else class="mobile-list">
            <div v-for="conv in conversations" :key="conv.id" class="mobile-list-item">
              <div class="item-header">
                <div class="buyer-info">
                  <el-avatar :size="36" :src="conv.avatar" />
                  <div>
                    <div class="buyer-name">{{ conv.buyer }}</div>
                    <el-tag size="small" :type="conv.platformType">{{ conv.platform }}</el-tag>
                  </div>
                </div>
                <span class="item-time">{{ conv.time }}</span>
              </div>
              <div class="item-message">{{ conv.message }}</div>
              <div class="item-actions">
                <el-button type="primary" link size="small">立即回复</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="8" :lg="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <div 
              v-for="action in quickActions" 
              :key="action.name"
              class="action-item"
              @click="handleAction(action)"
            >
              <div class="action-icon" :style="{ background: action.color }">
                <el-icon :size="20"><component :is="action.icon" /></el-icon>
              </div>
              <span class="action-name">{{ action.name }}</span>
            </div>
          </div>
        </el-card>
        
        <el-card style="margin-top: 16px;">
          <template #header>
            <div class="card-header">
              <span>系统公告</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(notice, index) in notices"
              :key="index"
              :type="notice.type"
              :timestamp="notice.time"
            >
              {{ notice.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { 
  ChatDotRound, User, Check, Clock, Bell,
  Plus, Document, Setting, Message
} from '@element-plus/icons-vue'

const router = useRouter()
const timeRange = ref('today')
const trendChart = ref<HTMLElement>()
const sourceChart = ref<HTMLElement>()

const isMobile = ref(window.innerWidth < 768)

let trendInstance: echarts.ECharts | null = null
let sourceInstance: echarts.ECharts | null = null

const statsCards = ref([
  { title: '今日会话', value: '128', icon: 'ChatDotRound', color: '#1677ff', trend: 12 },
  { title: '在线客服', value: '5', icon: 'User', color: '#52c41a', trend: 0 },
  { title: '已解决', value: '96', icon: 'Check', color: '#fa8c16', trend: 8 },
  { title: '平均响应', value: '45s', icon: 'Clock', color: '#f5222d', trend: -5 }
])

const conversations = ref([
  { id: 1, buyer: '张先生', avatar: '', platform: '淘宝', platformType: 'danger', message: '这个商品有优惠吗？', time: '2分钟前' },
  { id: 2, buyer: '李女士', avatar: '', platform: '京东', platformType: 'danger', message: '什么时候发货？', time: '5分钟前' },
  { id: 3, buyer: '王先生', avatar: '', platform: '拼多多', platformType: 'success', message: '申请退款怎么操作？', time: '8分钟前' },
  { id: 4, buyer: '赵女士', avatar: '', platform: '淘宝', platformType: 'danger', message: '可以开发票吗？', time: '12分钟前' }
])

const quickActions = [
  { name: '添加知识库', icon: 'Plus', color: '#1677ff', path: '/knowledge' },
  { name: '快捷回复', icon: 'Message', color: '#52c41a', path: '/settings' },
  { name: '客服设置', icon: 'Setting', color: '#fa8c16', path: '/staff' },
  { name: '查看报表', icon: 'Document', color: '#722ed1', path: '/dashboard' }
]

const notices = ref([
  { content: '系统将于今晚进行维护升级', time: '10分钟前', type: 'warning' },
  { content: '新增淘宝平台接入功能', time: '2小时前', type: 'success' },
  { content: 'AI模型已更新至v2.0', time: '昨天', type: 'primary' }
])

const initCharts = () => {
  if (trendChart.value) {
    trendInstance = echarts.init(trendChart.value)
    trendInstance.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00']
      },
      yAxis: { type: 'value' },
      series: [{
        name: '会话数',
        type: 'line',
        smooth: true,
        data: [12, 8, 25, 45, 38, 52, 28],
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(22, 119, 255, 0.3)' },
            { offset: 1, color: 'rgba(22, 119, 255, 0.05)' }
          ])
        },
        itemStyle: { color: '#1677ff' }
      }]
    })
  }

  if (sourceChart.value) {
    sourceInstance = echarts.init(sourceChart.value)
    sourceInstance.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: '5%' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        data: [
          { value: 45, name: '淘宝' },
          { value: 30, name: '京东' },
          { value: 25, name: '拼多多' }
        ]
      }]
    })
  }
}

const handleResize = () => {
  isMobile.value = window.innerWidth < 768
  trendInstance?.resize()
  sourceInstance?.resize()
}

const goToChat = () => {
  router.push('/chat')
}

const handleAction = (action: any) => {
  router.push(action.path)
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendInstance?.dispose()
  sourceInstance?.dispose()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-row {
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 16px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

.stat-label {
  font-size: 13px;
  color: #666;
  margin-top: 4px;
}

.stat-trend {
  font-size: 12px;
  margin-top: 4px;
}

.stat-trend.up {
  color: #52c41a;
}

.stat-trend.down {
  color: #f5222d;
}

.chart-row {
  margin-bottom: 16px;
}

.chart-card {
  margin-bottom: 16px;
}

.chart-container {
  height: 300px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.live-tag {
  margin-left: 8px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.buyer-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 移动端列表 */
.mobile-list {
  padding: 8px 0;
}

.mobile-list-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.mobile-list-item:last-child {
  border-bottom: none;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.item-header .buyer-info {
  flex-direction: row;
}

.buyer-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.item-time {
  font-size: 12px;
  color: #999;
}

.item-message {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
  padding-left: 44px;
}

.item-actions {
  padding-left: 44px;
}

/* 快捷操作 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  background: #f5f5f5;
  cursor: pointer;
  transition: all 0.3s;
}

.action-item:hover {
  background: #e8e8e8;
  transform: translateY(-2px);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-bottom: 12px;
}

.action-name {
  font-size: 13px;
  color: #333;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .stat-icon {
    width: 40px;
    height: 40px;
    margin-right: 12px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .chart-container {
    height: 240px;
  }
  
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .action-item {
    padding: 16px;
  }
}
</style>
