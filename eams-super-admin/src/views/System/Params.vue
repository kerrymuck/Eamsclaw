<template>
  <div class="page-container">
    <h3>参数设置</h3>
    <p>配置系统运行参数</p>
    
    <el-card style="margin-top: 20px;">
      <el-form label-width="150px">
        <el-form-item label="系统名称">
          <el-input model-value="EAMS 电商智能客服中台" />
        </el-form-item>
        <el-form-item label="登录失败锁定">
          <el-input-number :model-value="5" :min="3" :max="10" />
          <span style="margin-left: 10px;">次</span>
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
