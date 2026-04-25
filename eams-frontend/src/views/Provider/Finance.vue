<template>
  <div class="finance-management">
    <div class="page-header">
      <h2>💰 财务管理</h2>
      <p class="subtitle">查看账单明细、充值记录和收益统计</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="stat-card">
          <div class="stat-icon blue">💰</div>
          <div class="stat-info">
            <div class="stat-value">¥{{ stats.totalRevenue }}</div>
            <div class="stat-label">累计收益</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="stat-card">
          <div class="stat-icon green">📈</div>
          <div class="stat-info">
            <div class="stat-value">¥{{ stats.monthRevenue }}</div>
            <div class="stat-label">本月收益</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="stat-card">
          <div class="stat-icon orange">💳</div>
          <div class="stat-info">
            <div class="stat-value">¥{{ stats.balance }}</div>
            <div class="stat-label">账户余额</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 账单筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="订单号">
          <el-input v-model="filterForm.orderNo" placeholder="请输入订单号" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filterForm.type" placeholder="全部类型" clearable style="width: 120px">
            <el-option label="收入" value="income" />
            <el-option label="支出" value="expense" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="已完成" value="completed" />
            <el-option label="处理中" value="pending" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间周期">
          <el-select v-model="filterForm.timeRange" placeholder="全部时间" clearable @change="handleTimeRangeChange" style="width: 130px">
            <el-option label="当天" value="today" />
            <el-option label="本月" value="thisMonth" />
            <el-option label="近30天" value="last30Days" />
            <el-option label="近90天" value="last90Days" />
            <el-option label="近半年" value="last6Months" />
            <el-option label="近一年" value="last1Year" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="filterForm.timeRange === 'custom'" label="自定义时间">
          <el-date-picker
            v-model="filterForm.customDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="金额范围">
          <el-input-number v-model="filterForm.minAmount" :min="0" :precision="2" placeholder="最小金额" style="width: 130px" />
          <span style="margin: 0 8px;">-</span>
          <el-input-number v-model="filterForm.maxAmount" :min="0" :precision="2" placeholder="最大金额" style="width: 130px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetFilter">重置</el-button>
          <el-button type="success" @click="showRechargeDialog = true">
            <el-icon><Money /></el-icon>
            立即充值
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 账单明细 -->
    <el-card class="bill-card">
      <template #header>
        <div class="card-header">
          <span>账单明细</span>
          <el-radio-group v-model="billType" size="small">
            <el-radio-button label="all">全部</el-radio-button>
            <el-radio-button label="income">收入</el-radio-button>
            <el-radio-button label="expense">支出</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
      <el-table :data="billList" stripe>
        <el-table-column prop="date" label="时间" width="180" />
        <el-table-column prop="orderNo" label="订单号" width="200" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.type === 'income' ? 'success' : 'danger'">
              {{ row.type === 'income' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="amount" label="金额" width="150">
          <template #default="{ row }">
            <span :class="row.type === 'income' ? 'amount-income' : 'amount-expense'">
              {{ row.type === 'income' ? '+' : '-' }}¥{{ row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
              {{ row.status === 'completed' ? '已完成' : '处理中' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 充值弹窗 -->
    <el-dialog v-model="showRechargeDialog" title="账户充值" width="500px">
      <el-form :model="rechargeForm" label-width="100px">
        <el-form-item label="充值金额">
          <el-radio-group v-model="rechargeForm.amount">
            <el-radio-button label="1000">¥1,000</el-radio-button>
            <el-radio-button label="5000">¥5,000</el-radio-button>
            <el-radio-button label="10000">¥10,000</el-radio-button>
            <el-radio-button label="50000">¥50,000</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="支付方式">
          <el-radio-group v-model="rechargeForm.payment">
            <el-radio label="alipay">支付宝</el-radio>
            <el-radio label="wechat">微信支付</el-radio>
            <el-radio label="bank">银行转账</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRechargeDialog = false">取消</el-button>
        <el-button type="primary" @click="handleRecharge">确认充值</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Money, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const stats = ref({
  totalRevenue: '1,286,500',
  monthRevenue: '86,500',
  balance: '125,800'
})

const billType = ref('all')
const showRechargeDialog = ref(false)

const filterForm = reactive({
  orderNo: '',
  type: '',
  status: '',
  timeRange: '',
  customDateRange: [] as string[],
  minAmount: undefined as number | undefined,
  maxAmount: undefined as number | undefined
})

const handleTimeRangeChange = (val: string) => {
  if (val !== 'custom') {
    filterForm.customDateRange = []
  }
}

const handleSearch = () => {
  ElMessage.success('搜索完成')
}

const resetFilter = () => {
  filterForm.orderNo = ''
  filterForm.type = ''
  filterForm.status = ''
  filterForm.timeRange = ''
  filterForm.customDateRange = []
  filterForm.minAmount = undefined
  filterForm.maxAmount = undefined
}

const rechargeForm = reactive({
  amount: '1000',
  payment: 'alipay'
})

const billList = ref([
  { date: '2026-04-10 14:30:00', orderNo: 'RE202604100001', type: 'income', description: '商户「龙猫数码」续费', amount: '4,999', status: 'completed' },
  { date: '2026-04-10 10:15:00', orderNo: 'AI202604100002', type: 'expense', description: 'AI算力充值', amount: '10,000', status: 'completed' },
  { date: '2026-04-09 16:45:00', orderNo: 'RE202604090003', type: 'income', description: '商户「潮流服饰」购买授权', amount: '1,999', status: 'completed' }
])

const handleRecharge = () => {
  ElMessage.success('充值申请已提交，请完成支付')
  showRechargeDialog.value = false
}
</script>

<style scoped>
.finance-management {
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

.stat-icon.blue { background: #e6f7ff; }
.stat-icon.green { background: #f6ffed; }
.stat-icon.orange { background: #fff7e6; }

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

.filter-card {
  margin-bottom: 20px;
}

.bill-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.amount-income {
  color: #52c41a;
  font-weight: 500;
}

.amount-expense {
  color: #ff4d4f;
  font-weight: 500;
}
</style>
