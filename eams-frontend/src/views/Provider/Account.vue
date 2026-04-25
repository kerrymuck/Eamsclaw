<template>
  <div class="account-management">
    <div class="page-header">
      <h2>👤 账号管理</h2>
      <p class="subtitle">管理您的账号信息、等级及账户余额</p>
    </div>

    <!-- 服务商等级信息 -->
    <el-card class="level-card">
      <template #header>
        <div class="card-header">
          <span>服务商等级信息</span>
          <el-tag :type="getLevelType(providerInfo.level)" size="large" effect="dark">
            {{ getLevelText(providerInfo.level) }}
          </el-tag>
        </div>
      </template>
      
      <el-row :gutter="40">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="info-item">
            <div class="info-label">当前等级</div>
            <div class="info-value">{{ getLevelText(providerInfo.level) }}</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="info-item">
            <div class="info-label">拿货折扣</div>
            <div class="info-value discount">{{ providerInfo.discount }}%</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="info-item">
            <div class="info-label">已售授权数</div>
            <div class="info-value">{{ providerInfo.soldLicenses }}</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="info-item">
            <div class="info-label">账户余额</div>
            <div class="info-value balance">¥{{ providerInfo.balance.toLocaleString() }}</div>
          </div>
        </el-col>
      </el-row>
      
      <!-- 晋升信息 -->
      <div class="upgrade-section" v-if="nextLevel">
        <el-divider />
        <div class="upgrade-header">
          <el-icon :size="20" color="#409eff"><TrendCharts /></el-icon>
          <span class="upgrade-title">晋升下一等级：{{ nextLevel.name }}</span>
        </div>
        
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :xs="24" :sm="12">
            <div class="progress-item">
              <div class="progress-label">
                <span>授权数进度</span>
                <span class="progress-value">{{ providerInfo.soldLicenses }} / {{ nextLevel.minLicenses }}</span>
              </div>
              <el-progress 
                :percentage="Math.min(100, Math.round((providerInfo.soldLicenses / nextLevel.minLicenses) * 100))" 
                :status="providerInfo.soldLicenses >= nextLevel.minLicenses ? 'success' : ''"
                :stroke-width="18"
                striped
              />
              <div class="progress-hint" v-if="providerInfo.soldLicenses < nextLevel.minLicenses">
                还需售出 <strong>{{ nextLevel.minLicenses - providerInfo.soldLicenses }}</strong> 个授权
              </div>
              <div class="progress-hint success" v-else>
                <el-icon><CircleCheck /></el-icon> 授权数已达标
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" v-if="nextLevel.upgradeAmount > 0">
            <div class="progress-item">
              <div class="progress-label">
                <span>充值金额进度</span>
                <span class="progress-value">¥{{ providerInfo.totalRecharge.toLocaleString() }} / ¥{{ nextLevel.upgradeAmount.toLocaleString() }}</span>
              </div>
              <el-progress 
                :percentage="Math.min(100, Math.round((providerInfo.totalRecharge / nextLevel.upgradeAmount) * 100))" 
                :status="providerInfo.totalRecharge >= nextLevel.upgradeAmount ? 'success' : ''"
                :stroke-width="18"
                striped
              />
              <div class="progress-hint" v-if="providerInfo.totalRecharge < nextLevel.upgradeAmount">
                还需充值 <strong>¥{{ (nextLevel.upgradeAmount - providerInfo.totalRecharge).toLocaleString() }}</strong>
              </div>
              <div class="progress-hint success" v-else>
                <el-icon><CircleCheck /></el-icon> 充值金额已达标
              </div>
            </div>
          </el-col>
        </el-row>
        
        <div class="upgrade-benefit" v-if="nextLevel">
          <el-alert
            :title="`晋升${nextLevel.name}后可享受 ${nextLevel.discount}% 的拿货折扣`"
            :description="`比现在多省 ${providerInfo.discount - nextLevel.discount}% 的成本，立即行动吧！`"
            type="success"
            :closable="false"
            show-icon
          />
        </div>
      </div>
      
      <div class="max-level" v-else>
        <el-divider />
        <el-result icon="success" title="恭喜您达到最高等级！">
          <template #icon>
            <el-icon :size="60" color="#67c23a"><Trophy /></el-icon>
          </template>
          <template #sub-title>
            您已是金牌服务商，享受最高60%的拿货折扣
          </template>
        </el-result>
      </div>
    </el-card>

    <!-- 账户充值信息 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :xs="24" :md="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>账户余额</span>
              <el-button type="primary" @click="showRechargeDialog = true">
                <el-icon><Plus /></el-icon> 立即充值
              </el-button>
            </div>
          </template>
          
          <div class="balance-display">
            <div class="balance-amount">
              <span class="balance-label">当前余额</span>
              <span class="balance-value">¥{{ providerInfo.balance.toLocaleString() }}</span>
            </div>
            <div class="balance-stats">
              <div class="stat-item">
                <div class="stat-label">累计充值</div>
                <div class="stat-value">¥{{ providerInfo.totalRecharge.toLocaleString() }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">累计消费</div>
                <div class="stat-value">¥{{ (providerInfo.totalRecharge - providerInfo.balance).toLocaleString() }}</div>
              </div>
            </div>
          </div>
          
          <el-divider />
          
          <div class="recharge-rules">
            <div class="rules-title">
              <el-icon><InfoFilled /></el-icon>
              充值规则
            </div>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="最低充值金额">¥{{ rechargeSettings.minAmount }}</el-descriptions-item>
              <el-descriptions-item label="充值方式">{{ rechargeSettings.methods.join('、') }}</el-descriptions-item>
              <el-descriptions-item label="到账时间">{{ rechargeSettings.arrivalTime }}</el-descriptions-item>
              <el-descriptions-item label="发票说明">{{ rechargeSettings.invoiceNote }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :md="8">
        <el-card>
          <template #header>
            <span>快速充值</span>
          </template>
          
          <div class="quick-recharge">
            <div 
              v-for="amount in quickAmounts" 
              :key="amount"
              class="amount-option"
              :class="{ active: selectedAmount === amount }"
              @click="selectedAmount = amount"
            >
              <span class="amount-value">¥{{ amount.toLocaleString() }}</span>
              <el-tag v-if="amount >= 10000" type="danger" size="small" effect="plain">送5%</el-tag>
            </div>
            <div class="amount-option custom" :class="{ active: selectedAmount === 0 }" @click="selectedAmount = 0">
              <el-input-number v-model="customAmount" :min="rechargeSettings.minAmount" :step="100" controls-position="right" style="width: 100%" />
            </div>
          </div>
          
          <el-button type="primary" size="large" style="width: 100%; margin-top: 20px;" @click="handleQuickRecharge">
            确认充值 ¥{{ rechargeAmount.toLocaleString() }}
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 账号信息卡片 -->
    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <el-card class="info-card">
          <template #header>
            <span>基本信息</span>
          </template>
          <div class="profile-section">
            <div class="avatar-section">
              <el-avatar :size="100" :src="userInfo.avatar">{{ userInfo.name.charAt(0) }}</el-avatar>
              <el-button class="change-avatar" size="small" @click="changeAvatar">
                更换头像
              </el-button>
            </div>
            <el-form :model="userInfo" label-width="100px" class="info-form">
              <el-form-item label="企业名称">
                <el-input v-model="userInfo.company" />
              </el-form-item>
              <el-form-item label="联系人">
                <el-input v-model="userInfo.name" />
              </el-form-item>
              <el-form-item label="联系电话">
                <el-input v-model="userInfo.phone" />
              </el-form-item>
              <el-form-item label="邮箱">
                <el-input v-model="userInfo.email" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveInfo">保存修改</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card class="security-card">
          <template #header>
            <span>安全设置</span>
          </template>
          <div class="security-list">
            <div class="security-item">
              <div class="item-info">
                <div class="item-title">登录密码</div>
                <div class="item-desc">定期更换密码有助于保护账号安全</div>
              </div>
              <el-button @click="showPasswordDialog = true">修改</el-button>
            </div>
            <el-divider />
            <div class="security-item">
              <div class="item-info">
                <div class="item-title">手机绑定</div>
                <div class="item-desc">已绑定: {{ userInfo.phone }}</div>
              </div>
              <el-button @click="showPhoneDialog = true">更换</el-button>
            </div>
            <el-divider />
            <div class="security-item">
              <div class="item-info">
                <div class="item-title">邮箱绑定</div>
                <div class="item-desc">已绑定: {{ userInfo.email }}</div>
              </div>
              <el-button @click="showEmailDialog = true">更换</el-button>
            </div>
            <el-divider />
            <div class="security-item">
              <div class="item-info">
                <div class="item-title">登录设备管理</div>
                <div class="item-desc">管理已登录的设备</div>
              </div>
              <el-button @click="showDevicesDialog = true">查看</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="原密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="savePassword">确认修改</el-button>
      </template>
    </el-dialog>

    <!-- 充值对话框 -->
    <el-dialog v-model="showRechargeDialog" title="账户充值" width="500px">
      <el-form :model="rechargeForm" label-width="100px">
        <el-form-item label="充值金额">
          <el-input-number v-model="rechargeForm.amount" :min="rechargeSettings.minAmount" :step="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="支付方式">
          <el-radio-group v-model="rechargeForm.method">
            <el-radio-button label="alipay">支付宝</el-radio-button>
            <el-radio-button label="wechat">微信支付</el-radio-button>
            <el-radio-button label="bank">银行转账</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="rechargeForm.remark" type="textarea" rows="2" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRechargeDialog = false">取消</el-button>
        <el-button type="primary" @click="handleRechargeSubmit">确认充值</el-button>
      </template>
    </el-dialog>

    <!-- 更换手机弹窗 -->
    <el-dialog v-model="showPhoneDialog" title="更换手机号" width="400px">
      <el-form :model="phoneForm" label-width="100px">
        <el-form-item label="新手机号">
          <el-input v-model="phoneForm.phone" placeholder="请输入新手机号" />
        </el-form-item>
        <el-form-item label="验证码">
          <el-input v-model="phoneForm.code" placeholder="请输入验证码">
            <template #append>
              <el-button @click="sendCode" :disabled="codeSending">
                {{ codeSending ? `${codeCountdown}s` : '获取验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPhoneDialog = false">取消</el-button>
        <el-button type="primary" @click="savePhone">确认更换</el-button>
      </template>
    </el-dialog>

    <!-- 登录设备管理弹窗 -->
    <el-dialog v-model="showDevicesDialog" title="登录设备管理" width="600px">
      <el-table :data="deviceList" stripe>
        <el-table-column prop="device" label="设备" min-width="200">
          <template #default="{ row }">
            <div class="device-info">
              <el-icon :size="20"><Monitor v-if="row.type === 'pc'" /><Cellphone v-else /></el-icon>
              <span>{{ row.device }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="地点" width="120" />
        <el-table-column prop="time" label="登录时间" width="160" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button v-if="!row.current" link type="danger" @click="logoutDevice(row)">
              下线
            </el-button>
            <el-tag v-else size="small" type="success">当前</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { Monitor, Cellphone, TrendCharts, Trophy, CircleCheck, Money, Wallet } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 服务商等级定义
interface Level {
  name: string
  minLicenses: number
  maxLicenses: number
  discount: number
  upgradeAmount: number
}

const levelList = ref<Level[]>([
  { name: '金牌服务商', minLicenses: 100, maxLicenses: 999999, discount: 60, upgradeAmount: 100000 },
  { name: '银牌服务商', minLicenses: 50, maxLicenses: 99, discount: 75, upgradeAmount: 50000 },
  { name: '铜牌服务商', minLicenses: 20, maxLicenses: 49, discount: 85, upgradeAmount: 20000 },
  { name: '普通服务商', minLicenses: 0, maxLicenses: 19, discount: 100, upgradeAmount: 0 }
])

// 当前服务商信息
const providerInfo = reactive({
  name: '科技云',
  level: 'silver',
  discount: 75,
  soldLicenses: 68,
  totalRecharge: 45600,
  balance: 23400
})

// 计算下一等级
const nextLevel = computed(() => {
  const currentIndex = levelList.value.findIndex(l => l.discount === providerInfo.discount)
  if (currentIndex > 0) {
    return levelList.value[currentIndex - 1]
  }
  return null
})

// 充值设置（与系统后台一致）
const rechargeSettings = reactive({
  minAmount: 1000,
  methods: ['支付宝', '微信支付', '银行转账'],
  arrivalTime: '即时到账',
  invoiceNote: '充值后可申请开具增值税普通发票'
})

// 快速充值金额
const quickAmounts = [1000, 5000, 10000, 50000]
const selectedAmount = ref(5000)
const customAmount = ref(1000)

const rechargeAmount = computed(() => {
  if (selectedAmount.value === 0) {
    return customAmount.value
  }
  return selectedAmount.value
})

// 充值记录
const rechargeRecords = ref([
  { orderNo: 'R202604160001', amount: 10000, gift: 500, method: '支付宝', status: 'success', createTime: '2026-04-16 10:30:00', remark: '活动赠送5%' },
  { orderNo: 'R202604010002', amount: 5000, gift: 0, method: '微信支付', status: 'success', createTime: '2026-04-01 14:20:00', remark: '' },
  { orderNo: 'R202603150003', amount: 20000, gift: 1000, method: '银行转账', status: 'success', createTime: '2026-03-15 09:00:00', remark: '大额充值赠送' },
  { orderNo: 'R202603010004', amount: 3000, gift: 0, method: '支付宝', status: 'success', createTime: '2026-03-01 16:45:00', remark: '' },
  { orderNo: 'R202602200005', amount: 5000, gift: 0, method: '微信支付', status: 'success', createTime: '2026-02-20 11:30:00', remark: '' }
])

const userInfo = reactive({
  avatar: '',
  company: '智慧零售科技有限公司',
  name: '张三',
  phone: '13800138000',
  email: 'zhangsan@example.com'
})

const showPasswordDialog = ref(false)
const showPhoneDialog = ref(false)
const showEmailDialog = ref(false)
const showDevicesDialog = ref(false)
const showRechargeDialog = ref(false)

const rechargeForm = reactive({
  amount: 5000,
  method: 'alipay',
  remark: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const phoneForm = reactive({
  phone: '',
  code: ''
})

const codeSending = ref(false)
const codeCountdown = ref(60)

const deviceList = ref([
  { device: 'Windows 10 - Chrome', type: 'pc', location: '北京', time: '2026-04-10 14:30:00', current: true },
  { device: 'iPhone 15 - Safari', type: 'mobile', location: '北京', time: '2026-04-09 09:15:00', current: false },
  { device: 'MacBook Pro - Chrome', type: 'pc', location: '上海', time: '2026-04-08 18:20:00', current: false }
])

const changeAvatar = () => {
  ElMessage.info('更换头像功能')
}

const saveInfo = () => {
  ElMessage.success('信息保存成功')
}

const savePassword = () => {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  ElMessage.success('密码修改成功')
  showPasswordDialog.value = false
}

const sendCode = () => {
  codeSending.value = true
  codeCountdown.value = 60
  const timer = setInterval(() => {
    codeCountdown.value--
    if (codeCountdown.value <= 0) {
      clearInterval(timer)
      codeSending.value = false
    }
  }, 1000)
  ElMessage.success('验证码已发送')
}

const savePhone = () => {
  ElMessage.success('手机号更换成功')
  showPhoneDialog.value = false
}

const logoutDevice = (row: any) => {
  const index = deviceList.value.indexOf(row)
  if (index > -1) {
    deviceList.value.splice(index, 1)
    ElMessage.success('设备已下线')
  }
}

const getLevelType = (level: string) => {
  const map: Record<string, string> = {
    gold: 'danger',
    silver: '',
    bronze: 'warning',
    normal: 'info'
  }
  return map[level] || 'info'
}

const getLevelText = (level: string) => {
  const map: Record<string, string> = {
    gold: '金牌服务商',
    silver: '银牌服务商',
    bronze: '铜牌服务商',
    normal: '普通服务商'
  }
  return map[level] || level
}

const handleQuickRecharge = () => {
  ElMessage.success(`正在跳转充值 ¥${rechargeAmount.value}...`)
}

const handleRechargeSubmit = () => {
  ElMessage.success('充值申请已提交')
  showRechargeDialog.value = false
}
</script>

<style scoped>
.account-management {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
}

.subtitle {
  color: #909399;
  margin: 0;
}

.info-card, .security-card {
  margin-bottom: 20px;
}

.profile-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
}

.change-avatar {
  margin-top: 12px;
}

.info-form {
  width: 100%;
}

.security-list {
  padding: 10px 0;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.item-title {
  font-weight: 500;
  color: #1a1a2e;
  margin-bottom: 4px;
}

.item-desc {
  font-size: 13px;
  color: #909399;
}

.device-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 等级信息样式 */
.level-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-item {
  text-align: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.info-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.info-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.info-value.discount {
  color: #f56c6c;
}

.info-value.balance {
  color: #67c23a;
}

.upgrade-section {
  margin-top: 10px;
}

.upgrade-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.upgrade-title {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
}

.progress-item {
  margin-bottom: 20px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.progress-value {
  color: #409eff;
  font-weight: 500;
}

.progress-hint {
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
}

.progress-hint strong {
  color: #f56c6c;
}

.progress-hint.success {
  color: #67c23a;
  display: flex;
  align-items: center;
  gap: 4px;
}

.upgrade-benefit {
  margin-top: 20px;
}

.max-level {
  padding: 20px 0;
}

/* 账户余额样式 */
.balance-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
}

.balance-amount {
  display: flex;
  flex-direction: column;
}

.balance-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.balance-value {
  font-size: 36px;
  font-weight: bold;
  color: #f56c6c;
}

.balance-stats {
  display: flex;
  gap: 30px;
}

.balance-stats .stat-item {
  text-align: center;
}

.balance-stats .stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.balance-stats .stat-value {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.recharge-rules {
  margin-top: 10px;
}

.rules-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 15px;
}

/* 快速充值样式 */
.quick-recharge {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.amount-option {
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.amount-option:hover {
  border-color: #409eff;
}

.amount-option.active {
  border-color: #409eff;
  background: #f0f9ff;
}

.amount-option.custom {
  grid-column: span 2;
  padding: 10px;
}

.amount-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
</style>
