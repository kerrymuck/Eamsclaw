<template>
  <div class="page-container">
    <h3>大模型管理</h3>
    <p>管理AI大模型配置</p>
    
    <el-card style="margin-top: 20px;">
      <el-table :data="modelList" stripe>
        <el-table-column prop="name" label="模型名称" />
        <el-table-column prop="modelId" label="模型ID" />
        <el-table-column prop="provider" label="提供商" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-switch v-model="row.status" active-value="active" inactive-value="inactive" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const modelList = ref([
  { name: 'GPT-4 Turbo', modelId: 'gpt-4-turbo-preview', provider: 'OpenAI', status: 'active' },
  { name: 'GPT-3.5 Turbo', modelId: 'gpt-3.5-turbo', provider: 'OpenAI', status: 'active' },
  { name: 'Claude 3 Opus', modelId: 'claude-3-opus', provider: 'Anthropic', status: 'active' }
])
</script>

<style scoped>
.page-container {
  padding: 0;
}
</style>
