<template>
  <div class="settings-container">
    <h3>服务商设置</h3>
    <p>配置服务商相关参数</p>
    
    <el-card style="margin-top: 20px;">
      <el-form :model="form" label-width="150px">
        <el-form-item label="默认有效期">
          <el-input-number v-model="form.defaultExpireMonths" :min="1" :max="36" />
          <span style="margin-left: 10px;">个月</span>
        </el-form-item>
        <el-form-item label="最低充值金额">
          <el-input-number v-model="form.minRecharge" :min="100" :step="100" />
          <span style="margin-left: 10px;">元</span>
        </el-form-item>
        <el-form-item label="自动审核">
          <el-switch v-model="form.autoApprove" />
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
  defaultExpireMonths: 12,
  minRecharge: 1000,
  autoApprove: false
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
