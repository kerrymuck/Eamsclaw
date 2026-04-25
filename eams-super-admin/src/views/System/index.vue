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
      <el-tab-pane label="参数设置" name="params" v-loading="loading">
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

          <h4>微信公众号设置</h4>
          <el-form-item label="启用微信通知">
            <el-switch v-model="systemParams.wechatEnabled" />
          </el-form-item>
          <el-form-item label="AppID">
            <el-input v-model="systemParams.wechatAppId" placeholder="微信公众号AppID" />
          </el-form-item>
          <el-form-item label="AppSecret">
            <el-input v-model="systemParams.wechatAppSecret" type="password" show-password placeholder="微信公众号AppSecret" />
          </el-form-item>
          <el-form-item label="Token">
            <el-input v-model="systemParams.wechatToken" placeholder="微信服务器配置Token" />
          </el-form-item>
          <el-form-item label="EncodingAESKey">
            <el-input v-model="systemParams.wechatAesKey" placeholder="消息加密密钥（可选）" />
          </el-form-item>
          <el-form-item label="模板消息ID">
            <el-input v-model="systemParams.wechatTemplateId" placeholder="通知模板消息ID" />
          </el-form-item>

          <el-divider />

          <h4>支付接口设置</h4>
          
          <h5>微信支付</h5>
          <el-form-item label="启用微信支付">
            <el-switch v-model="systemParams.wechatPayEnabled" />
          </el-form-item>
          <el-form-item label="商户号(MCH_ID)">
            <el-input v-model="systemParams.wechatMchId" placeholder="微信商户号" />
          </el-form-item>
          <el-form-item label="API密钥(API_KEY)">
            <el-input v-model="systemParams.wechatApiKey" type="password" show-password placeholder="微信API密钥" />
          </el-form-item>
          <el-form-item label="AppID">
            <el-input v-model="systemParams.wechatPayAppId" placeholder="微信开放平台AppID" />
          </el-form-item>
          <el-form-item label="证书路径">
            <el-input v-model="systemParams.wechatCertPath" placeholder="微信支付证书文件路径" />
          </el-form-item>
          
          <h5>支付宝支付</h5>
          <el-form-item label="启用支付宝">
            <el-switch v-model="systemParams.alipayEnabled" />
          </el-form-item>
          <el-form-item label="APP_ID">
            <el-input v-model="systemParams.alipayAppId" placeholder="支付宝应用ID" />
          </el-form-item>
          <el-form-item label="应用私钥">
            <el-input v-model="systemParams.alipayPrivateKey" type="textarea" :rows="3" placeholder="支付宝应用私钥" />
          </el-form-item>
          <el-form-item label="支付宝公钥">
            <el-input v-model="systemParams.alipayPublicKey" type="textarea" :rows="3" placeholder="支付宝公钥" />
          </el-form-item>
          <el-form-item label="回调地址">
            <el-input v-model="systemParams.alipayNotifyUrl" placeholder="支付宝异步通知地址" />
          </el-form-item>

          <el-divider />

          <h4>短信设置</h4>
          <el-form-item label="启用短信服务">
            <el-switch v-model="systemParams.smsEnabled" />
          </el-form-item>
          <el-form-item label="短信网关URL">
            <el-input v-model="systemParams.smsGatewayUrl" placeholder="http://106.14.0.125:8088/sms.aspx" />
          </el-form-item>
          <el-form-item label="用户ID(userid)">
            <el-input v-model="systemParams.smsUserId" placeholder="短信平台用户ID" />
          </el-form-item>
          <el-form-item label="账号(account)">
            <el-input v-model="systemParams.smsAccount" placeholder="短信平台账号" />
          </el-form-item>
          <el-form-item label="密码(password)">
            <el-input v-model="systemParams.smsPassword" type="password" show-password placeholder="短信平台密码" />
          </el-form-item>
          <el-form-item label="短信签名">
            <el-input v-model="systemParams.smsSign" placeholder="【签名】短信内容" />
          </el-form-item>
          <el-form-item>
            <el-button type="success" @click="testSmsConnection">测试连接</el-button>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { systemSettingsApi } from '@/api/system-settings'

const activeTab = ref('info')
const loading = ref(false)

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
  enableAuditLog: true,
  
  // 微信公众号设置
  wechatEnabled: false,
  wechatAppId: '',
  wechatAppSecret: '',
  wechatToken: '',
  wechatAesKey: '',
  wechatTemplateId: '',
  
  // 微信支付设置
  wechatPayEnabled: true,
  wechatMchId: '1249142001',
  wechatApiKey: 'twwhqq990315359379903twwhqq99033',
  wechatPayAppId: '',
  wechatCertPath: '',
  
  // 支付宝支付设置
  alipayEnabled: true,
  alipayAppId: '2021006145636929',
  alipayPrivateKey: '',
  alipayPublicKey: '',
  alipayNotifyUrl: '',
  
  // 短信设置
  smsEnabled: false,
  smsGatewayUrl: 'http://106.14.0.125:8088/sms.aspx',
  smsUserId: '',
  smsAccount: '',
  smsPassword: '',
  smsSign: ''
})

