<template>
  <div class="page-container">
    <h3>商户管理</h3>
    <p>管理所有服务商旗下的商户信息</p>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #409eff;">
            <el-icon :size="28"><Shop /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">总商户数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #67c23a;">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.active }}</div>
            <div class="stat-label">正常营业</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #e6a23c;">
            <el-icon :size="28"><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pending }}</div>
            <div class="stat-label">待审核</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #f56c6c;">
            <el-icon :size="28"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.expired }}</div>
            <div class="stat-label">套餐过期</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="商户名称">
          <el-input v-model="searchForm.name" placeholder="请输入商户名称" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="所属服务商">
          <el-select v-model="searchForm.providerId" placeholder="全部服务商" clearable style="width: 150px">
            <el-option label="科技云" value="1" />
            <el-option label="智慧零售" value="2" />
            <el-option label="未来电商" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="套餐类型">
          <el-select v-model="searchForm.planType" placeholder="全部套餐" clearable style="width: 130px">
            <el-option label="免费版" value="free" />
            <el-option label="普通版" value="basic" />
            <el-option label="标准版" value="standard" />
            <el-option label="高级版" value="premium" />
            <el-option label="旗舰版" value="ultimate" />
            <el-option label="定制版" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="正常" value="active" />
            <el-option label="待审核" value="pending" />
            <el-option label="已禁用" value="disabled" />
            <el-option label="套餐过期" value="expired" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间周期">
          <el-select v-model="searchForm.timeRange" placeholder="全部时间" clearable @change="handleTimeRangeChange" style="width: 130px">
            <el-option label="当天" value="today" />
            <el-option label="本月" value="thisMonth" />
            <el-option label="近30天" value="last30Days" />
            <el-option label="近90天" value="last90Days" />
            <el-option label="近半年" value="last6Months" />
            <el-option label="近一年" value="last1Year" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="searchForm.timeRange === 'custom'" label="自定义时间">
          <el-date-picker
            v-model="searchForm.customDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 商户列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>商户列表</span>
          <div>
            <el-button type="success" @click="handleAdd">
              <el-icon><Plus /></el-icon> 添加商户
            </el-button>
            <el-button type="primary" @click="handleExport">
              <el-icon><Download /></el-icon> 导出
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="merchantList" stripe @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="商户名称" min-width="150">
          <template #default="{ row }">
            <div class="merchant-info">
              <el-avatar :size="32" :src="row.logo" v-if="row.logo">
                <Shop />
              </el-avatar>
              <div class="merchant-detail">
                <div class="merchant-name">{{ row.name }}</div>
                <div class="merchant-id">ID: {{ row.id }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="providerName" label="所属服务商" min-width="120" />
        <el-table-column prop="planName" label="当前套餐" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getPlanType(row.planType)">{{ row.planName }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="shopCount" label="店铺数" min-width="80" align="center">
          <template #default="{ row }">
            <span :class="{ 'limit-warning': row.shopCount >= row.maxShops }">
              {{ row.shopCount }}/{{ row.maxShops }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="expireDate" label="套餐到期" min-width="150">
          <template #default="{ row }">
            <div :class="{ 'expired': isExpired(row.expireDate) }">
              {{ row.expireDate }}
              <el-tag v-if="isExpired(row.expireDate)" type="danger" size="small">已过期</el-tag>
              <el-tag v-else-if="isNearExpire(row.expireDate)" type="warning" size="small">即将过期</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="contactName" label="联系人" min-width="120" />
        <el-table-column prop="contactPhone" label="联系电话" min-width="130" />
        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" min-width="150" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleChangePlan(row)">变更套餐</el-button>
            <el-button link :type="row.status === 'disabled' ? 'success' : 'danger'" @click="handleToggle(row)">
              {{ row.status === 'disabled' ? '启用' : '禁用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page.current"
          v-model:page-size="page.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="page.total"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>

    <!-- 添加/编辑商户对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑商户' : '添加商户'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="商户名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入商户名称" />
        </el-form-item>
        <el-form-item label="所属服务商" prop="providerId">
          <el-select v-model="form.providerId" style="width: 100%" placeholder="选择服务商">
            <el-option label="科技云" value="1" />
            <el-option label="智慧零售" value="2" />
            <el-option label="未来电商" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="套餐" prop="planType">
          <el-select v-model="form.planType" style="width: 100%" placeholder="选择套餐">
            <el-option label="免费版" value="free" />
            <el-option label="普通版" value="basic" />
            <el-option label="标准版" value="standard" />
            <el-option label="高级版" value="premium" />
            <el-option label="旗舰版" value="ultimate" />
            <el-option label="定制版" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系人" prop="contactName">
          <el-input v-model="form.contactName" placeholder="请输入联系人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contactPhone">
          <el-input v-model="form.contactPhone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="联系邮箱" prop="contactEmail">
          <el-input v-model="form.contactEmail" placeholder="请输入联系邮箱" />
        </el-form-item>
        <el-form-item label="商户地址" prop="address">
          <el-input v-model="form.address" type="textarea" rows="2" placeholder="请输入商户地址" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" rows="2" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 变更套餐对话框 -->
    <el-dialog v-model="planDialogVisible" title="变更套餐" width="500px">
      <el-form :model="planForm" label-width="120px">
        <el-form-item label="当前商户">
          <span>{{ currentMerchant?.name }}</span>
        </el-form-item>
        <el-form-item label="当前套餐">
          <el-tag :type="getPlanType(currentMerchant?.planType)">{{ currentMerchant?.planName }}</el-tag>
        </el-form-item>
        <el-form-item label="新套餐" prop="newPlanType">
          <el-select v-model="planForm.newPlanType" style="width: 100%" placeholder="选择新套餐">
            <el-option label="免费版" value="free" />
            <el-option label="普通版" value="basic" />
            <el-option label="标准版" value="standard" />
            <el-option label="高级版" value="premium" />
            <el-option label="旗舰版" value="ultimate" />
            <el-option label="定制版" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="套餐时长">
          <el-select v-model="planForm.duration" style="width: 100%">
            <el-option label="1个月" :value="1" />
            <el-option label="3个月" :value="3" />
            <el-option label="6个月" :value="6" />
            <el-option label="1年" :value="12" />
            <el-option label="2年" :value="24" />
            <el-option label="永久" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="变更原因">
          <el-input v-model="planForm.reason" type="textarea" rows="2" placeholder="请输入变更原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePlanSubmit">确认变更</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Shop, CircleCheck, Timer, Warning, Search, Plus, Download } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

interface Merchant {
  id: string
  name: string
  logo?: string
  providerId: string
  providerName: string
  planType: string
  planName: string
  maxShops: number
  shopCount: number
  expireDate: string
  contactName: string
  contactPhone: string
  contactEmail?: string
  address?: string
  status: string
  createTime: string
}

const stats = reactive({
  total: 1258,
  active: 986,
  pending: 45,
  expired: 89
})

const searchForm = reactive({
  name: '',
  providerId: '',
  planType: '',
  status: '',
  timeRange: '',
  customDateRange: [] as string[]
})

const handleTimeRangeChange = (val: string) => {
  if (val !== 'custom') {
    searchForm.customDateRange = []
  }
}

const page = reactive({
  current: 1,
  size: 10,
  total: 100
})

const dialogVisible = ref(false)
const planDialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref('')
const currentMerchant = ref<Merchant | null>(null)
const selectedMerchants = ref<Merchant[]>([])
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  providerId: '',
  planType: 'basic',
  contactName: '',
  contactPhone: '',
  contactEmail: '',
  address: '',
  remark: ''
})

const planForm = reactive({
  newPlanType: '',
  duration: 12,
  reason: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入商户名称', trigger: 'blur' }],
  providerId: [{ required: true, message: '请选择所属服务商', trigger: 'change' }],
  planType: [{ required: true, message: '请选择套餐', trigger: 'change' }],
  contactName: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  contactPhone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
}

const merchantList = ref<Merchant[]>([
  { id: 'M2026001', name: '小明电商旗舰店', providerId: '1', providerName: '科技云', planType: 'premium', planName: '高级版', maxShops: 10, shopCount: 5, expireDate: '2027-03-31 23:59:59', contactName: '张小明', contactPhone: '13800138001', contactEmail: 'zhang@example.com', status: 'active', createTime: '2026-01-15 10:30:00' },
  { id: 'M2026002', name: '智慧零售体验店', providerId: '2', providerName: '智慧零售', planType: 'standard', planName: '标准版', maxShops: 5, shopCount: 3, expireDate: '2026-12-31 23:59:59', contactName: '李小红', contactPhone: '13800138002', contactEmail: 'li@example.com', status: 'active', createTime: '2026-02-20 14:15:00' },
  { id: 'M2026003', name: '未来电商专营店', providerId: '3', providerName: '未来电商', planType: 'ultimate', planName: '旗舰版', maxShops: 50, shopCount: 12, expireDate: '2027-06-30 23:59:59', contactName: '王大伟', contactPhone: '13800138003', status: 'active', createTime: '2026-03-01 09:00:00' },
  { id: 'M2026004', name: '测试商户A', providerId: '1', providerName: '科技云', planType: 'free', planName: '免费版', maxShops: 1, shopCount: 1, expireDate: '2026-04-30 23:59:59', contactName: '赵测试', contactPhone: '13800138004', status: 'pending', createTime: '2026-04-10 16:45:00' },
  { id: 'M2026005', name: '星辰科技商城', providerId: '1', providerName: '科技云', planType: 'basic', planName: '普通版', maxShops: 3, shopCount: 3, expireDate: '2026-03-15 23:59:59', contactName: '刘星辰', contactPhone: '13800138005', status: 'expired', createTime: '2025-06-20 11:20:00' },
  { id: 'M2026006', name: '云端旗舰店', providerId: '2', providerName: '智慧零售', planType: 'custom', planName: '定制版', maxShops: 100, shopCount: 25, expireDate: '2028-01-31 23:59:59', contactName: '陈云端', contactPhone: '13800138006', status: 'active', createTime: '2025-12-01 08:30:00' }
])

const getPlanType = (type?: string) => {
  const map: Record<string, string> = {
    free: 'info',
    basic: '',
    standard: 'success',
    premium: 'warning',
    ultimate: 'danger',
    custom: 'primary'
  }
  return map[type || ''] || ''
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    active: 'success',
    pending: 'warning',
    disabled: 'info',
    expired: 'danger'
  }
  return map[status] || ''
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    active: '正常',
    pending: '待审核',
    disabled: '已禁用',
    expired: '套餐过期'
  }
  return map[status] || status
}

