<template>
  <div class="page-container">
    <h3>Ecode设置</h3>
    <p>配置商户授权码规则</p>
    
    <el-card style="margin-top: 20px;">
      <el-form label-width="150px">
        <el-form-item label="Ecode长度">
          <el-input-number :model-value="32" :min="16" :max="64" />
        </el-form-item>
        <el-form-item label="包含大写字母">
          <el-switch :model-value="true" />
        </el-form-item>
        <el-form-item label="包含数字">
          <el-switch :model-value="true" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.page-container {
  padding: 0;
}
</style>
