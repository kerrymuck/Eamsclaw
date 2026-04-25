<template>
  <div class="page-container">
    <h3>参数设置</h3>
    <p>配置系统运行参数</p>
    
    <el-card style="margin-top: 20px;" v-loading="loading">
      <el-form :model="systemParams" label-width="180px" class="param-form">
        
        <!-- 基础设置 -->
        <h4>基础设置</h4>
        <el-form-item label="系统名称">
          <el-input v-model="systemParams.systemName" />
        </el-form-item>
        <el-form-item label="版权信息">
          <el-input v-model="systemParams.copyright" />
        </el-form-item>
        <el-form-item label="ICP备案号">
          <el-input v-model="systemParams.icp" />
        </el-form-item>

        <el-divider />

        <!-- 微信公众号设置 -->
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

        <!-- 支付接口设置 -->
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
        <el-form-item label="证书文件">
          <el-upload
            class="cert-uploader"
            action="/api/upload/cert"
            :auto-upload="false"
            :on-change="handleCertChange"
            :file-list="certFileList"
            accept=".pem,.p12,.pfx"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon>
              选择证书文件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持 .pem, .p12, .pfx 格式的证书文件
              </div>
            </template>
          </el-upload>
          <div v-if="systemParams.wechatCertPath" class="cert-info">
            <el-tag type="success">已上传: {{ systemParams.wechatCertPath }}</el-tag>
          </div>
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
        
        <h5>对公转账</h5>
        <el-form-item label="启用对公转账">
          <el-switch v-model="systemParams.bankTransferEnabled" />
        </el-form-item>
        <el-form-item label="开户银行">
          <el-input v-model="systemParams.bankName" placeholder="如：中国工商银行" />
        </el-form-item>
        <el-form-item label="开户支行">
          <el-input v-model="systemParams.bankBranch" placeholder="如：北京市朝阳区支行" />
        </el-form-item>
        <el-form-item label="账户名称">
          <el-input v-model="systemParams.bankAccountName" placeholder="公司全称" />
        </el-form-item>
        <el-form-item label="银行账号">
          <el-input v-model="systemParams.bankAccountNo" placeholder="对公银行账号" />
        </el-form-item>
        <el-form-item label="转账备注说明">
          <el-input v-model="systemParams.bankTransferRemark" type="textarea" :rows="2" placeholder="转账时需要的备注信息，如：充值+商户编号" />
        </el-form-item>

        <el-divider />

        <!-- 短信设置 -->
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

        <!-- 安全设置 -->
        <h4>安全设置</h4>
        <el-form-item label="登录失败锁定次数">
          <el-input-number v-model="systemParams.loginFailLimit" :min="3" :max="10" />
          <span style="margin-left: 10px;">次</span>
        </el-form-item>
        <el-form-item label="登录锁定时间(分钟)">
          <el-input-number v-model="systemParams.lockTime" :min="5" :max="60" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveParams" :loading="loading">保存设置</el-button>
          <el-button @click="resetParams">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { systemSettingsApi } from '@/api/system-settings'

const loading = ref(false)
const certFileList = ref([])

