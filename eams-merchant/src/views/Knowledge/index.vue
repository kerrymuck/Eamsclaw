<template>
  <div class="knowledge-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>知识库管理</span>
          <el-button type="primary" :icon="Plus">添加知识</el-button>
        </div>
      </template>
      
      <el-input
        v-model="searchQuery"
        placeholder="搜索知识库..."
        :prefix-icon="Search"
        clearable
        style="margin-bottom: 16px;"
      />
      
      <el-empty description="知识库功能开发中" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'

const searchQuery = ref('')
</script>

<style scoped>
.knowledge-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
