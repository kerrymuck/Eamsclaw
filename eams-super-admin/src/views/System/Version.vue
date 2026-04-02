<template>
  <div class="page-container">
    <h3>版本说明</h3>
    <p>查看系统版本更新历史</p>
    
    <el-card style="margin-top: 20px;">
      <el-timeline>
        <el-timeline-item timestamp="2026-03-25" type="primary">
          <h4>v2.1.0</h4>
          <ul>
            <li>新增超级管理员后台</li>
            <li>新增AI算力中控管理</li>
            <li>新增授权码管理系统</li>
          </ul>
        </el-timeline-item>
        <el-timeline-item timestamp="2026-03-15">
          <h4>v2.0.0</h4>
          <ul>
            <li>新增多店铺管理</li>
            <li>新增统一收件箱</li>
            <li>新增AI智能回复引擎</li>
          </ul>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<style scoped>
.page-container {
  padding: 0;
}
</style>