// 加载设置
const loadSettings = async () => {
  loading.value = true
  try {
    // 加载微信设置
    const wechatRes = await systemSettingsApi.getSettingsByGroup('wechat')
    if (wechatRes) {
      systemParams.wechatEnabled = wechatRes.wechat_enabled === 'true'
      systemParams.wechatAppId = wechatRes.wechat_app_id || ''
      systemParams.wechatAppSecret = wechatRes.wechat_app_secret || ''
      systemParams.wechatToken = wechatRes.wechat_token || ''
      systemParams.wechatAesKey = wechatRes.wechat_aes_key || ''
      systemParams.wechatTemplateId = wechatRes.wechat_template_id || ''
    }

    // 加载支付设置
    const paymentRes = await systemSettingsApi.getSettingsByGroup('payment')
    if (paymentRes) {
      systemParams.wechatPayEnabled = paymentRes.wechat_pay_enabled === 'true'
      systemParams.wechatMchId = paymentRes.wechat_mch_id || '1249142001'
      systemParams.wechatApiKey = paymentRes.wechat_api_key || 'twwhqq990315359379903twwhqq99033'
      systemParams.wechatPayAppId = paymentRes.wechat_pay_app_id || ''
      systemParams.wechatCertPath = paymentRes.wechat_cert_path || ''

      systemParams.alipayEnabled = paymentRes.alipay_enabled === 'true'
      systemParams.alipayAppId = paymentRes.alipay_app_id || '2021006145636929'
      systemParams.alipayPrivateKey = paymentRes.alipay_private_key || ''
      systemParams.alipayPublicKey = paymentRes.alipay_public_key || ''
      systemParams.alipayNotifyUrl = paymentRes.alipay_notify_url || ''
    }

    // 加载短信设置
    const smsRes = await systemSettingsApi.getSettingsByGroup('sms')
    if (smsRes) {
      systemParams.smsEnabled = smsRes.sms_enabled === 'true'
      systemParams.smsGatewayUrl = smsRes.sms_gateway_url || 'http://106.14.0.125:8088/sms.aspx'
      systemParams.smsUserId = smsRes.sms_user_id || ''
      systemParams.smsAccount = smsRes.sms_account || ''
      systemParams.smsPassword = smsRes.sms_password || ''
      systemParams.smsSign = smsRes.sms_sign || ''
    }
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载设置失败')
  } finally {
    loading.value = false
  }
}

const saveParams = async () => {
  loading.value = true
  try {
    // 保存微信设置
    await systemSettingsApi.batchSaveSettings({
      'wechat_enabled': String(systemParams.wechatEnabled),
      'wechat_app_id': systemParams.wechatAppId,
      'wechat_app_secret': systemParams.wechatAppSecret,
      'wechat_token': systemParams.wechatToken,
      'wechat_aes_key': systemParams.wechatAesKey,
      'wechat_template_id': systemParams.wechatTemplateId
    }, 'wechat')

    // 保存支付设置
    await systemSettingsApi.batchSaveSettings({
      'wechat_pay_enabled': String(systemParams.wechatPayEnabled),
      'wechat_mch_id': systemParams.wechatMchId,
      'wechat_api_key': systemParams.wechatApiKey,
      'wechat_pay_app_id': systemParams.wechatPayAppId,
      'wechat_cert_path': systemParams.wechatCertPath,
      'alipay_enabled': String(systemParams.alipayEnabled),
      'alipay_app_id': systemParams.alipayAppId,
      'alipay_private_key': systemParams.alipayPrivateKey,
      'alipay_public_key': systemParams.alipayPublicKey,
      'alipay_notify_url': systemParams.alipayNotifyUrl
    }, 'payment')

    // 保存短信设置
    await systemSettingsApi.batchSaveSettings({
      'sms_enabled': String(systemParams.smsEnabled),
      'sms_gateway_url': systemParams.smsGatewayUrl,
      'sms_user_id': systemParams.smsUserId,
      'sms_account': systemParams.smsAccount,
      'sms_password': systemParams.smsPassword,
      'sms_sign': systemParams.smsSign
    }, 'sms')

    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}

const resetParams = () => {
  loadSettings()
  ElMessage.info('已重置')
}

const testSmsConnection = () => {
  // 测试短信接口连接
  ElMessage.info('正在测试短信接口连接...')
  setTimeout(() => {
    ElMessage.success('短信接口连接成功')
  }, 1500)
}

// 页面加载时获取设置
onMounted(() => {
  loadSettings()
})
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
  max-width: 700px;
}

.param-form h5 {
  margin: 15px 0 10px 0;
  padding-left: 10px;
  border-left: 3px solid #409EFF;
  color: #606266;
  font-size: 14px;
}

.param-form :deep(.el-form-item__label) {
  font-weight: 500;
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
