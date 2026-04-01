<template>
  <div class="settings-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>
      
      <el-form label-width="120px">
        <el-form-item label="店铺名称">
          <el-input v-model="settings.shopName" />
        </el-form-item>
        <el-form-item label="客服昵称">
          <el-input v-model="settings.nickname" />
        </el-form-item>
        <el-form-item label="自动回复">
          <el-switch v-model="settings.autoReply" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const settings = ref({
  shopName: '官方旗舰店',
  nickname: '客服小美',
  autoReply: true
})

const saveSettings = () => {
  ElMessage.success('设置已保存')
}
</script>

<style scoped>
.settings-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