const isExpired = (date: string) => {
  return new Date(date) < new Date()
}

const isNearExpire = (date: string) => {
  const expire = new Date(date)
  const now = new Date()
  const diff = expire.getTime() - now.getTime()
  const days = diff / (1000 * 60 * 60 * 24)
  return days > 0 && days <= 30
}

const handleSearch = () => {
  ElMessage.success('搜索完成')
}

const resetSearch = () => {
  searchForm.name = ''
  searchForm.providerId = ''
  searchForm.planType = ''
  searchForm.status = ''
  searchForm.timeRange = ''
  searchForm.customDateRange = []
}

const handleAdd = () => {
  isEdit.value = false
  editId.value = ''
  form.name = ''
  form.providerId = ''
  form.planType = 'basic'
  form.contactName = ''
  form.contactPhone = ''
  form.contactEmail = ''
  form.address = ''
  form.remark = ''
  dialogVisible.value = true
}

const handleEdit = (row: Merchant) => {
  isEdit.value = true
  editId.value = row.id
  form.name = row.name
  form.providerId = row.providerId
  form.planType = row.planType
  form.contactName = row.contactName
  form.contactPhone = row.contactPhone
  form.contactEmail = row.contactEmail || ''
  form.address = row.address || ''
  dialogVisible.value = true
}

