<template>
  <div class="page-container">
    <h3>系统信息</h3>
    <p>查看系统基本信息</p>
    
    <el-card style="margin-top: 20px;">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="系统名称">EAMS 电商智能客服中台</el-descriptions-item>
        <el-descriptions-item label="系统版本">v2.1.0</el-descriptions-item>
        <el-descriptions-item label="服务器IP">192.168.1.100</el-descriptions-item>
        <el-descriptions-item label="数据库">PostgreSQL 15.2</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<style scoped>
.page-container {
  padding: 0;
}
</style>
