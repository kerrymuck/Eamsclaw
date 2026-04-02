<template>
  <div class="page-container">
    <h3>防破解</h3>
    <p>配置防破解策略</p>
    
    <el-card style="margin-top: 20px;">
      <el-form label-width="150px">
        <el-form-item label="启用代码混淆">
          <el-switch :model-value="true" />
        </el-form-item>
        <el-form-item label="启用防调试">
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