const handleView = (row: Merchant) => {
  ElMessage.info(`查看商户: ${row.name}`)
}

const handleChangePlan = (row: Merchant) => {
  currentMerchant.value = row
  planForm.newPlanType = row.planType
  planForm.duration = 12
  planForm.reason = ''
  planDialogVisible.value = true
}

const handlePlanSubmit = () => {
  ElMessage.success('套餐变更成功')
  planDialogVisible.value = false
}

const handleToggle = (row: Merchant) => {
  const action = row.status === 'disabled' ? '启用' : '禁用'
  ElMessageBox.confirm(`确定要${action}该商户吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    row.status = row.status === 'disabled' ? 'active' : 'disabled'
    ElMessage.success(`${action}成功`)
  })
}

const handleExport = () => {
  ElMessage.success('导出成功')
}

const handleSelectionChange = (selection: Merchant[]) => {
  selectedMerchants.value = selection
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (valid) {
      ElMessage.success(isEdit.value ? '编辑成功' : '添加成功')
      dialogVisible.value = false
    }
  })
}
</script>

<style scoped>
.page-container {
  padding: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 15px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.merchant-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.merchant-detail {
  display: flex;
  flex-direction: column;
}

.merchant-name {
  font-weight: 500;
  color: #303133;
}

.merchant-id {
  font-size: 12px;
  color: #909399;
}

.limit-warning {
  color: #f56c6c;
  font-weight: bold;
}

.expired {
  color: #f56c6c;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
