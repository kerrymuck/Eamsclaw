<template>
  <div class="plan-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>📦 套餐管理</h2>
        <p class="subtitle">查看系统套餐及您的拿货价格</p>
      </div>
    </div>

    <!-- 我的等级信息 -->
    <el-card class="level-card">
      <template #header>
        <div class="card-header">
          <span>我的等级信息</span>
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
            <div class="info-label">累计充值</div>
            <div class="info-value">¥{{ providerInfo.totalRecharge.toLocaleString() }}</div>
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
          <div class="upgrade-benefit-box">
            <el-icon :size="20" color="#67c23a"><CircleCheck /></el-icon>
            <div class="benefit-text">
              <div class="benefit-title">晋升{{ nextLevel.name }}后可享受 {{ nextLevel.discount }}% 的拿货折扣</div>
              <div class="benefit-desc">比现在多省 {{ providerInfo.discount - nextLevel.discount }}% 的成本</div>
            </div>
            <el-button type="success" size="large" class="upgrade-btn">
              <el-icon><TrendCharts /></el-icon>
              马上升级
            </el-button>
          </div>
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

    <!-- 套餐列表 -->
    <el-card class="plan-list-card">
      <template #header>
        <div class="card-header">
          <div>
            <span>系统套餐及拿货价</span>
            <el-tag type="info" style="margin-left: 10px;">您的折扣：{{ providerInfo.discount }}%</el-tag>
          </div>
        </div>
      </template>
      
      <el-alert
        title="拿货价说明"
        :description="`以下展示系统标准套餐价格及您的拿货价格（按${providerInfo.discount}%折扣计算）。定制版价格根据店铺数量自动计算后应用折扣。`"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      />
      
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="plan in planList" :key="plan.id">
          <el-card class="plan-card" :class="{ 'custom-plan': plan.type === 'custom' }">
            <template #header>
              <div class="plan-header">
                <div class="plan-title">
                  <el-tag :type="getPlanTagType(plan.type)" size="small">{{ plan.level }}</el-tag>
                  <h4>{{ plan.name }}</h4>
                </div>
              </div>
            </template>
            
            <div class="plan-body">
              <!-- 标准套餐价格 -->
              <template v-if="plan.type !== 'custom'">
                <div class="price-section">
                  <div class="original-price">
                    <span class="price-label">系统售价</span>
                    <span class="price-value">¥{{ plan.price }}</span>
                    <span class="price-unit">/{{ plan.duration }}个月</span>
                  </div>
                  <div class="provider-price">
                    <span class="price-label">您的拿货价</span>
                    <span class="price-value discount">¥{{ calculateProviderPrice(plan.price) }}</span>
                    <el-tag type="danger" size="small" effect="plain" class="save-tag">
                      省 ¥{{ plan.price - calculateProviderPrice(plan.price) }}
                    </el-tag>
                  </div>
                </div>
              </template>
              
              <!-- 定制版价格计算器 -->
              <template v-else>
                <div class="custom-price-section">
                  <div class="custom-price-base">
                    <div class="price-row">
                      <span class="price-label">旗舰版基础</span>
                      <span class="price-value">¥{{ ultimatePlanPrice }}</span>
                    </div>
                    <div class="price-row provider-price-row">
                      <span class="price-label">拿货价</span>
                      <span class="price-value discount">¥{{ calculateProviderPrice(ultimatePlanPrice) }}</span>
                    </div>
                  </div>
                  <div class="custom-price-input">
                    <span>店铺数量：</span>
                    <el-input-number 
                      v-model="customShopCount" 
                      :min="ultimatePlanMaxShops + 1" 
                      :max="9999" 
                      size="small"
                      style="width: 100px"
                    />
                    <span class="input-hint">个</span>
                  </div>
                  <div class="custom-price-result" v-if="customShopCount > ultimatePlanMaxShops">
                    <div class="calc-detail">
                      超出 {{ customShopCount - ultimatePlanMaxShops }} 个 × ¥{{ licenseUnitPrice }} = ¥{{ ((customShopCount - ultimatePlanMaxShops) * licenseUnitPrice).toFixed(2) }}
                    </div>
                    <div class="calc-total">
                      <span class="total-label">系统售价：</span>
                      <span class="total-value">¥{{ calculatedCustomPrice }}</span>
                    </div>
                    <div class="calc-provider">
                      <span class="total-label">您的拿货价：</span>
                      <span class="total-value discount">¥{{ calculateProviderPrice(calculatedCustomPrice) }}</span>
                      <el-tag type="danger" size="small" effect="plain" class="save-tag">
                        省 ¥{{ (calculatedCustomPrice - calculateProviderPrice(calculatedCustomPrice)).toFixed(2) }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </template>
              
              <div class="plan-features">
                <div class="feature-item">
                  <el-icon><Shop /></el-icon>
                  <span>支持店铺数量：<strong>{{ plan.maxShops }}</strong> 个</span>
                </div>
                <div class="feature-item">
                  <el-icon><Key /></el-icon>
                  <span>授权码数量：<strong>{{ plan.licenseCount }}</strong> 个</span>
                </div>
                <div class="feature-item">
                  <el-icon><Calendar /></el-icon>
                  <span>套餐时长：<strong>{{ plan.duration }}</strong> 个月</span>
                </div>
                <div class="feature-item">
                  <el-icon><User /></el-icon>
                  <span>员工账号：<strong>{{ plan.maxStaff }}</strong> 个</span>
                </div>
                <div class="feature-item">
                  <el-icon><Service /></el-icon>
                  <span>客服支持：<strong>{{ plan.support }}</strong></span>
                </div>
              </div>
              
              <div class="plan-description">
                <p>{{ plan.description }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { TrendCharts, Trophy, Shop, Key, Calendar, User, Service, CircleCheck } from '@element-plus/icons-vue'

// 服务商等级定义（与超管后台一致）
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
  totalRecharge: 45600
})

