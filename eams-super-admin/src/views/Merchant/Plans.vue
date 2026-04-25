<template>
  <div class="page-container">
    <h3>套餐设置</h3>
    <p>配置商户订阅套餐，设置完成后商户可在商家后台查看并订阅</p>
    
    <!-- 套餐列表 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <div>
            <span>套餐列表</span>
            <el-tag type="info" style="margin-left: 10px;">商户可见</el-tag>
          </div>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 添加套餐
          </el-button>
        </div>
      </template>
      
      <el-alert
        title="套餐说明"
        :description="`以下套餐将展示在商家管理后台，商户可根据需求选择订阅。定制版：店铺数量超过旗舰版(${ultimatePlanMaxShops}个)后，价格=旗舰版价格(¥${ultimatePlanPrice})+(店铺数量-${ultimatePlanMaxShops})×授权码单价(¥${licenseUnitPrice})`"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      />
      
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="(plan, index) in planList" :key="plan.id">
          <el-card class="plan-card" :class="{ 'custom-plan': plan.type === 'custom' }">
            <template #header>
              <div class="plan-header">
                <div class="plan-title">
                  <el-tag :type="getPlanTagType(plan.type)" size="small">{{ plan.level }}</el-tag>
                  <h4>{{ plan.name }}</h4>
                </div>
                <div class="plan-actions">
                  <el-button link type="primary" @click="handleEdit(plan, index)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button link type="danger" @click="handleDelete(index)" v-if="!plan.isDefault">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </template>
            
            <div class="plan-body">
              <div class="plan-price" :class="{ 'custom-price': plan.type === 'custom' }">
                <template v-if="plan.type === 'custom'">
                  <div class="custom-price-section">
                    <div class="custom-price-label">旗舰版基础 ¥{{ ultimatePlanPrice }}/年</div>
                    <div class="custom-price-formula">
                      <div class="formula-row">
                        <span>店铺数量：</span>
                        <el-input-number 
                          v-model="customShopCount" 
                          :min="ultimatePlanMaxShops + 1" 
                          :max="9999" 
                          size="small"
                          style="width: 120px"
                          @change="calculateCustomPrice"
                        />
                        <span class="formula-hint">个（最少{{ ultimatePlanMaxShops + 1 }}个）</span>
                      </div>
                      <div class="formula-result" v-if="customShopCount > ultimatePlanMaxShops">
                        <div class="formula-detail">
                          超出 {{ customShopCount - ultimatePlanMaxShops }} 个店铺
                          × ¥{{ licenseUnitPrice }}/个
                        </div>
                        <div class="formula-total">
                          <span class="price-symbol">¥</span>
                          <span class="price-value">{{ calculatedCustomPrice }}</span>
                          <span class="price-unit">/年</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <span class="price-symbol">¥</span>
                  <span class="price-value">{{ plan.price }}</span>
                  <span class="price-unit">/{{ plan.duration }}个月</span>
                </template>
              </div>
              
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
                  <el-icon><ChatDotRound /></el-icon>
                  <span>消息中心：<strong>{{ plan.inbox ? '支持' : '不支持' }}</strong></span>
                </div>
                <div class="feature-item">
                  <el-icon><Collection /></el-icon>
                  <span>知识库：<strong>{{ plan.knowledge ? '支持' : '不支持' }}</strong></span>
                </div>
                <div class="feature-item">
                  <el-icon><Tickets /></el-icon>
                  <span>工单流转：<strong>{{ plan.tickets ? '支持' : '不支持' }}</strong></span>
                </div>
                <div class="feature-item">
                  <el-icon><TrendCharts /></el-icon>
                  <span>绩效管理：<strong>{{ plan.performance ? '支持' : '不支持' }}</strong></span>
                </div>
                <div class="feature-item">
                  <el-icon><Box /></el-icon>
                  <span>订单管理：<strong>{{ plan.orders ? '支持' : '不支持' }}</strong></span>
                </div>
                <div class="feature-item">
                  <el-icon><Lightning /></el-icon>
                  <span>AI算力中心：<strong>{{ plan.aiPower ? '支持' : '不支持' }}</strong></span>
                </div>
                <div class="feature-item">
                  <el-icon><Service /></el-icon>
                  <span>客服支持：<strong>{{ plan.support }}</strong></span>
                </div>
              </div>
              
              <div class="plan-description">
                <p>{{ plan.description }}</p>
              </div>
              
              <div class="plan-status">
                <el-switch
                  v-model="plan.isActive"
                  active-text="上架"
                  inactive-text="下架"
                  @change="(val: boolean) => handleStatusChange(plan, val)"
                />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 套餐对比表 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>套餐功能对比</span>
      </template>
      
      <el-table :data="planList" stripe border>
        <el-table-column prop="name" label="套餐名称" min-width="120" fixed="left" />
        <el-table-column prop="price" label="价格" min-width="120">
          <template #default="{ row }">
            <template v-if="row.type === 'custom'">
              <div class="custom-table-price">
                <div>旗舰版 ¥{{ ultimatePlanPrice }}</div>
                <div class="custom-table-formula">+ 超出数量 × ¥{{ licenseUnitPrice }}</div>
              </div>
            </template>
            <template v-else>
              <span class="price-highlight">¥{{ row.price }}</span>
            </template>
          </template>
        </el-table-column>
        <el-table-column prop="maxShops" label="店铺数量" min-width="100" align="center" />
        <el-table-column prop="licenseCount" label="授权码数量" min-width="100" align="center" />
        <el-table-column prop="duration" label="时长(月)" min-width="100" align="center" />
        <el-table-column prop="maxStaff" label="员工账号" min-width="100" align="center" />
        <el-table-column prop="inbox" label="消息中心" min-width="100" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.inbox" color="#67c23a"><CircleCheck /></el-icon>
            <el-icon v-else color="#909399"><CircleClose /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="knowledge" label="知识库" min-width="100" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.knowledge" color="#67c23a"><CircleCheck /></el-icon>
            <el-icon v-else color="#909399"><CircleClose /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="tickets" label="工单流转" min-width="100" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.tickets" color="#67c23a"><CircleCheck /></el-icon>
            <el-icon v-else color="#909399"><CircleClose /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="performance" label="绩效管理" min-width="100" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.performance" color="#67c23a"><CircleCheck /></el-icon>
            <el-icon v-else color="#909399"><CircleClose /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="orders" label="订单管理" min-width="100" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.orders" color="#67c23a"><CircleCheck /></el-icon>
            <el-icon v-else color="#909399"><CircleClose /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="aiPower" label="AI算力" min-width="100" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.aiPower" color="#67c23a"><CircleCheck /></el-icon>
            <el-icon v-else color="#909399"><CircleClose /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="isActive" label="状态" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.isActive ? 'success' : 'info'">{{ row.isActive ? '上架' : '下架' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑套餐对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑套餐' : '添加套餐'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="140px">
        <el-form-item label="套餐名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入套餐名称" />
        </el-form-item>
        <el-form-item label="套餐等级" prop="level">
          <el-select v-model="form.level" style="width: 100%" placeholder="选择套餐等级">
            <el-option label="Level 1 - 入门级" value="L1" />
            <el-option label="Level 2 - 基础级" value="L2" />
            <el-option label="Level 3 - 进阶级" value="L3" />
            <el-option label="Level 4 - 专业级" value="L4" />
            <el-option label="Level 5 - 企业级" value="L5" />
            <el-option label="Level 6 - 定制级" value="L6" />
          </el-select>
        </el-form-item>
        <el-form-item label="套餐类型" prop="type">
          <el-select v-model="form.type" style="width: 100%" placeholder="选择套餐类型">
            <el-option label="免费版" value="free" />
            <el-option label="普通版" value="basic" />
            <el-option label="标准版" value="standard" />
            <el-option label="高级版" value="premium" />
            <el-option label="旗舰版" value="ultimate" />
            <el-option label="定制版" value="custom" />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="价格(元)" prop="price">
              <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="时长(月)" prop="duration">
              <el-input-number v-model="form.duration" :min="1" :max="120" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="店铺数量" prop="maxShops">
              <el-input-number v-model="form.maxShops" :min="1" :max="9999" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="授权码数量" prop="licenseCount">
              <el-input-number v-model="form.licenseCount" :min="1" :max="9999" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="员工账号" prop="maxStaff">
              <el-input-number v-model="form.maxStaff" :min="1" :max="999" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="客服支持" prop="support">
          <el-select v-model="form.support" style="width: 100%">
            <el-option label="在线文档" value="在线文档" />
            <el-option label="工单支持" value="工单支持" />
            <el-option label="在线客服" value="在线客服" />
            <el-option label="专属客服" value="专属客服" />
            <el-option label="7x24小时" value="7x24小时" />
          </el-select>
        </el-form-item>
        <el-form-item label="功能权限">
          <el-checkbox-group v-model="form.features">
            <el-checkbox label="inbox">消息中心</el-checkbox>
            <el-checkbox label="knowledge">知识库</el-checkbox>
            <el-checkbox label="tickets">工单流转</el-checkbox>
            <el-checkbox label="performance">绩效管理</el-checkbox>
            <el-checkbox label="orders">订单管理</el-checkbox>
            <el-checkbox label="aiPower">AI算力中心</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="套餐说明" prop="description">
          <el-input v-model="form.description" type="textarea" rows="3" placeholder="请输入套餐说明，将展示给商户查看" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Shop, Key, Calendar, User, ChatDotRound, Collection, Tickets, TrendCharts, Box, Lightning, Service, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

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
  inbox: boolean
  knowledge: boolean
  tickets: boolean
  performance: boolean
  orders: boolean
  aiPower: boolean
  description: string
  isActive: boolean
  isDefault?: boolean
}

