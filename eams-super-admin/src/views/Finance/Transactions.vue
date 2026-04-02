<template>
  <div class="page-container">
    <h3>收支明细</h3>
    <p>查看系统收支记录</p>
    
    <el-card style="margin-top: 20px;">
      <el-table :data="transactionList" stripe>
        <el-table-column prop="orderNo" label="订单号" />
        <el-table-column prop="createTime" label="时间" />
        <el-table-column prop="type" label="类型">
          <template #default="{ row }">
            <el-tag :type="row.type === 'income' ? 'success' : 'danger'">
              {{ row.type === 'income' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额">
          <template #default="{ row }">
            <span :style="{ color: row.type === 'income' ? '#67c23a' : '#f56c6c', fontWeight: 'bold' }">
              {{ row.type === 'income' ? '+' : '-' }}¥{{ row.amount.toLocaleString() }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const transactionList = ref([
  { orderNo: 'TRX202603310001', createTime: '2026-03-31 14:30:25', type: 'income', amount: 5990 },
  { orderNo: 'TRX202603310002', createTime: '2026-03-31 13:15:10', type: 'income', amount: 50000 },
  { orderNo: 'TRX202603310003', createTime: '2026-03-31 10:20:18', type: 'expense', amount: 3500 }
])
</script>

<style scoped>
.page-container {
  padding: 0;
}
</style>
