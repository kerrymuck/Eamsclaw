<template>
  <div class="settings-container">
    <h3>等级设置</h3>
    <p>配置服务商等级规则</p>
    
    <el-card style="margin-top: 20px;">
      <el-form :model="form" label-width="150px">
        <el-form-item label="自动升级">
          <el-switch v-model="form.autoUpgrade" />
        </el-form-item>
        <el-form-item label="降级保护期">
          <el-input-number v-model="form.downgradeProtectionDays" :min="0" :max="90" />
          <span style="margin-left: 10px;">天</span>
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
  autoUpgrade: true,
  downgradeProtectionDays: 30
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