// 计算下一等级
const nextLevel = computed(() => {
  const currentIndex = levelList.value.findIndex(l => l.discount === providerInfo.discount)
  if (currentIndex > 0) {
    return levelList.value[currentIndex - 1]
  }
  return null
})

// 旗舰版配置（用于定制版价格计算）
const ultimatePlanPrice = ref(2999)
const ultimatePlanMaxShops = ref(50)
const licenseUnitPrice = ref(19.9)

// 定制版店铺数量
const customShopCount = ref(51)

// 计算定制版系统售价
const calculatedCustomPrice = computed(() => {
  if (customShopCount.value <= ultimatePlanMaxShops.value) {
    return ultimatePlanPrice.value
  }
  const extraShops = customShopCount.value - ultimatePlanMaxShops.value
  return ultimatePlanPrice.value + (extraShops * licenseUnitPrice.value)
})

// 计算服务商拿货价
const calculateProviderPrice = (systemPrice: number) => {
  return Math.round(systemPrice * (providerInfo.discount / 100))
}

interface Plan {
  id: string
  name: string
  level: string
  type: string
  price: number
  duration: number
  maxShops: number
  licenseCount: number
  maxStaff: number
  support: string
  description: string
}

// 系统套餐列表（与超管后台一致）
const planList = ref<Plan[]>([
  {
    id: 'P001',
    name: '免费版',
    level: 'L1',
    type: 'free',
    price: 0,
    duration: 12,
    maxShops: 1,
    licenseCount: 1,
    maxStaff: 2,
    support: '在线文档',
    description: '适合个人创业者，体验基础功能'
  },
  {
    id: 'P002',
    name: '普通版',
    level: 'L2',
    type: 'basic',
    price: 299,
    duration: 12,
    maxShops: 1,
    licenseCount: 1,
    maxStaff: 5,
    support: '工单支持',
    description: '适合小型商家，满足日常经营需求'
  },
  {
    id: 'P003',
    name: '标准版',
    level: 'L3',
    type: 'standard',
    price: 599,
    duration: 12,
    maxShops: 3,
    licenseCount: 3,
    maxStaff: 10,
    support: '在线客服',
    description: '适合成长型商家，支持多店铺管理'
  },
  {
    id: 'P004',
    name: '高级版',
    level: 'L4',
    type: 'premium',
    price: 1299,
    duration: 12,
    maxShops: 10,
    licenseCount: 10,
    maxStaff: 30,
    support: '专属客服',
    description: '适合中大型商家，功能全面支持'
  },
  {
    id: 'P005',
    name: '旗舰版',
    level: 'L5',
    type: 'ultimate',
    price: 2999,
    duration: 12,
    maxShops: 50,
    licenseCount: 50,
    maxStaff: 100,
    support: '7x24小时',
    description: '适合大型连锁企业，无限制扩展'
  },
  {
    id: 'P006',
    name: '定制版',
    level: 'L6',
    type: 'custom',
    price: 0,
    duration: 12,
    maxShops: 9999,
    licenseCount: 9999,
    maxStaff: 999,
    support: '7x24小时',
    description: '专属定制方案，按需订购授权码'
  }
])

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

