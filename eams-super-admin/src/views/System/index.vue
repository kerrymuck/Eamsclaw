<template>
  <div class="system-container">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 系统信息 -->
      <el-tab-pane label="系统信息" name="info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="系统名称">EAMS 电商智能客服中台</el-descriptions-item>
          <el-descriptions-item label="系统版本">v2.1.0</el-descriptions-item>
          <el-descriptions-item label="运行环境">Production</el-descriptions-item>
          <el-descriptions-item label="部署时间">2026-03-15 08:00:00</el-descriptions-item>
          <el-descriptions-item label="服务器IP">192.168.1.100</el-descriptions-item>
          <el-descriptions-item label="数据库">PostgreSQL 15.2</el-descriptions-item>
          <el-descriptions-item label="Redis版本">7.0.12</el-descriptions-item>
          <el-descriptions-item label="Python版本">3.11.4</el-descriptions-item>
          <el-descriptions-item label="Node版本">18.17.0</el-descriptions-item>
          <el-descriptions-item label="系统状态">
            <el-tag type="success">运行正常</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <h4>系统统计</h4>
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number">99.99%</div>
              <div class="stat-label">系统可用性</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number">156天</div>
              <div class="stat-label">连续运行</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number">12.5GB</div>
              <div class="stat-label">数据库存储</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number">2.3GB</div>
              <div class="stat-label">缓存使用</div>
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- 参数设置 -->
      <el-tab-pane label="参数设置" name="params">
        <el-form :model="systemParams" label-width="180px" class="param-form">
          <h4>基础设置</h4>
          <el-form-item label="系统名称">
            <el-input v-model="systemParams.systemName" />
          </el-form-item>
          <el-form-item label="系统Logo">
            <el-upload
              class="avatar-uploader"
              action="#"
              :show-file-list="false"
              :auto-upload="false"
            >
              <img v-if="systemParams.logo" :src="systemParams.logo" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            </el-upload>
          </el-form-item>
          <el-form-item label="版权信息">
            <el-input v-model="systemParams.copyright" />
          </el-form-item>
          <el-form-item label="ICP备案号">
            <el-input v-model="systemParams.icp" />
          </el-form-item>

          <el-divider />

          <h4>安全设置</h4>
          <el-form-item label="登录失败锁定次数">
            <el-input-number v-model="systemParams.loginFailLimit" :min="3" :max="10" />
          </el-form-item>
          <el-form-item label="登录锁定时间(分钟)">
            <el-input-number v-model="systemParams.lockTime" :min="5" :max="60" />
          </el-form-item>
          <el-form-item label="Token有效期(小时)">
            <el-input-number v-model="systemParams.tokenExpire" :min="1" :max="168" />
          </el-form-item>
          <el-form-item label="密码最小长度">
            <el-input-number v-model="systemParams.passwordMinLength" :min="6" :max="20" />
          </el-form-item>

          <el-divider />

          <h4>功能开关</h4>
          <el-form-item label="开放注册">
            <el-switch v-model="systemParams.enableRegister" />
          </el-form-item>
          <el-form-item label="邮箱验证">
            <el-switch v-model="systemParams.enableEmailVerify" />
          </el-form-item>
          <el-form-item label="短信通知">
            <el-switch v-model="systemParams.enableSms" />
          </el-form-item>
          <el-form-item label="操作日志">
            <el-switch v-model="systemParams.enableAuditLog" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveParams">保存设置</el-button>
            <el-button @click="resetParams">重置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- 版本说明 -->
      <el-tab-pane label="版本说明" name="version">
        <el-timeline>
          <el-timeline-item timestamp="2026-03-25" placement="top" type="primary">
            <el-card>
              <h4>v2.1.0 - 当前版本</h4>
              <ul>
                <li>新增超级管理员后台</li>
                <li>新增AI算力中控管理</li>
                <li>新增授权码管理系统</li>
                <li>优化平台适配器架构</li>
                <li>修复已知Bug</li>
              </ul>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="2026-03-15" placement="top">
            <el-card>
              <h4>v2.0.0</h4>
              <ul>
                <li>新增多店铺管理（支持32个平台）</li>
                <li>新增统一收件箱</li>
                <li>新增AI智能回复引擎</li>
                <li>新增WebSocket实时通信</li>
                <li>新增跨平台用户数据关联</li>
              </ul>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="2026-02-28" placement="top">
            <el-card>
              <h4>v1.5.0</h4>
              <ul>
                <li>新增知识库管理</li>
                <li>新增数据统计报表</li>
                <li>新增快捷回复模板</li>
                <li>优化对话体验</li>
              </ul>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="2026-02-10" placement="top">
            <el-card>
              <h4>v1.0.0</h4>
              <ul>
                <li>EAMS 系统正式上线</li>
                <li>基础对话功能</li>
                <li>淘宝/京东平台对接</li>
              </ul>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const activeTab = ref('info')

const systemParams = reactive({
  systemName: 'EAMS 电商智能客服中台',
  logo: '',
  copyright: '© 2026 龙猫技术团队',
  icp: '京ICP备XXXXXXXX号',
  loginFailLimit: 5,
  lockTime: 30,
  tokenExpire: 24,
  passwordMinLength: 8,
  enableRegister: true,
  enableEmailVerify: true,
  enableSms: true,
  enableAuditLog: true
})

const saveParams = () => {
  ElMessage.success('保存成功')
}

const resetParams = () => {
  ElMessage.info('已重置')
}
</script>

<style scoped>
.system-container {
  padding: 0;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.param-form {
  max-width: 600px;
}

.avatar-uploader {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
  width: 120px;
  height: 120px;
}

.avatar-uploader:hover {
  border-color: var(--el-color-primary);
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  text-align: center;
  line-height: 120px;
}

.avatar {
  width: 120px;
  height: 120px;
  display: block;
}

h4 {
  margin: 20px 0 15px;
  color: #303133;
}

ul {
  padding-left: 20px;
}

li {
  margin: 8px 0;
  color: #606266;
}
</style>
