<template>
  <div class="settings-container">
    <h3>平台设置</h3>
    <p>配置电商平台对接参数</p>
    
    <el-card style="margin-top: 20px;">
      <el-form :model="form" label-width="150px">
        <el-form-item label="自动同步">
          <el-switch v-model="form.autoSync" />
        </el-form-item>
        <el-form-item label="同步间隔">
          <el-input-number v-model="form.syncInterval" :min="1" :max="60" />
          <span style="margin-left: 10px;">分钟</span>
        </el-form-item>
        <el-form-item label="Webhook超时">
          <el-input-number v-model="form.webhookTimeout" :min="1" :max="60" />
          <span style="margin-left: 10px;">秒</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSave">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const form = reactive({
  autoSync: true,
  syncInterval: 5,
  webhookTimeout: 10
})

const handleSave = () => {
  ElMessage.success('保存成功')
}
</script>

<style scoped>
.settings-container {
  padding: 0;
}
</style>