// 默认六个等级套餐 - 功能权限与商家后台匹配
// 定制版：店铺数超过旗舰版后，按需订购授权码，价格=旗舰版价格+授权码单价×超出数量

// 旗舰版配置（用于定制版价格计算）
const ultimatePlanPrice = ref(2999)  // 旗舰版价格
const ultimatePlanMaxShops = ref(50)  // 旗舰版最高店铺数量
const licenseUnitPrice = ref(19.9)   // 授权码单价（元/个/年）

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
    inbox: true,
    knowledge: false,
    tickets: false,
    performance: false,
    orders: false,
    aiPower: false,
    description: '适合个人创业者，体验基础功能',
    isActive: true,
    isDefault: true
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
    inbox: true,
    knowledge: true,
    tickets: true,
    performance: false,
    orders: true,
    aiPower: false,
    description: '适合小型商家，满足日常经营需求',
    isActive: true,
    isDefault: true
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
    inbox: true,
    knowledge: true,
    tickets: true,
    performance: true,
    orders: true,
    aiPower: true,
    description: '适合成长型商家，支持多店铺管理',
    isActive: true,
    isDefault: true
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
    inbox: true,
    knowledge: true,
    tickets: true,
    performance: true,
    orders: true,
    aiPower: true,
    description: '适合中大型商家，功能全面支持',
    isActive: true,
    isDefault: true
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
    inbox: true,
    knowledge: true,
    tickets: true,
    performance: true,
    orders: true,
    aiPower: true,
    description: '适合大型连锁企业，无限制扩展',
    isActive: true,
    isDefault: true
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
    inbox: true,
    knowledge: true,
    tickets: true,
    performance: true,
    orders: true,
    aiPower: true,
    description: `专属定制方案，旗舰版基础上店铺超过${ultimatePlanMaxShops.value}个后按¥${licenseUnitPrice.value}/个/年收取授权码费用`,
    isActive: true,
    isDefault: true
  }
])

