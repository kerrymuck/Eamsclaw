<template>
  <div class="settings-container">
    <h3>授权设置</h3>
    <p>配置授权码生成和验证规则</p>
    
    <el-card style="margin-top: 20px;">
      <el-form :model="form" label-width="150px">
        <el-form-item label="授权码前缀">
          <el-input v-model="form.prefix" style="width: 200px;" />
        </el-form-item>
        <el-form-item label="默认有效期">
          <el-input-number v-model="form.defaultExpireMonths" :min="1" :max="120" />
          <span style="margin-left: 10px;">个月</span>
        </el-form-item>
        <el-form-item label="允许解绑">
          <el-switch v-model="form.allowUnbind" />
        </el-form-item>
        <el-form-item label="解绑冷却期">
          <el-input-number v-model="form.unbindCooldownDays" :min="0" :max="30" />
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
  prefix: 'EAMS',
  defaultExpireMonths: 12,
  allowUnbind: true,
  unbindCooldownDays: 7
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