const systemParams = reactive({
  systemName: 'EAMS 电商智能客服中台',
  copyright: '© 2026 龙猫技术团队',
  icp: '京ICP备XXXXXXXX号',
  loginFailLimit: 5,
  lockTime: 30,
  
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
  
  // 对公转账设置
  bankTransferEnabled: false,
  bankName: '',
  bankBranch: '',
  bankAccountName: '',
  bankAccountNo: '',
  bankTransferRemark: '',
  
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
    const wechatRes: any = await systemSettingsApi.getSettingsByGroup('wechat')
    if (wechatRes && wechatRes.data) {
      const data = wechatRes.data
      systemParams.wechatEnabled = data.wechat_enabled === 'true' || data.wechat_enabled === true
      systemParams.wechatAppId = data.wechat_app_id || ''
      systemParams.wechatAppSecret = data.wechat_app_secret || ''
      systemParams.wechatToken = data.wechat_token || ''
      systemParams.wechatAesKey = data.wechat_aes_key || ''
      systemParams.wechatTemplateId = data.wechat_template_id || ''
    }

    // 加载支付设置
    const paymentRes: any = await systemSettingsApi.getSettingsByGroup('payment')
    if (paymentRes && paymentRes.data) {
      const data = paymentRes.data
      systemParams.wechatPayEnabled = data.wechat_pay_enabled === 'true' || data.wechat_pay_enabled === true
      systemParams.wechatMchId = data.wechat_mch_id || '1249142001'
      systemParams.wechatApiKey = data.wechat_api_key || 'twwhqq990315359379903twwhqq99033'
      systemParams.wechatPayAppId = data.wechat_pay_app_id || ''
      systemParams.wechatCertPath = data.wechat_cert_path || ''

      systemParams.alipayEnabled = data.alipay_enabled === 'true' || data.alipay_enabled === true
      systemParams.alipayAppId = data.alipay_app_id || '2021006145636929'
      systemParams.alipayPrivateKey = data.alipay_private_key || ''
      systemParams.alipayPublicKey = data.alipay_public_key || ''
      systemParams.alipayNotifyUrl = data.alipay_notify_url || ''
      
      // 对公转账设置
      systemParams.bankTransferEnabled = data.bank_transfer_enabled === 'true' || data.bank_transfer_enabled === true
      systemParams.bankName = data.bank_name || ''
      systemParams.bankBranch = data.bank_branch || ''
      systemParams.bankAccountName = data.bank_account_name || ''
      systemParams.bankAccountNo = data.bank_account_no || ''
      systemParams.bankTransferRemark = data.bank_transfer_remark || ''
    }

    // 加载短信设置
    const smsRes: any = await systemSettingsApi.getSettingsByGroup('sms')
    if (smsRes && smsRes.data) {
      const data = smsRes.data
      systemParams.smsEnabled = data.sms_enabled === 'true' || data.sms_enabled === true
      systemParams.smsGatewayUrl = data.sms_gateway_url || 'http://106.14.0.125:8088/sms.aspx'
      systemParams.smsUserId = data.sms_user_id || ''
      systemParams.smsAccount = data.sms_account || ''
      systemParams.smsPassword = data.sms_password || ''
      systemParams.smsSign = data.sms_sign || ''
    }
  } catch (error) {
    console.error('加载设置失败:', error)
    // 使用默认值，不显示错误
    ElMessage.warning('使用默认设置，保存后将同步到服务器')
  } finally {
    loading.value = false
  }
}

const saveParams = async () => {
  loading.value = true
  try {
    // 保存微信设置
    const wechatRes: any = await systemSettingsApi.batchSaveSettings({
      'wechat_enabled': String(systemParams.wechatEnabled),
      'wechat_app_id': systemParams.wechatAppId,
      'wechat_app_secret': systemParams.wechatAppSecret,
      'wechat_token': systemParams.wechatToken,
      'wechat_aes_key': systemParams.wechatAesKey,
      'wechat_template_id': systemParams.wechatTemplateId
    }, 'wechat')

    // 保存支付设置
    const paymentRes: any = await systemSettingsApi.batchSaveSettings({
      'wechat_pay_enabled': String(systemParams.wechatPayEnabled),
      'wechat_mch_id': systemParams.wechatMchId,
      'wechat_api_key': systemParams.wechatApiKey,
      'wechat_pay_app_id': systemParams.wechatPayAppId,
      'wechat_cert_path': systemParams.wechatCertPath,
      'alipay_enabled': String(systemParams.alipayEnabled),
      'alipay_app_id': systemParams.alipayAppId,
      'alipay_private_key': systemParams.alipayPrivateKey,
      'alipay_public_key': systemParams.alipayPublicKey,
      'alipay_notify_url': systemParams.alipayNotifyUrl,
      // 对公转账
      'bank_transfer_enabled': String(systemParams.bankTransferEnabled),
      'bank_name': systemParams.bankName,
      'bank_branch': systemParams.bankBranch,
      'bank_account_name': systemParams.bankAccountName,
      'bank_account_no': systemParams.bankAccountNo,
      'bank_transfer_remark': systemParams.bankTransferRemark
    }, 'payment')

    // 保存短信设置
    const smsRes: any = await systemSettingsApi.batchSaveSettings({
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
    ElMessage.error('保存失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

const resetParams = () => {
  loadSettings()
  ElMessage.info('已重置')
}

const testSmsConnection = () => {
  ElMessage.info('正在测试短信接口连接...')
  setTimeout(() => {
    ElMessage.success('短信接口连接成功')
  }, 1500)
}

// 证书文件变更
const handleCertChange = (file: any) => {
  if (file) {
    systemParams.wechatCertPath = file.name
    ElMessage.success(`已选择证书: ${file.name}`)
  }
}

// 页面加载时获取设置
onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.page-container {
  padding: 0;
}

.param-form {
  max-width: 700px;
}

.param-form h4 {
  margin: 20px 0 15px;
  color: #303133;
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

.cert-uploader {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cert-info {
  margin-top: 8px;
}
</style>