const dialogVisible = ref(false)
const isEdit = ref(false)
const editIndex = ref(-1)
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  level: 'L2',
  type: 'basic',
  price: 299,
  duration: 12,
  maxShops: 1,
  licenseCount: 1,
  maxStaff: 5,
  support: '工单支持',
  features: [] as string[],
  description: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入套餐名称', trigger: 'blur' }],
  level: [{ required: true, message: '请选择套餐等级', trigger: 'change' }],
  type: [{ required: true, message: '请选择套餐类型', trigger: 'change' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  duration: [{ required: true, message: '请输入时长', trigger: 'blur' }],
  maxShops: [{ required: true, message: '请输入店铺数量', trigger: 'blur' }],
  licenseCount: [{ required: true, message: '请输入授权码数量', trigger: 'blur' }],
  maxStaff: [{ required: true, message: '请输入员工账号数', trigger: 'blur' }],
  description: [{ required: true, message: '请输入套餐说明', trigger: 'blur' }]
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

const handleAdd = () => {
  isEdit.value = false
  editIndex.value = -1
  form.name = ''
  form.level = 'L2'
  form.type = 'basic'
  form.price = 299
  form.duration = 12
  form.maxShops = 1
  form.licenseCount = 1
  form.maxStaff = 5
  form.support = '工单支持'
  form.features = []
  form.description = ''
  dialogVisible.value = true
}

const handleEdit = (row: Plan, index: number) => {
  isEdit.value = true
  editIndex.value = index
  form.name = row.name
  form.level = row.level
  form.type = row.type
  form.price = row.price
  form.duration = row.duration
  form.maxShops = row.maxShops
  form.licenseCount = row.licenseCount
  form.maxStaff = row.maxStaff
  form.support = row.support
  form.features = []
  if (row.inbox) form.features.push('inbox')
  if (row.knowledge) form.features.push('knowledge')
  if (row.tickets) form.features.push('tickets')
  if (row.performance) form.features.push('performance')
  if (row.orders) form.features.push('orders')
  if (row.aiPower) form.features.push('aiPower')
  form.description = row.description
  dialogVisible.value = true
}

const handleDelete = (index: number) => {
  ElMessageBox.confirm('确定要删除该套餐吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    planList.value.splice(index, 1)
    ElMessage.success('删除成功')
  })
}

const handleStatusChange = (plan: Plan, val: boolean) => {
  ElMessage.success(`${plan.name}已${val ? '上架' : '下架'}`)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (valid) {
      const planData: Plan = {
        id: isEdit.value ? planList.value[editIndex.value].id : 'P' + Date.now(),
        name: form.name,
        level: form.level,
        type: form.type,
        price: form.price,
        duration: form.duration,
        maxShops: form.maxShops,
        licenseCount: form.licenseCount,
        maxStaff: form.maxStaff,
        support: form.support,
        inbox: form.features.includes('inbox'),
        knowledge: form.features.includes('knowledge'),
        tickets: form.features.includes('tickets'),
        performance: form.features.includes('performance'),
        orders: form.features.includes('orders'),
        aiPower: form.features.includes('aiPower'),
        description: form.description,
        isActive: true
      }
      
      if (isEdit.value && editIndex.value >= 0) {
        planList.value[editIndex.value] = planData
        ElMessage.success('编辑成功')
      } else {
        planList.value.push(planData)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
    }
  })
}
</script>

