<template>
  <div class="page-container">
    <h3>平台列表</h3>
    <p>管理支持的电商平台</p>
    
    <el-card style="margin-top: 20px;">
      <el-table :data="platformList" stripe>
        <el-table-column prop="name" label="平台名称" />
        <el-table-column prop="code" label="平台代码" />
        <el-table-column prop="type" label="类型" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '已启用' : '未启用' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const platformList = ref([
  { name: '淘宝', code: 'taobao', type: '国内电商', status: 'active' },
  { name: '京东', code: 'jd', type: '国内电商', status: 'active' },
  { name: '拼多多', code: 'pdd', type: '国内电商', status: 'active' },
  { name: 'Amazon', code: 'amazon', type: '跨境电商', status: 'active' }
])
</script>

<style scoped>
.page-container {
  padding: 0;
}
</style>
