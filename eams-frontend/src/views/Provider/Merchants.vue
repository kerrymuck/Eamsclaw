<template>
  <div class="merchant-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>🏪 商户管理</h2>
        <p class="subtitle">管理您的合作商户，查看详细信息</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加商户
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon blue">🏪</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">总商户数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon green">✅</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.active }}</div>
            <div class="stat-label">正常运营</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon orange">⏰</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.expiring }}</div>
            <div class="stat-label">即将到期</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon red">⚠️</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.expired }}</div>
            <div class="stat-label">已到期</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="商户名称">
          <el-input v-model="filterForm.name" placeholder="请输入商户名称" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="正常" value="active" />
            <el-option label="已停用" value="inactive" />
            <el-option label="已到期" value="expired" />
          </el-select>
        </el-form-item>
        <el-form-item label="套餐类型">
          <el-select v-model="filterForm.planType" placeholder="全部套餐" clearable style="width: 130px">
            <el-option label="免费版" value="free" />
            <el-option label="普通版" value="basic" />
            <el-option label="标准版" value="standard" />
            <el-option label="高级版" value="premium" />
            <el-option label="旗舰版" value="ultimate" />
            <el-option label="定制版" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间周期">
          <el-select v-model="filterForm.timeRange" placeholder="全部时间" clearable @change="handleTimeRangeChange" style="width: 130px">
            <el-option label="当天" value="today" />
            <el-option label="本月" value="thisMonth" />
            <el-option label="近30天" value="last30Days" />
            <el-option label="近90天" value="last90Days" />
            <el-option label="近半年" value="last6Months" />
            <el-option label="近一年" value="last1Year" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="filterForm.timeRange === 'custom'" label="自定义时间">
          <el-date-picker
            v-model="filterForm.customDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="到期时间">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 220px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 商户列表 -->
    <el-card class="list-card">
      <el-table :data="merchantList" v-loading="loading" stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column label="商户信息" min-width="250">
          <template #default="{ row }">
            <div class="merchant-info">
              <el-avatar :size="48" :src="row.logo">{{ row.name.charAt(0) }}</el-avatar>
              <div class="merchant-detail">
                <div class="name">{{ row.name }}</div>
                <div class="contact">
                  <span>{{ row.contactName }}</span>
                  <el-divider direction="vertical" />
                  <span>{{ row.contactPhone }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="套餐信息" width="200">
          <template #default="{ row }">
            <div class="package-info">
              <el-tag :type="getPlanTagType(row.planType)" size="small">{{ row.packageName }}</el-tag>
              <div class="package-detail">
                <span>{{ row.maxShops }}店铺/{{ row.licenseCount }}授权</span>
              </div>
              <div class="package-price" v-if="row.planType !== 'free'">
                ¥{{ row.yearlyPrice }}/年
              </div>
              <div class="package-price free" v-else>免费</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="使用情况" width="150">
          <template #default="{ row }">
            <div class="usage-info">
              <div>店铺: {{ row.shopCount }} 家</div>
              <div>员工: {{ row.staffCount }} 人</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="expireDate" label="到期时间" width="120">
          <template #default="{ row }">
            <el-tag :type="getExpireTagType(row.expireDate)">
              {{ row.expireDate }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : row.status === 'expired' ? 'danger' : 'info'">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button link type="primary" @click="editMerchant(row)">编辑</el-button>
            <el-dropdown>
              <el-button link type="primary">
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="renewMerchant(row)">续费</el-dropdown-item>
                  <el-dropdown-item @click="upgradePackage(row)">升级套餐</el-dropdown-item>
                  <el-dropdown-item divided @click="toggleStatus(row)">
                    {{ row.status === 'active' ? '停用' : '启用' }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pageInfo.page"
          v-model:page-size="pageInfo.pageSize"
          :total="pageInfo.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>

    <!-- 添加/编辑商户弹窗 -->
    <el-dialog
      v-model="showAddDialog"
      :title="isEdit ? '编辑商户' : '添加商户'"
      width="700px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商户名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入商户名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系人" prop="contactName">
              <el-input v-model="form.contactName" placeholder="请输入联系人" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系电话" prop="contactPhone">
              <el-input v-model="form.contactPhone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="选择套餐" prop="packageId">
              <el-select v-model="form.packageId" placeholder="请选择套餐" style="width: 100%">
                <el-option
                  v-for="pkg in packages"
                  :key="pkg.id"
                  :label="pkg.name + ' - ¥' + pkg.price + '/月'"
                  :value="pkg.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="到期时间" prop="expireDate">
              <el-date-picker
                v-model="form.expireDate"
                type="date"
                placeholder="选择到期时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="可选填" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveMerchant" :loading="saving">
          {{ isEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 商户详情抽屉 -->
    <el-drawer
      v-model="showDetailDrawer"
      title="商户详情"
      size="600px"
    >
      <div v-if="currentMerchant" class="merchant-detail-panel">
        <div class="detail-header">
          <el-avatar :size="80" :src="currentMerchant.logo">{{ currentMerchant.name.charAt(0) }}</el-avatar>
          <div class="header-info">
            <h3>{{ currentMerchant.name }}</h3>
            <el-tag :type="currentMerchant.status === 'active' ? 'success' : 'danger'">
              {{ getStatusText(currentMerchant.status) }}
            </el-tag>
          </div>
        </div>
        
        <el-divider />
        
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2">
            <el-descriptions-item label="联系人">{{ currentMerchant.contactName }}</el-descriptions-item>
            <el-descriptions-item label="联系电话">{{ currentMerchant.contactPhone }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ currentMerchant.email }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ currentMerchant.createTime }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="detail-section">
          <h4>套餐信息</h4>
          <el-descriptions :column="2">
            <el-descriptions-item label="当前套餐">{{ currentMerchant.packageName }}</el-descriptions-item>
            <el-descriptions-item label="月费">¥{{ currentMerchant.monthlyFee }}</el-descriptions-item>
            <el-descriptions-item label="到期时间">{{ currentMerchant.expireDate }}</el-descriptions-item>
            <el-descriptions-item label="剩余天数">{{ currentMerchant.remainingDays }} 天</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="detail-section">
          <h4>使用统计</h4>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-box">
                <div class="number">{{ currentMerchant.shopCount }}</div>
                <div class="label">店铺数</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-box">
                <div class="number">{{ currentMerchant.staffCount }}</div>
                <div class="label">员工数</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-box">
                <div class="number">{{ currentMerchant.licenseCount }}</div>
                <div class="label">授权码数</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { Plus, Search, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

// 统计数据
const stats = ref({
  total: 328,
  active: 286,
  expiring: 42,
  expired: 15
})

// 筛选表单
const filterForm = reactive({
  name: '',
  status: '',
  planType: '',
  timeRange: '',
  customDateRange: [] as string[],
  dateRange: []
})

const handleTimeRangeChange = (val: string) => {
  if (val !== 'custom') {
    filterForm.customDateRange = []
  }
}

// 系统套餐列表（与超管后台一致）
const systemPlans = ref([
  { id: 'P001', name: '免费版', type: 'free', price: 0, maxShops: 1, licenseCount: 1 },
  { id: 'P002', name: '普通版', type: 'basic', price: 299, maxShops: 1, licenseCount: 1 },
  { id: 'P003', name: '标准版', type: 'standard', price: 599, maxShops: 3, licenseCount: 3 },
  { id: 'P004', name: '高级版', type: 'premium', price: 1299, maxShops: 10, licenseCount: 10 },
  { id: 'P005', name: '旗舰版', type: 'ultimate', price: 2999, maxShops: 50, licenseCount: 50 },
  { id: 'P006', name: '定制版', type: 'custom', price: 0, maxShops: 9999, licenseCount: 9999 }
])

// 套餐选项（用于下拉选择）
const packages = computed(() => {
  return systemPlans.value.map(plan => ({
    id: plan.id,
    name: plan.name,
    price: plan.price,
    type: plan.type
  }))
})

// 商户列表（套餐信息与系统设置匹配）
const merchantList = ref([
  {
    id: 1,
    name: '龙猫数码旗舰店',
    logo: '',
    contactName: '张三',
    contactPhone: '13800138001',
    email: 'zhangsan@example.com',
    planType: 'premium',
    packageName: '高级版',
    yearlyPrice: 1299,
    maxShops: 10,
    shopCount: 5,
    staffCount: 12,
    licenseCount: 10,
    expireDate: '2026-12-31',
    remainingDays: 265,
    status: 'active',
    createTime: '2024-01-15'
  },
  {
    id: 2,
    name: '潮流服饰专营店',
    logo: '',
    contactName: '李四',
    contactPhone: '13800138002',
    email: 'lisi@example.com',
    planType: 'standard',
    packageName: '标准版',
    yearlyPrice: 599,
    maxShops: 3,
    shopCount: 3,
    staffCount: 8,
    licenseCount: 3,
    expireDate: '2026-11-30',
    remainingDays: 235,
    status: 'active',
    createTime: '2024-02-20'
  },
  {
    id: 3,
    name: '美妆护肤集合店',
    logo: '',
    contactName: '王五',
    contactPhone: '13800138003',
    email: 'wangwu@example.com',
    planType: 'ultimate',
    packageName: '旗舰版',
    yearlyPrice: 2999,
    maxShops: 50,
    shopCount: 12,
    staffCount: 25,
    licenseCount: 50,
    expireDate: '2025-04-15',
    remainingDays: 5,
    status: 'expiring',
    createTime: '2024-03-10'
  },
  {
    id: 4,
    name: '小明个人工作室',
    logo: '',
    contactName: '赵小明',
    contactPhone: '13800138004',
    email: 'zhao@example.com',
    planType: 'free',
    packageName: '免费版',
    yearlyPrice: 0,
    maxShops: 1,
    shopCount: 1,
    staffCount: 2,
    licenseCount: 1,
    expireDate: '2026-06-30',
    remainingDays: 75,
    status: 'active',
    createTime: '2024-04-01'
  },
  {
    id: 5,
    name: '未来科技有限公司',
    logo: '',
    contactName: '钱总',
    contactPhone: '13800138005',
    email: 'qian@example.com',
    planType: 'custom',
    packageName: '定制版',
    yearlyPrice: 5998,
    maxShops: 100,
    shopCount: 68,
    staffCount: 150,
    licenseCount: 100,
    expireDate: '2027-03-31',
    remainingDays: 350,
    status: 'active',
    createTime: '2024-01-10'
  }
])

const loading = ref(false)
const pageInfo = reactive({
  page: 1,
  pageSize: 10,
  total: 328
})

// 弹窗相关
const showAddDialog = ref(false)
const showDetailDrawer = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const currentMerchant = ref<any>(null)
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  contactName: '',
  contactPhone: '',
  email: '',
  packageId: null,
  expireDate: '',
  remark: ''
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入商户名称', trigger: 'blur' }],
  contactName: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  contactPhone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  packageId: [{ required: true, message: '请选择套餐', trigger: 'change' }],
  expireDate: [{ required: true, message: '请选择到期时间', trigger: 'change' }]
}

const handleSearch = () => {
  // 搜索逻辑
}

const resetFilter = () => {
  filterForm.name = ''
  filterForm.status = ''
  filterForm.planType = ''
  filterForm.timeRange = ''
  filterForm.customDateRange = []
  filterForm.dateRange = []
}

const getExpireTagType = (date: string) => {
  const days = getRemainingDays(date)
  if (days <= 0) return 'danger'
  if (days <= 7) return 'warning'
  return 'success'
}

const getRemainingDays = (date: string) => {
  const end = new Date(date)
  const now = new Date()
  return Math.ceil((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    active: '正常',
    inactive: '已停用',
    expired: '已到期',
    expiring: '即将到期'
  }
  return map[status] || status
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

const viewDetail = (row: any) => {
  currentMerchant.value = row
  showDetailDrawer.value = true
}

const editMerchant = (row: any) => {
  isEdit.value = true
  Object.assign(form, row)
  showAddDialog.value = true
}

const renewMerchant = (row: any) => {
  ElMessageBox.prompt('请输入续费月数', '商户续费', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /^[1-9]\d*$/,
    inputErrorMessage: '请输入正确的月数'
  }).then(({ value }) => {
    ElMessage.success(`商户「${row.name}」续费${value}个月成功`)
  })
}

const upgradePackage = (row: any) => {
  ElMessage.info(`升级商户「${row.name}」的套餐`)
}

const toggleStatus = (row: any) => {
  const action = row.status === 'active' ? '停用' : '启用'
  ElMessageBox.confirm(
    `确定要${action}商户「${row.name}」吗？`,
    '确认操作',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(() => {
    row.status = row.status === 'active' ? 'inactive' : 'active'
    ElMessage.success(`商户已${action}`)
  })
}

const saveMerchant = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (!valid) return
    saving.value = true
    setTimeout(() => {
      ElMessage.success(isEdit.value ? '商户信息已更新' : '商户添加成功')
      saving.value = false
      showAddDialog.value = false
    }, 500)
  })
}
</script>

<style scoped>
.merchant-management {
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

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 12px;
}

.stat-icon.blue { background: #e6f7ff; }
.stat-icon.green { background: #f6ffed; }
.stat-icon.orange { background: #fff7e6; }
.stat-icon.red { background: #fff1f0; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.filter-card {
  margin-bottom: 20px;
}

.list-card {
  margin-bottom: 20px;
}

.merchant-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.merchant-detail .name {
  font-weight: 500;
  color: #1a1a2e;
  margin-bottom: 4px;
}

.merchant-detail .contact {
  font-size: 12px;
  color: #909399;
}

.package-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.package-info .package-detail {
  font-size: 12px;
  color: #606266;
}

.package-info .package-price {
  font-size: 13px;
  color: #f56c6c;
  font-weight: 500;
}

.package-info .package-price.free {
  color: #67c23a;
}

.usage-info {
  font-size: 13px;
  color: #666;
  line-height: 1.8;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.merchant-detail-panel .detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.merchant-detail-panel .header-info h3 {
  margin: 0 0 8px 0;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #1a1a2e;
}

.stat-box {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-box .number {
  font-size: 24px;
  font-weight: 700;
  color: #1677ff;
}

.stat-box .label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
