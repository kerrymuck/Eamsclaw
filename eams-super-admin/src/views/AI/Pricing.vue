<template>
  <div class="page-container">
    <h3>价格设置</h3>
    <p>配置AI算力对外售价</p>
    
    <el-card style="margin-top: 20px;">
      <el-table :data="pricingList" stripe>
        <el-table-column prop="modelName" label="模型" />
        <el-table-column prop="costPrice" label="成本价">
          <template #default="{ row }">
            ¥{{ row.costPrice }}/1K tokens
          </template>
        </el-table-column>
        <el-table-column prop="salePrice" label="销售价">
          <template #default="{ row }">
            <el-input-number v-model="row.salePrice" :min="0" :precision="4" :step="0.001" />
          </template>
        </el-table-column>
      </el-table>
      
      <div style="margin-top: 20px;">
        <el-button type="primary" @click="handleSave">保存设置</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const pricingList = ref([
  { modelName: 'GPT-4 Turbo', costPrice: 0.04, salePrice: 0.08 },
  { modelName: 'GPT-3.5 Turbo', costPrice: 0.002, salePrice: 0.005 },
  { modelName: 'Claude 3 Opus', costPrice: 0.09, salePrice: 0.18 }
])

const handleSave = () => {
  ElMessage.success('保存成功')
}
</script>

<style scoped>
.page-container {
  padding: 0;
}
</style>