const getPlanTagType = (type: string) => {
  const map: Record<string, string> = {
    free: 'info',
    basic: '',
    standard: 'success',
    premium: 'warning',
    ultimate: 'danger',
    custom: 'primary'
  }
  return map[type] || ''
}
</script>

<style scoped>
.plan-management {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h2 {
  margin: 0 0 8px 0;
}

.subtitle {
  color: #909399;
  margin: 0;
}

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

.upgrade-benefit-box {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 16px 20px;
  background: #f0f9eb;
  border: 1px solid #b3e19d;
  border-radius: 8px;
}

.benefit-text {
  flex: 1;
}

.benefit-title {
  font-size: 15px;
  font-weight: 600;
  color: #67c23a;
  margin-bottom: 4px;
}

.benefit-desc {
  font-size: 13px;
  color: #909399;
}

.upgrade-btn {
  margin-left: auto;
}

.max-level {
  padding: 20px 0;
}

.plan-list-card {
  margin-bottom: 20px;
}

.plan-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.plan-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.custom-plan {
  border: 2px solid #409eff;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plan-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.plan-title h4 {
  margin: 0;
  font-size: 18px;
}

.plan-body {
  padding: 10px 0;
}

.price-section {
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.original-price {
  margin-bottom: 10px;
}

.price-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.price-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.price-value.discount {
  color: #f56c6c;
}

.price-unit {
  font-size: 14px;
  color: #909399;
}

.provider-price {
  position: relative;
  padding: 10px;
  background: #fff5f5;
  border-radius: 8px;
}

.save-tag {
  position: absolute;
  top: 0;
  right: 0;
  transform: translate(30%, -30%);
}

.custom-price-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.custom-price-base {
  margin-bottom: 15px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.provider-price-row {
  padding: 8px;
  background: #fff5f5;
  border-radius: 4px;
}

.custom-price-input {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.custom-price-input span {
  font-size: 13px;
  color: #606266;
}

.input-hint {
  font-size: 12px;
  color: #909399;
}

.custom-price-result {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
}

.calc-detail {
  font-size: 12px;
  color: #606266;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #dcdfe6;
}

.calc-total, .calc-provider {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.calc-provider {
  padding: 8px;
  background: #fff5f5;
  border-radius: 4px;
  margin-bottom: 0;
}

.total-label {
  font-size: 13px;
  color: #606266;
}

.total-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.total-value.discount {
  color: #f56c6c;
}

.plan-features {
  margin-bottom: 15px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px dashed #ebeef5;
  font-size: 13px;
}

.feature-item:last-child {
  border-bottom: none;
}

.feature-item .el-icon {
  color: #409eff;
  font-size: 16px;
}

.plan-description {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.plan-description p {
  margin: 0;
  font-size: 12px;
  color: #606266;
}
</style>