<style scoped>
.page-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.plan-actions {
  display: flex;
  gap: 5px;
}

.plan-body {
  padding: 10px 0;
}

.plan-price {
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
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

.plan-features {
  margin-bottom: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px dashed #ebeef5;
}

.feature-item:last-child {
  border-bottom: none;
}

.feature-item .el-icon {
  color: #409eff;
  font-size: 18px;
}

.plan-description {
  margin-bottom: 15px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.plan-description p {
  margin: 0;
  font-size: 13px;
  color: #606266;
}

.plan-status {
  text-align: center;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.price-highlight {
  font-weight: bold;
  color: #f56c6c;
}

.custom-price {
  text-align: center;
}

.price-custom {
  font-size: 20px;
  color: #409eff;
  font-weight: 500;
}

.custom-price-section {
  padding: 10px;
}

.custom-price-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #dcdfe6;
}

.custom-price-formula {
  text-align: left;
}

.formula-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.formula-row span {
  font-size: 14px;
  color: #606266;
}

.formula-hint {
  font-size: 12px;
  color: #909399;
}

.formula-result {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  margin-top: 10px;
}

.formula-detail {
  font-size: 13px;
  color: #606266;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #dcdfe6;
}

.formula-total {
  text-align: center;
}

.formula-total .price-symbol {
  font-size: 18px;
}

.formula-total .price-value {
  font-size: 32px;
}

.formula-total .price-unit {
  font-size: 14px;
  color: #909399;
}

.custom-table-price {
  font-size: 13px;
}

.custom-table-formula {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
