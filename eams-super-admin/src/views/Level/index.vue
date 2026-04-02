<template>
  <div class="page-container">
    <h3>服务商等级</h3>
    <p>管理服务商等级体系</p>
    
    <el-card style="margin-top: 20px;">
      <el-table :data="levelList" stripe>
        <el-table-column prop="name" label="等级名称" />
        <el-table-column prop="minLicenses" label="最小授权数" />
        <el-table-column prop="discount" label="折扣率">
          <template #default="{ row }">
            {{ row.discount }}%
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const levelList = ref([
  { name: '金牌服务商', minLicenses: 100, discount: 60 },
  { name: '银牌服务商', minLicenses: 50, discount: 75 },
  { name: '铜牌服务商', minLicenses: 20, discount: 85 },
  { name: '普通服务商', minLicenses: 0, discount: 100 }
])
</script>

<style scoped>
.page-container {
  padding: 0;
}
</style>
