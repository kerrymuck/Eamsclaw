<template>
  <div class="plan-page">
    <!-- 当前套餐信息 -->
    <el-card class="current-plan-card">
      <template #header>
        <div class="card-header">
          <span>我的套餐</span>
          <el-tag :type="currentPlan.tagType" size="large">{{ currentPlan.name }}</el-tag>
        </div>
      </template>
      
      <div class="current-plan-info">
        <el-row :gutter="40">
          <el-col :xs="24" :sm="12" :md="6">
            <div class="info-item">
              <div class="info-label">套餐到期</div>
              <div class="info-value" :class="{ 'expired': isExpired }">
                {{ currentPlan.expireDate }}
                <el-tag v-if="isExpired" type="danger" size="small">已过期</el-tag>
                <el-tag v-else-if="isNearExpire" type="warning" size="small">即将过期</el-tag>
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="info-item">
              <div class="info-label">店铺数量</div>
              <div class="info-value">
                <span :class="{ 'warning': currentPlan.shopCount >= currentPlan.maxShops }">
                  {{ currentPlan.shopCount }}
                </span>
                / {{ currentPlan.maxShops }}
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="info-item">
              <div class="info-label">员工账号</div>
              <div class="info-value">
                <span :class="{ 'warning': currentPlan.staffCount >= currentPlan.maxStaff }">
                  {{ currentPlan.staffCount }}
                </span>
                / {{ currentPlan.maxStaff }}
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="info-item">
              <div class="info-label">客服支持</div>
              <div class="info-value">{{ currentPlan.support }}</div>
            </div>
          </el-col>
        </el-row>
        
        <div class="plan-actions" v-if="!isExpired">
          <el-button type="primary" size="large" @click="handleRenew">
            <el-icon><Refresh /></el-icon>
            续费套餐
          </el-button>
          <el-button size="large" @click="handleUpgrade" v-if="currentPlan.type !== 'ultimate'">
            <el-icon><Top /></el-icon>
            升级套餐
          </el-button>
        </div>
        <div class="plan-actions" v-else>
          <el-button type="danger" size="large" @click="handleRenew">
            <el-icon><Warning /></el-icon>
            立即续费
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 套餐对比 -->
    <el-card class="plan-compare-card">
      <template #header>
        <div class="card-header">
          <span>套餐版本对比</span>
          <el-radio-group v-model="billingCycle" size="small">
            <el-radio-button label="monthly">月付</el-radio-button>
            <el-radio-button label="yearly">年付</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
      <div class="plan-list">
        <el-row :gutter="20">
          <el-col 
            :xs="24" 
            :sm="12" 
            :md="8" 
            v-for="plan in planList" 
            :key="plan.id"
          >
            <div 
              class="plan-item" 
              :class="{ 
                'current': plan.type === currentPlan.type,
                'recommended': plan.recommended 
              }"
            >
              <div class="plan-header">
                <h4>{{ plan.name }}</h4>
                <el-tag v-if="plan.type === currentPlan.type" type="success" size="small">当前</el-tag>
                <el-tag v-if="plan.recommended" type="danger" size="small" effect="dark">推荐</el-tag>
              </div>
              
              <div class="plan-price" :class="{ 'custom-price': plan.type === 'custom' }">
                <template v-if="plan.type === 'custom'">
                  <div class="custom-price-section">
                    <div class="custom-price-base">旗舰版基础 ¥{{ ultimatePlanPrice }}/年</div>
                    <div class="custom-price-input">
                      <span>店铺数量：</span>
                      <el-input-number 
                        v-model="customShopCount" 
                        :min="ultimatePlanMaxShops + 1" 
                        :max="9999" 
                        size="small"
                        style="width: 100px"
                        @change="calculateCustomPrice"
                      />
                      <span class="input-hint">个</span>
                    </div>
                    <div class="custom-price-result" v-if="customShopCount > ultimatePlanMaxShops">
                      <div class="price-calc-detail">
                        超出 {{ customShopCount - ultimatePlanMaxShops }} 个 × ¥{{ licenseUnitPrice }}
                      </div>
                      <div class="price-calc-total">
                        <span class="price-symbol">¥</span>
                        <span class="price-value">{{ calculatedCustomPrice }}</span>
                        <span class="price-unit">/年</span>
                      </div>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <span class="price-symbol">¥</span>
                  <span class="price-value">{{ billingCycle === 'yearly' ? plan.yearlyPrice : plan.monthlyPrice }}</span>
                  <span class="price-unit">/{{ billingCycle === 'yearly' ? '年' : '月' }}</span>
                </template>
              </div>
              
              <div class="plan-original-price" v-if="plan.type !== 'custom' && billingCycle === 'yearly' && plan.yearlyPrice < plan.monthlyPrice * 12">
                <span>原价 ¥{{ plan.monthlyPrice * 12 }}</span>
                <el-tag type="danger" size="small">省{{ Math.round((1 - plan.yearlyPrice / (plan.monthlyPrice * 12)) * 100) }}%</el-tag>
              </div>
              
              <div class="plan-features">
                <div class="feature-item">
                  <el-icon><Shop /></el-icon>
                  <span>店铺数量：{{ plan.maxShops }} 个</span>
                </div>
                <div class="feature-item">
                  <el-icon><Key /></el-icon>
                  <span>授权码数量：{{ plan.licenseCount }} 个</span>
                </div>
                <div class="feature-item">
                  <el-icon><User /></el-icon>
                  <span>员工账号：{{ plan.maxStaff }} 个</span>
                </div>
                <div class="feature-item">
                  <el-icon><ChatDotRound /></el-icon>
                  <span>消息中心：<el-icon v-if="plan.inbox" color="#67c23a"><CircleCheck /></el-icon><el-icon v-else color="#909399"><CircleClose /></el-icon></span>
                </div>
                <div class="feature-item">
                  <el-icon><Collection /></el-icon>
                  <span>知识库：<el-icon v-if="plan.knowledge" color="#67c23a"><CircleCheck /></el-icon><el-icon v-else color="#909399"><CircleClose /></el-icon></span>
                </div>
                <div class="feature-item">
                  <el-icon><Tickets /></el-icon>
                  <span>工单流转：<el-icon v-if="plan.tickets" color="#67c23a"><CircleCheck /></el-icon><el-icon v-else color="#909399"><CircleClose /></el-icon></span>
                </div>
                <div class="feature-item">
                  <el-icon><TrendCharts /></el-icon>
                  <span>绩效管理：<el-icon v-if="plan.performance" color="#67c23a"><CircleCheck /></el-icon><el-icon v-else color="#909399"><CircleClose /></el-icon></span>
                </div>
                <div class="feature-item">
                  <el-icon><Box /></el-icon>
                  <span>订单管理：<el-icon v-if="plan.orders" color="#67c23a"><CircleCheck /></el-icon><el-icon v-else color="#909399"><CircleClose /></el-icon></span>
                </div>
                <div class="feature-item">
                  <el-icon><Lightning /></el-icon>
                  <span>AI算力中心：<el-icon v-if="plan.aiPower" color="#67c23a"><CircleCheck /></el-icon><el-icon v-else color="#909399"><CircleClose /></el-icon></span>
                </div>
                <div class="feature-item">
                  <el-icon><Service /></el-icon>
                  <span>客服支持：{{ plan.support }}</span>
                </div>
              </div>
              
              <div class="plan-description">
                {{ plan.description }}
              </div>
              
              <div class="plan-action">
                <el-button 
                  :type="plan.type === currentPlan.type ? 'info' : plan.recommended ? 'danger' : 'primary'"
                  size="large"
                  :disabled="plan.type === currentPlan.type"
                  @click="handleSubscribe(plan)"
                  style="width: 100%;"
                >
                  {{ plan.type === currentPlan.type ? '当前套餐' : '立即订阅' }}
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 功能对比表 -->
    <el-card class="feature-compare-card">
      <template #header>
        <div class="card-header">
          <span>功能详细对比</span>
        </div>
      </template>
      
      <el-table :data="featureCompareData" stripe border style="width: 100%">
        <el-table-column prop="feature" label="功能项" min-width="200" fixed="left">
          <template #default="{ row }">
            <div class="feature-name">
              <el-icon v-if="row.important" color="#f56c6c"><StarFilled /></el-icon>
              <span>{{ row.feature }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column 
          v-for="plan in planList" 
          :key="plan.id"
          :label="plan.name" 
          min-width="120"
          align="center"
        >
          <template #default="{ row }">
            <template v-if="row[plan.type] === true">
              <el-icon color="#67c23a" :size="20"><CircleCheckFilled /></el-icon>
            </template>
            <template v-else-if="row[plan.type] === false">
              <el-icon color="#909399" :size="20"><CircleClose /></el-icon>
            </template>
            <template v-else>
              <span :class="{ 'highlight': row.highlight }">{{ row[plan.type] }}</span>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 定制版订阅对话框 -->
    <el-dialog v-model="customSubscribeDialogVisible" title="订阅定制版" width="500px">
      <div class="subscribe-info">
        <div class="info-row">
          <span class="label">套餐名称：</span>
          <span class="value">定制版</span>
        </div>
        <div class="info-row">
          <span class="label">店铺数量：</span>
          <el-input-number 
            v-model="customSubscribeForm.shopCount" 
            :min="ultimatePlanMaxShops + 1" 
            :max="9999"
            @change="updateCustomPrice"
          />
          <span class="unit">个</span>
        </div>
        <div class="info-row">
          <span class="label">价格计算：</span>
          <div class="value">
            <div>旗舰版基础：¥{{ ultimatePlanPrice }}</div>
            <div v-if="customSubscribeForm.shopCount > ultimatePlanMaxShops">
              超出 {{ customSubscribeForm.shopCount - ultimatePlanMaxShops }} 个店铺 × ¥{{ licenseUnitPrice }} = ¥{{ ((customSubscribeForm.shopCount - ultimatePlanMaxShops) * licenseUnitPrice).toFixed(2) }}
            </div>
          </div>
        </div>
        <div class="info-row total">
          <span class="label">应付金额：</span>
          <span class="value price">¥{{ (ultimatePlanPrice + (customSubscribeForm.shopCount > ultimatePlanMaxShops ? (customSubscribeForm.shopCount - ultimatePlanMaxShops) * licenseUnitPrice : 0)).toFixed(2) }}/年</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="customSubscribeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCustomSubscribe">确认订阅</el-button>
      </template>
    </el-dialog>

    <!-- 订阅确认对话框 -->
    <el-dialog v-model="subscribeDialogVisible" :title="`订阅${selectedPlan?.name}`" width="500px">
      <div class="subscribe-info">
        <div class="info-row">
          <span class="label">套餐名称：</span>
          <span class="value">{{ selectedPlan?.name }}</span>
        </div>
        <div class="info-row">
          <span class="label">计费周期：</span>
          <el-radio-group v-model="subscribeForm.cycle" size="small">
            <el-radio-button label="monthly">月付 ¥{{ selectedPlan?.monthlyPrice }}/月</el-radio-button>
            <el-radio-button label="yearly">年付 ¥{{ selectedPlan?.yearlyPrice }}/年</el-radio-button>
          </el-radio-group>
        </div>
        <div class="info-row">
          <span class="label">购买时长：</span>
          <el-input-number v-model="subscribeForm.duration" :min="1" :max="12" />
          <span class="unit">{{ subscribeForm.cycle === 'yearly' ? '年' : '个月' }}</span>
        </div>
        <div class="info-row total">
          <span class="label">应付金额：</span>
          <span class="value price">¥{{ calculateTotal() }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="subscribeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSubscribe">确认支付</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'

// 旗舰版配置（用于定制版价格计算）
const ultimatePlanPrice = ref(2999)  // 旗舰版价格
const ultimatePlanMaxShops = ref(50)  // 旗舰版最高店铺数量
const licenseUnitPrice = ref(19.9)   // 授权码单价（元/个/年）
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, Top, Warning, Shop, Key, User, ChatDotRound, Collection, Tickets, TrendCharts, Box, Lightning, Service, StarFilled, CircleCheckFilled, CircleClose, CircleCheck 
} from '@element-plus/icons-vue'

interface Plan {
  id: string
  name: string
  type: string
  monthlyPrice: number
  yearlyPrice: number
  maxShops: number
  licenseCount: number
  maxStaff: number
  support: string
  inbox: boolean
  knowledge: boolean
  tickets: boolean
  performance: boolean
  orders: boolean
  aiPower: boolean
  description: string
  recommended?: boolean
}

// 当前套餐 - 与超管后台套餐设置一致
const currentPlan = reactive({
  name: '标准版',
  type: 'standard',
  tagType: 'success',
  expireDate: '2026-12-31',
  shopCount: 2,
  maxShops: 3,
  staffCount: 5,
  maxStaff: 10,
  support: '在线客服'
})

// 是否过期
const isExpired = computed(() => {
  return new Date(currentPlan.expireDate) < new Date()
})

// 是否即将过期（30天内）
const isNearExpire = computed(() => {
  const expire = new Date(currentPlan.expireDate)
  const now = new Date()
  const diff = expire.getTime() - now.getTime()
  const days = diff / (1000 * 60 * 60 * 24)
  return days > 0 && days <= 30
})

// 计费周期
const billingCycle = ref('yearly')

// 定制版店铺数量输入
const customShopCount = ref(51)

// 计算定制版价格
const calculatedCustomPrice = computed(() => {
  if (customShopCount.value <= ultimatePlanMaxShops.value) {
    return ultimatePlanPrice.value
  }
  const extraShops = customShopCount.value - ultimatePlanMaxShops.value
  return ultimatePlanPrice.value + (extraShops * licenseUnitPrice.value)
})

const calculateCustomPrice = () => {
  // 价格自动计算，此方法用于触发更新
}

// 套餐列表 - 与超管后台套餐设置完全一致
// 定制版：店铺数超过旗舰版(50个)后，按需订购授权码，价格=旗舰版价格+19.9元/个/年
const planList = ref<Plan[]>([
  {
    id: 'P001',
    name: '免费版',
    type: 'free',
    monthlyPrice: 0,
    yearlyPrice: 0,
    maxShops: 1,
    licenseCount: 1,
    maxStaff: 2,
    support: '在线文档',
    inbox: true,
    knowledge: false,
    tickets: false,
    performance: false,
    orders: false,
    aiPower: false,
    description: '适合个人创业者，体验基础功能'
  },
  {
    id: 'P002',
    name: '普通版',
    type: 'basic',
    monthlyPrice: 29,
    yearlyPrice: 299,
    maxShops: 1,
    licenseCount: 1,
    maxStaff: 5,
    support: '工单支持',
    inbox: true,
    knowledge: true,
    tickets: true,
    performance: false,
    orders: true,
    aiPower: false,
    description: '适合小型商家，满足日常经营需求'
  },
  {
    id: 'P003',
    name: '标准版',
    type: 'standard',
    monthlyPrice: 59,
    yearlyPrice: 599,
    maxShops: 3,
    licenseCount: 3,
    maxStaff: 10,
    support: '在线客服',
    inbox: true,
    knowledge: true,
    tickets: true,
    performance: true,
    orders: true,
    aiPower: true,
    description: '适合成长型商家',
    recommended: true
  },
  {
    id: 'P004',
    name: '高级版',
    type: 'premium',
    monthlyPrice: 129,
    yearlyPrice: 1299,
    maxShops: 10,
    licenseCount: 10,
    maxStaff: 30,
    support: '专属客服',
    inbox: true,
    knowledge: true,
    tickets: true,
    performance: true,
    orders: true,
    aiPower: true,
    description: '适合中大型商家'
  },
  {
    id: 'P005',
    name: '旗舰版',
    type: 'ultimate',
    monthlyPrice: 299,
    yearlyPrice: 2999,
    maxShops: 50,
    licenseCount: 50,
    maxStaff: 100,
    support: '7x24小时',
    inbox: true,
    knowledge: true,
    tickets: true,
    performance: true,
    orders: true,
    aiPower: true,
    description: '适合大型连锁企业'
  },
  {
    id: 'P006',
    name: '定制版',
    type: 'custom',
    monthlyPrice: 0,
    yearlyPrice: 0,
    maxShops: 9999,
    licenseCount: 9999,
    maxStaff: 999,
    support: '7x24小时',
    inbox: true,
    knowledge: true,
    tickets: true,
    performance: true,
    orders: true,
    aiPower: true,
    description: '专属定制方案，旗舰版基础上店铺超过50个后按19.9元/个/年收取授权码费用'
  }
])

// 功能对比数据 - 与超管后台一致
const featureCompareData = [
  { feature: '店铺数量', free: '1个', basic: '1个', standard: '3个', premium: '10个', ultimate: '50个', custom: '不限', important: true, highlight: true },
  { feature: '授权码数量', free: '1个', basic: '1个', standard: '3个', premium: '10个', ultimate: '50个', custom: '按需', important: true, highlight: true },
  { feature: '员工账号', free: '2个', basic: '5个', standard: '10个', premium: '30个', ultimate: '100个', custom: '不限', important: true, highlight: true },
  { feature: '消息中心', free: true, basic: true, standard: true, premium: true, ultimate: true, custom: true, important: false },
  { feature: '知识库', free: false, basic: true, standard: true, premium: true, ultimate: true, custom: true, important: false },
  { feature: '工单流转', free: false, basic: true, standard: true, premium: true, ultimate: true, custom: true, important: false },
  { feature: '绩效管理', free: false, basic: false, standard: true, premium: true, ultimate: true, custom: true, important: false },
  { feature: '订单管理', free: false, basic: true, standard: true, premium: true, ultimate: true, custom: true, important: false },
  { feature: 'AI算力中心', free: false, basic: false, standard: true, premium: true, ultimate: true, custom: true, important: false },
  { feature: '客服支持', free: '在线文档', basic: '工单支持', standard: '在线客服', premium: '专属客服', ultimate: '7x24小时', custom: '7x24小时', important: false }
]

// 订阅对话框
const subscribeDialogVisible = ref(false)
const selectedPlan = ref<Plan | null>(null)

const subscribeForm = reactive({
  cycle: 'yearly',
  duration: 1
})

// 定制版订阅对话框
const customSubscribeDialogVisible = ref(false)
const customSubscribeForm = reactive({
  shopCount: 51,
  price: 0
})

const calculateTotal = () => {
  if (!selectedPlan.value) return 0
  const price = subscribeForm.cycle === 'yearly' ? selectedPlan.value.yearlyPrice : selectedPlan.value.monthlyPrice
  return price * subscribeForm.duration
}

const handleRenew = () => {
  const plan = planList.value.find(p => p.type === currentPlan.type)
  if (plan) {
    selectedPlan.value = plan
    subscribeForm.cycle = 'yearly'
    subscribeForm.duration = 1
    subscribeDialogVisible.value = true
  }
}

const handleUpgrade = () => {
  ElMessage.info('请选择下方套餐进行升级')
  document.querySelector('.plan-compare-card')?.scrollIntoView({ behavior: 'smooth' })
}

const handleSubscribe = (plan: Plan) => {
  if (plan.type === 'custom') {
    // 定制版：打开定制版订阅对话框
    selectedPlan.value = plan
    customSubscribeForm.shopCount = customShopCount.value
    customSubscribeForm.price = calculatedCustomPrice.value
    customSubscribeDialogVisible.value = true
    return
  }
  selectedPlan.value = plan
  subscribeForm.cycle = 'yearly'
  subscribeForm.duration = 1
  subscribeDialogVisible.value = true
}

const confirmSubscribe = () => {
  ElMessage.success('订阅成功！')
  subscribeDialogVisible.value = false
}

const updateCustomPrice = () => {
  // 价格自动更新
}

const confirmCustomSubscribe = () => {
  ElMessage.success('定制版订阅申请已提交，客服将尽快与您联系！')
  customSubscribeDialogVisible.value = false
}
</script>

<style scoped>
.plan-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.current-plan-card {
  margin-bottom: 24px;
}

.current-plan-info {
  padding: 20px 0;
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

.info-value .expired {
  color: #f56c6c;
}

.info-value .warning {
  color: #e6a23c;
}

.plan-actions {
  margin-top: 24px;
  text-align: center;
}

.plan-compare-card {
  margin-bottom: 24px;
}

.plan-list {
  padding: 20px 0;
}

.plan-item {
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  transition: all 0.3s;
  background: #fff;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.plan-item:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px);
}

.plan-item.current {
  border-color: #67c23a;
  background: #f0f9ff;
}

.plan-item.recommended {
  border-color: #f56c6c;
  position: relative;
}

.plan-item.recommended::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #f56c6c, #ff9d9d);
  border-radius: 12px 12px 0 0;
}

.plan-header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.plan-header h4 {
  margin: 0;
  font-size: 18px;
}

.plan-price {
  margin-bottom: 8px;
}

.price-symbol {
  font-size: 20px;
  color: #f56c6c;
}

.price-value {
  font-size: 36px;
  font-weight: bold;
  color: #f56c6c;
}

.price-unit {
  font-size: 14px;
  color: #909399;
}

.plan-original-price {
  margin-bottom: 16px;
  font-size: 13px;
  color: #909399;
}

.plan-original-price span {
  text-decoration: line-through;
  margin-right: 8px;
}

.plan-features {
  flex: 1;
  text-align: left;
  margin-bottom: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 13px;
  color: #606266;
  border-bottom: 1px dashed #ebeef5;
}

.feature-item:last-child {
  border-bottom: none;
}

.feature-item .el-icon {
  color: #409eff;
}

.plan-description {
  font-size: 12px;
  color: #909399;
  margin-bottom: 16px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.plan-action {
  margin-top: auto;
}

.feature-compare-card {
  margin-bottom: 24px;
}

.feature-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.feature-name .el-icon {
  font-size: 16px;
}

.highlight {
  color: #409eff;
  font-weight: 600;
}

.custom-price {
  margin-bottom: 8px;
}

.price-custom {
  font-size: 18px;
  color: #409eff;
  font-weight: 500;
}

.custom-price-section {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
}

.custom-price-base {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #dcdfe6;
}

.custom-price-input {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
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
  background: #fff;
  border-radius: 6px;
  padding: 12px;
  margin-top: 8px;
}

.price-calc-detail {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #e4e7ed;
}

.price-calc-total {
  text-align: center;
}

.price-calc-total .price-symbol {
  font-size: 16px;
}

.price-calc-total .price-value {
  font-size: 28px;
}

.price-calc-total .price-unit {
  font-size: 13px;
}

.subscribe-info {
  padding: 20px;
}

.subscribe-info .info-row {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.subscribe-info .info-row .label {
  width: 100px;
  color: #606266;
}

.subscribe-info .info-row .value {
  flex: 1;
  color: #303133;
}

.subscribe-info .info-row .value.price {
  font-size: 24px;
  font-weight: bold;
  color: #f56c6c;
}

.subscribe-info .info-row.total {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.subscribe-info .unit {
  margin-left: 8px;
  color: #606266;
}
</style>
