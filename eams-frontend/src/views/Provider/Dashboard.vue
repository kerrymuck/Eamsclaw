<template>
  <div class="provider-dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>📊 数据面板</h2>
      <p class="subtitle">实时查看您的业务数据和运营情况</p>
    </div>

    <!-- 核心指标卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="8" :lg="4">
        <el-card class="stat-card primary">
          <div class="stat-icon">🔑</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalLicenses }}</div>
            <div class="stat-label">总授权数</div>
            <div class="stat-trend up">
              <el-icon><ArrowUp /></el-icon>
              <span>+{{ stats.newLicensesToday }} 今日</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8" :lg="4">
        <el-card class="stat-card success">
          <div class="stat-icon">✅</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeLicenses }}</div>
            <div class="stat-label">已激活</div>
            <div class="stat-trend">
              <span>激活率 {{ stats.activationRate }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8" :lg="4">
        <el-card class="stat-card warning">
          <div class="stat-icon">🆕</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.newLicensesMonth }}</div>
            <div class="stat-label">本月新增</div>
            <div class="stat-trend up">
              <el-icon><ArrowUp /></el-icon>
              <span>+{{ stats.newLicensesGrowth }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8" :lg="4">
        <el-card class="stat-card danger">
          <div class="stat-icon">⏰</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.expiringLicenses }}</div>
            <div class="stat-label">即将到期</div>
            <div class="stat-trend down">
              <span>7天内到期</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8" :lg="4">
        <el-card class="stat-card info">
          <div class="stat-icon">🏪</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalMerchants }}</div>
            <div class="stat-label">合作商户</div>
            <div class="stat-trend up">
              <el-icon><ArrowUp /></el-icon>
              <span>+{{ stats.newMerchantsMonth }} 本月</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8" :lg="4">
        <el-card class="stat-card purple">
          <div class="stat-icon">💰</div>
          <div class="stat-info">
            <div class="stat-value">¥{{ stats.monthlyRevenue }}</div>
            <div class="stat-label">本月收益</div>
            <div class="stat-trend up">
              <el-icon><ArrowUp /></el-icon>
              <span>+{{ stats.revenueGrowth }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>授权趋势</span>
              <el-radio-group v-model="licenseTrendPeriod" size="small">
                <el-radio-button label="7">近7天</el-radio-button>
                <el-radio-button label="30">近30天</el-radio-button>
                <el-radio-button label="90">近90天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-placeholder">
            <div class="mock-chart">
              <div class="chart-bar" v-for="(item, index) in licenseTrendData" :key="index" :style="{ height: item + '%' }">
                <span class="bar-value">{{ item }}</span>
              </div>
            </div>
            <div class="chart-labels">
              <span v-for="(label, index) in trendLabels" :key="index">{{ label }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>收益趋势</span>
              <el-radio-group v-model="revenueTrendPeriod" size="small">
                <el-radio-button label="7">近7天</el-radio-button>
                <el-radio-button label="30">近30天</el-radio-button>
                <el-radio-button label="90">近90天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-placeholder">
            <div class="mock-chart line-chart">
              <div class="line-points">
                <div class="point" v-for="(item, index) in revenueTrendData" :key="index" :style="{ bottom: item + '%', left: (index * 14) + '%' }">
                  <span class="point-value">¥{{ item }}k</span>
                </div>
              </div>
              <svg class="line-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
                <polyline :points="revenueLinePoints" fill="none" stroke="#1677ff" stroke-width="2"/>
              </svg>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作和动态 -->
    <el-row :gutter="20" class="bottom-row">
      <el-col :xs="24" :lg="12">
        <el-card class="quick-actions">
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="action-grid">
            <div class="action-item" @click="goTo('/provider/merchants')">
              <el-icon :size="32"><Plus /></el-icon>
              <span>添加商户</span>
            </div>
            <div class="action-item" @click="goTo('/provider/license')">
              <el-icon :size="32"><Key /></el-icon>
              <span>生成授权码</span>
            </div>
            <div class="action-item" @click="goTo('/provider/finance')">
              <el-icon :size="32"><Money /></el-icon>
              <span>查看账单</span>
            </div>
            <div class="action-item" @click="goTo('/provider/ai-power')">
              <el-icon :size="32"><Cpu /></el-icon>
              <span>算力充值</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <el-card class="recent-activity">
          <template #header>
            <div class="card-header">
              <span>最近动态</span>
              <el-button link @click="refreshActivity">刷新</el-button>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowUp, Plus, Key, Money, Cpu } from '@element-plus/icons-vue'

const router = useRouter()

// 统计数据
const stats = ref({
  totalLicenses: 12580,
  newLicensesToday: 156,
  activeLicenses: 10234,
  activationRate: 81.3,
  newLicensesMonth: 2340,
  newLicensesGrowth: 23.5,
  expiringLicenses: 89,
  totalMerchants: 328,
  newMerchantsMonth: 45,
  monthlyRevenue: '286,500',
  revenueGrowth: 15.6
})

// 图表数据
const licenseTrendPeriod = ref('7')
const licenseTrendData = ref([45, 52, 48, 65, 72, 68, 85])
const trendLabels = ref(['周一', '周二', '周三', '周四', '周五', '周六', '周日'])

const revenueTrendPeriod = ref('7')
const revenueTrendData = ref([28, 35, 32, 42, 48, 45, 58])

const revenueLinePoints = computed(() => {
  return revenueTrendData.value.map((v, i) => `${i * 14},${100 - v}`).join(' ')
})

// 最近动态
const recentActivities = ref([
  { content: '商户「龙猫数码」激活了专业版授权', time: '2分钟前', type: 'primary' },
  { content: '生成50个企业版授权码', time: '15分钟前', type: 'success' },
  { content: '商户「潮流服饰」续费一年', time: '1小时前', type: 'warning' },
  { content: 'AI算力充值 ¥10,000', time: '2小时前', type: 'info' },
  { content: '新商户「美妆集合店」入驻', time: '3小时前', type: 'primary' }
])

const goTo = (path: string) => {
  router.push(path)
}

const refreshActivity = () => {
  // 刷新动态
}
</script>

<style scoped>
.provider-dashboard {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
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
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
}

.stat-card.primary::before { background: #1677ff; }
.stat-card.success::before { background: #52c41a; }
.stat-card.warning::before { background: #faad14; }
.stat-card.danger::before { background: #ff4d4f; }
.stat-card.info::before { background: #13c2c2; }
.stat-card.purple::before { background: #722ed1; }

.stat-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.stat-trend {
  margin-top: 12px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-trend.up {
  color: #52c41a;
}

.stat-trend.down {
  color: #ff4d4f;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-placeholder {
  height: 250px;
  padding: 20px;
}

.mock-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 200px;
  padding-bottom: 30px;
  position: relative;
}

.chart-bar {
  width: 40px;
  background: linear-gradient(180deg, #1677ff 0%, #0958d9 100%);
  border-radius: 4px 4px 0 0;
  transition: all 0.3s;
  position: relative;
}

.chart-bar:hover {
  opacity: 0.8;
}

.bar-value {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  color: #666;
}

.chart-labels {
  display: flex;
  justify-content: space-around;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}

.chart-labels span {
  font-size: 12px;
  color: #909399;
}

.line-chart {
  position: relative;
}

.line-points {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 30px;
}

.point {
  position: absolute;
  width: 12px;
  height: 12px;
  background: #1677ff;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.point-value {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: #666;
  white-space: nowrap;
}

.line-svg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 30px;
  width: 100%;
  height: 100%;
}

.bottom-row {
  margin-bottom: 20px;
}

.quick-actions {
  margin-bottom: 20px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  gap: 8px;
}

.action-item:hover {
  border-color: #1677ff;
  background: #f0f7ff;
  color: #1677ff;
}

.action-item span {
  font-size: 14px;
}

.recent-activity {
  margin-bottom: 20px;
}
</style>
