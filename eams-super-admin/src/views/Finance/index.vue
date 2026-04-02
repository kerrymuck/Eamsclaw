<template>
  <div class="finance-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #67c23a;">
            <el-icon :size="28"><Wallet /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">¥{{ stats.totalIncome.toLocaleString() }}</div>
            <div class="stat-label">累计收入</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #409eff;">
            <el-icon :size="28"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">¥{{ stats.todayIncome.toLocaleString() }}</div>
            <div class="stat-label">今日收入</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #e6a23c;">
            <el-icon :size="28"><Money /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">¥{{ stats.monthIncome.toLocaleString() }}</div>
            <div class="stat-label">本月收入</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #f56c6c;">
            <el-icon :size="28"><ShoppingCart /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalOrders }}</div>
            <div class="stat-label">总订单数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 收支明细 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>收支明细</span>
          <div class="header-actions">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="margin-right: 10px;"
            />
            <el-select v-model="filterType" placeholder="交易类型" clearable style="width: 120px; margin-right: 10px;">
              <el-option label="全部" value="" />
              <el-option label="收入" value="income" />
              <el-option label="支出" value="expense" />
            </el-select>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon> 查询
            </el-button>
            <el-button @click="handleExport">
              <el-icon><Download /></el-icon> 导出
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="transactionList" stripe>
        <el-table-column prop="orderNo" label="订单号" min-width="180" />
        <el-table-column prop="createTime" label="交易时间" min-width="150" />
        <el-table-column prop="type" label="类型" min-width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'income' ? 'success' : 'danger'">
              {{ row.type === 'income' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="交易类别" min-width="120">
          <template #default="{ row }">
            {{ getCategoryText(row.category) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" min-width="120">
          <template #default="{ row }">
            <span :class="row.type === 'income' ? 'income' : 'expense'">
              {{ row.type === 'income' ? '+' : '-' }}¥{{ row.amount.toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="providerName" label="服务商" min-width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : row.status === 'pending' ? 'warning' : 'danger'">
              {{ row.status === 'success' ? '成功' : row.status === 'pending' ? '处理中' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page.current"
          v-model:page-size="page.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="page.total"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>

    <!-- 收入构成图表 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :sm="24" :md="12">
        <el-card>
          <template #header>
            <span>收入构成</span>
          </template>
          <div ref="incomeChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12">
        <el-card>
          <template #header>
            <span>月度趋势</span>
          </template>
          <div ref="trendChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { Wallet, TrendCharts, Money, ShoppingCart, Search, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const dateRange = ref([])
const filterType = ref('')

const stats = reactive({
  totalIncome: 2856000,
  todayIncome: 56800,
  monthIncome: 456000,
  totalOrders: 12580
})

const page = reactive({
  current: 1,
  size: 10,
  total: 100
})

const transactionList = ref([
  { orderNo: 'TRX202603310001', createTime: '2026-03-31 14:30:25', type: 'income', category: 'license', amount: 5990, providerName: '科技云', description: '购买企业版授权×10', status: 'success' },
  { orderNo: 'TRX202603310002', createTime: '2026-03-31 13:15:10', type: 'income', category: 'recharge', amount: 50000, providerName: '智慧零售', description: '账户充值', status: 'success' },
  { orderNo: 'TRX202603310003', createTime: '2026-03-31 11:45:33', type: 'income', category: 'ai', amount: 1250, providerName: '未来电商', description: 'AI算力充值', status: 'success' },
  { orderNo: 'TRX202603310004', createTime: '2026-03-31 10:20:18', type: 'expense', category: 'server', amount: 3500, providerName: '系统', description: '服务器费用', status: 'success' },
  { orderNo: 'TRX202603310005', createTime: '2026-03-31 09:10:05', type: 'income', category: 'license', amount: 2995, providerName: '星辰科技', description: '购买专业版授权×5', status: 'success' }
])

const getCategoryText = (category: string) => {
  const map: Record<string, string> = {
    license: '授权销售',
    recharge: '账户充值',
    ai: 'AI算力',
    server: '服务器费用',
    bandwidth: '带宽费用',
    other: '其他'
  }
  return map[category] || category
}

const handleSearch = () => {
  ElMessage.success('查询完成')
}

const handleExport = () => {
  ElMessage.success('导出成功')
}

// 图表
const incomeChart = ref<HTMLElement>()
const trendChart = ref<HTMLElement>()
let incomeInstance: echarts.ECharts | null = null
let trendInstance: echarts.ECharts | null = null

onMounted(() => {
  if (incomeChart.value) {
    incomeInstance = echarts.init(incomeChart.value)
    incomeInstance.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: '5%' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: 1850000, name: '授权销售', itemStyle: { color: '#409EFF' } },
          { value: 680000, name: 'AI算力', itemStyle: { color: '#67C23A' } },
          { value: 256000, name: '增值服务', itemStyle: { color: '#E6A23C' } },
          { value: 70000, name: '其他', itemStyle: { color: '#909399' } }
        ]
      }]
    })
  }

  if (trendChart.value) {
    trendInstance = echarts.init(trendChart.value)
    trendInstance.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['10月', '11月', '12月', '1月', '2月', '3月']
      },
      yAxis: { type: 'value' },
      series: [{
        name: '收入',
        type: 'bar',
        data: [320000, 380000, 420000, 390000, 410000, 456000],
        itemStyle: { color: '#409EFF' }
      }]
    })
  }
})

onUnmounted(() => {
  incomeInstance?.dispose()
  trendInstance?.dispose()
})
</script>

<style scoped>
.finance-container {
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

.table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.income {
  color: #67c23a;
  font-weight: bold;
}

.expense {
  color: #f56c6c;
  font-weight: bold;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
}
</style>
