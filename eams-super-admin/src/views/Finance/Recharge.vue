<template>
  <div class="page-container">
    <h3>充值明细</h3>
    <p>查看所有充值记录</p>
    
    <!-- 筛选栏 -->
    <el-card style="margin-top: 20px;">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="订单号">
          <el-input v-model="searchForm.orderNo" placeholder="请输入订单号" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="服务商">
          <el-select v-model="searchForm.providerId" placeholder="全部服务商" clearable style="width: 150px">
            <el-option label="科技云" value="1" />
            <el-option label="智慧零售" value="2" />
            <el-option label="未来电商" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="支付方式">
          <el-select v-model="searchForm.paymentMethod" placeholder="全部方式" clearable style="width: 130px">
            <el-option label="微信支付" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="银行转账" value="bank" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="成功" value="success" />
            <el-option label="处理中" value="pending" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间周期">
          <el-select v-model="searchForm.timeRange" placeholder="全部时间" clearable @change="handleTimeRangeChange" style="width: 130px">
            <el-option label="当天" value="today" />
            <el-option label="本月" value="thisMonth" />
            <el-option label="近30天" value="last30Days" />
            <el-option label="近90天" value="last90Days" />
            <el-option label="近半年" value="last6Months" />
            <el-option label="近一年" value="last1Year" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="searchForm.timeRange === 'custom'" label="自定义时间">
          <el-date-picker
            v-model="searchForm.customDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="金额范围">
          <el-input-number v-model="searchForm.minAmount" :min="0" :precision="2" placeholder="最小金额" style="width: 130px" />
          <span style="margin: 0 8px;">-</span>
          <el-input-number v-model="searchForm.maxAmount" :min="0" :precision="2" placeholder="最大金额" style="width: 130px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon> 导出
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <el-table :data="rechargeList" stripe>
        <el-table-column prop="orderNo" label="订单号" />
        <el-table-column prop="createTime" label="充值时间" />
        <el-table-column prop="providerName" label="服务商" />
        <el-table-column prop="amount" label="充值金额">
          <template #default="{ row }">
            <span style="color: #67c23a; font-weight: bold;">+¥{{ row.amount.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="paymentMethod" label="支付方式" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'warning'">
              {{ row.status === 'success' ? '成功' : '处理中' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Download } from '@element-plus/icons-vue'

const searchForm = reactive({
  orderNo: '',
  providerId: '',
  paymentMethod: '',
  status: '',
  timeRange: '',
  customDateRange: [] as string[],
  minAmount: undefined as number | undefined,
  maxAmount: undefined as number | undefined
})

const handleTimeRangeChange = (val: string) => {
  if (val !== 'custom') {
    searchForm.customDateRange = []
  }
}

const handleSearch = () => {
  ElMessage.success('搜索完成')
}

const resetSearch = () => {
  searchForm.orderNo = ''
  searchForm.providerId = ''
  searchForm.paymentMethod = ''
  searchForm.status = ''
  searchForm.timeRange = ''
  searchForm.customDateRange = []
  searchForm.minAmount = undefined
  searchForm.maxAmount = undefined
}

const handleExport = () => {
  ElMessage.success('导出成功')
}

const rechargeList = ref([
  { orderNo: 'RC202603310001', createTime: '2026-03-31 14:30:25', providerName: '科技云', amount: 50000, paymentMethod: '银行转账', status: 'success' },
  { orderNo: 'RC202603310002', createTime: '2026-03-31 11:15:10', providerName: '智慧零售', amount: 20000, paymentMethod: '支付宝', status: 'success' },
  { orderNo: 'RC202603310003', createTime: '2026-03-31 09:45:33', providerName: '未来电商', amount: 10000, paymentMethod: '微信支付', status: 'pending' }
])
</script>

<style scoped>
.page-container {
  padding: 0;
}
</style>
