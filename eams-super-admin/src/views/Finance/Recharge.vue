<template>
  <div class="page-container">
    <h3>充值明细</h3>
    <p>查看所有充值记录</p>
    
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
import { ref } from 'vue'

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
