<template>
  <div class="settings-container">
    <h3>等级设置</h3>
    <p>配置服务商等级规则</p>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>等级规则设置</span>
      </template>
      
      <el-form :model="form" label-width="150px">
        <el-form-item label="自动升级">
          <el-switch v-model="form.autoUpgrade" />
          <span class="form-tip">开启后，服务商累计充值金额达到等级要求时自动升级</span>
        </el-form-item>
        <el-form-item label="降级保护期">
          <el-input-number v-model="form.downgradeProtectionDays" :min="0" :max="90" />
          <span style="margin-left: 10px;">天</span>
        </el-form-item>
        <el-form-item label="等级计算周期">
          <el-radio-group v-model="form.calculationPeriod">
            <el-radio label="monthly">按月计算</el-radio>
            <el-radio label="quarterly">按季度计算</el-radio>
            <el-radio label="yearly">按年计算</el-radio>
            <el-radio label="lifetime">累计计算</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSave">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 升级规则说明 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>升级规则说明</span>
      </template>
      <div class="rules-description">
        <p><strong>自动升级逻辑：</strong></p>
        <ul>
          <li>当服务商累计充值金额达到某等级的升级金额时，自动升级到该等级</li>
          <li>升级后享受该等级的折扣优惠</li>
          <li>等级降级需要经过保护期后才生效</li>
        </ul>
        <p><strong>等级权益：</strong></p>
        <ul>
          <li>不同等级享受不同的授权采购折扣</li>
          <li>高等级服务商可获得更多技术支持</li>
          <li>等级越高，可持有的最大授权数越多</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const form = reactive({
  autoUpgrade: true,
  downgradeProtectionDays: 30,
  calculationPeriod: 'lifetime'
})

const handleSave = () => {
  ElMessage.success('保存成功')
}
</script>

<style scoped>
.settings-container {
  padding: 0;
}

.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 13px;
}

.rules-description {
  line-height: 2;
}

.rules-description ul {
  margin: 10px 0;
  padding-left: 20px;
}

.rules-description li {
  margin: 5px 0;
  color: #606266;
}
</style>
