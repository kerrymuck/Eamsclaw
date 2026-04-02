<template>
  <div class="page-container">
    <h3>加密管理</h3>
    <p>管理加密密钥</p>
    
    <el-card style="margin-top: 20px;">
      <el-table :data="keyList" stripe>
        <el-table-column prop="name" label="密钥名称" />
        <el-table-column prop="type" label="类型" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '使用中' : '已轮换' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const keyList = ref([
  { name: '主加密密钥', type: 'AES', status: 'active' },
  { name: 'API签名密钥', type: 'HMAC', status: 'active' }
])
</script>

<style scoped>
.page-container {
  padding: 0;
}
</style>
