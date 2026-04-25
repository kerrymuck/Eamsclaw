<template>
  <div class="license-management">
    <div class="page-header">
      <div class="header-left">
        <h2>🔑 授权码管理</h2>
        <p class="subtitle">生成、管理和分发商户授权码（一个店铺一个授权码）</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showGenerateDialog = true">
          <el-icon><Plus /></el-icon>
          生成授权码
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon blue">🔑</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">总授权码</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon green">✅</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.active }}</div>
            <div class="stat-label">已激活</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon orange">⏳</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pending }}</div>
            <div class="stat-label">待激活</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon purple">💰</div>
          <div class="stat-info">
            <div class="stat-value purchase-price">¥{{ providerInfo.purchasePrice }}</div>
            <div class="stat-label">我的拿货价/个/年</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 授权码价格说明 -->
    <el-card class="price-info-card">
      <template #header>
        <span>💡 授权码价格说明</span>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="官方零售价">¥{{ licensePrice.retail }} /个/年</el-descriptions-item>
        <el-descriptions-item label="我的等级">{{ providerInfo.level }}</el-descriptions-item>
        <el-descriptions-item label="享受折扣">{{ providerInfo.discount }}%</el-descriptions-item>
        <el-descriptions-item label="我的拿货价" :span="3">
          <span class="highlight-price">¥{{ providerInfo.purchasePrice }} /个/年</span>
          <span class="price-calc-tip">（{{ licensePrice.retail }} × {{ providerInfo.discount }}% = {{ providerInfo.purchasePrice }}）</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 搜索筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="授权码">
          <el-input v-model="filterForm.code" placeholder="请输入授权码" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="待激活" value="pending" />
            <el-option label="已激活" value="active" />
            <el-option label="已过期" value="expired" />
            <el-option label="已禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="绑定商户">
          <el-select v-model="filterForm.merchantId" placeholder="全部商户" clearable style="width: 150px">
            <el-option v-for="m in merchantList" :key="m.id" :label="m.name" :value="m.id" />
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
        <el-form-item label="生成时间">
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

    <!-- 授权码列表 -->
    <el-card class="list-card">
      <el-table :data="licenseList" v-loading="loading" stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="code" label="授权码" min-width="200">
          <template #default="{ row }">
            <div class="code-cell">
              <span class="code-text">{{ row.code }}</span>
              <el-button link type="primary" @click="copyCode(row.code)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="merchantName" label="绑定商户" min-width="150">
          <template #default="{ row }">
            <span v-if="row.merchantName">{{ row.merchantName }}</span>
            <span v-else class="text-gray">未绑定</span>
          </template>
        </el-table-column>
        <el-table-column prop="shopName" label="绑定店铺" min-width="150">
          <template #default="{ row }">
            <span v-if="row.shopName">{{ row.shopName }}</span>
            <span v-else class="text-gray">未绑定</span>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="生成时间" width="160" />
        <el-table-column prop="expireTime" label="过期时间" width="160">
          <template #default="{ row }">
            <el-tag :type="getExpireType(row.expireTime)">{{ row.expireTime }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" link type="primary" @click="copyCode(row.code)">复制</el-button>
            <el-button v-if="row.status === 'pending'" link type="danger" @click="disableLicense(row)">禁用</el-button>
            <el-button v-if="row.status === 'active'" link type="primary" @click="viewDetail(row)">详情</el-button>
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

    <!-- 生成授权码弹窗 -->
    <el-dialog v-model="showGenerateDialog" title="生成授权码" width="550px">
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="选择商户" required>
          <el-select 
            v-model="generateForm.merchantId" 
            placeholder="请选择商户" 
            style="width: 100%"
            @change="handleMerchantChange"
          >
            <el-option 
              v-for="m in merchantList" 
              :key="m.id" 
              :label="m.name" 
              :value="m.id"
            />
          </el-select>
        </el-form-item>
        
        <!-- 商户套餐信息展示 -->
        <el-form-item v-if="selectedMerchant">
          <el-alert
            :title="`商户套餐：${selectedMerchant.planName}`"
            :description="`店铺数量：${selectedMerchant.shopCount} 个 | 员工账号：${selectedMerchant.maxStaff} 个 | 到期时间：${selectedMerchant.expireDate}`"
            type="info"
            :closable="false"
            show-icon
          />
        </el-form-item>
        
        <el-form-item label="生成数量" required>
          <el-input-number 
            v-model="generateForm.count" 
            :min="1" 
            :max="maxGenerateCount"
            style="width: 150px"
          />
          <span class="form-tip" v-if="selectedMerchant">
            （该商户有 {{ selectedMerchant.shopCount }} 个店铺，建议生成 {{ selectedMerchant.shopCount }} 个授权码）
          </span>
          <span class="form-tip" v-else>
            请先选择商户
          </span>
        </el-form-item>
        
        <el-form-item label="有效期" required>
          <el-radio-group v-model="generateForm.validity">
            <el-radio-button label="30">30天</el-radio-button>
            <el-radio-button label="90">90天</el-radio-button>
            <el-radio-button label="365">1年</el-radio-button>
            <el-radio-button label="0">永久</el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input v-model="generateForm.remark" type="textarea" :rows="2" placeholder="可选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" @click="generateLicenses" :loading="generating">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { Plus, Search, CopyDocument } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Merchant {
  id: string
  name: string
  planName: string
  planType: string
  shopCount: number
  maxStaff: number
  expireDate: string
}

const stats = ref({
  total: 12580,
  active: 10234,
  pending: 1560,
  expired: 786
})

// 授权码价格配置
const licensePrice = reactive({
  retail: 19.9,  // 官方零售价
})

// 服务商信息
const providerInfo = reactive({
  level: '银牌服务商',
  discount: 75,  // 折扣率
  purchasePrice: 14.93  // 计算后的拿货价
})

const filterForm = reactive({
  code: '',
  status: '',
  merchantId: '',
  timeRange: '',
  customDateRange: [] as string[],
  dateRange: []
})

const handleTimeRangeChange = (val: string) => {
  if (val !== 'custom') {
    filterForm.customDateRange = []
  }
}

const loading = ref(false)
const pageInfo = reactive({
  page: 1,
  pageSize: 10,
  total: 12580
})

// 商户列表
const merchantList = ref<Merchant[]>([
  { id: 'M001', name: '龙猫数码旗舰店', planName: '专业版', planType: 'pro', shopCount: 3, maxStaff: 10, expireDate: '2027-04-10' },
  { id: 'M002', name: '智慧零售体验店', planName: '标准版', planType: 'standard', shopCount: 2, maxStaff: 5, expireDate: '2026-12-31' },
  { id: 'M003', name: '未来电商专营店', planName: '旗舰版', planType: 'ultimate', shopCount: 5, maxStaff: 20, expireDate: '2027-06-30' },
  { id: 'M004', name: '星辰科技商城', planName: '普通版', planType: 'basic', shopCount: 1, maxStaff: 3, expireDate: '2026-10-15' }
])

const licenseList = ref([
  {
    id: 1,
    code: 'EAMS-PRO-2026-4X8K9M2N',
    merchantName: '龙猫数码旗舰店',
    shopName: '龙猫数码-主店',
    createTime: '2026-04-10 14:30:00',
    expireTime: '2027-04-10',
    status: 'active'
  },
  {
    id: 2,
    code: 'EAMS-ENT-2026-7P3Q5R8T',
    merchantName: '',
    shopName: '',
    createTime: '2026-04-10 10:15:00',
    expireTime: '2027-04-10',
    status: 'pending'
  },
  {
    id: 3,
    code: 'EAMS-BAS-2026-2W6Y4U1I',
    merchantName: '',
    shopName: '',
    createTime: '2026-04-09 16:45:00',
    expireTime: '2026-05-09',
    status: 'pending'
  }
])

const showGenerateDialog = ref(false)
const generating = ref(false)

const generateForm = reactive({
  merchantId: '',
  count: 1,
  validity: '365',
  remark: ''
})

// 当前选中的商户
const selectedMerchant = computed(() => {
  return merchantList.value.find(m => m.id === generateForm.merchantId)
})

// 最大生成数量
const maxGenerateCount = computed(() => {
  return selectedMerchant.value?.shopCount || 100
})

const handleMerchantChange = () => {
  // 自动设置生成数量为商户店铺数量
  if (selectedMerchant.value) {
    generateForm.count = selectedMerchant.value.shopCount
  }
}

const getExpireType = (date: string) => {
  const days = getRemainingDays(date)
  if (days <= 0) return 'danger'
  if (days <= 30) return 'warning'
  return 'success'
}

const getRemainingDays = (date: string) => {
  const end = new Date(date)
  const now = new Date()
  return Math.ceil((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    active: 'success',
    expired: 'danger',
    disabled: 'warning'
  }
  return map[status] || ''
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待激活',
    active: '已激活',
    expired: '已过期',
    disabled: '已禁用'
  }
  return map[status] || status
}

const copyCode = (code: string) => {
  navigator.clipboard.writeText(code)
  ElMessage.success('授权码已复制到剪贴板')
}

const disableLicense = (row: any) => {
  ElMessageBox.confirm(
    `确定要禁用授权码「${row.code}」吗？禁用后将无法激活。`,
    '确认禁用',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(() => {
    row.status = 'disabled'
    ElMessage.success('授权码已禁用')
  })
}

const viewDetail = (row: any) => {
  ElMessage.info(`查看授权码详情: ${row.code}`)
}

const handleSearch = () => {
  // 搜索逻辑
}

const resetFilter = () => {
  filterForm.code = ''
  filterForm.status = ''
  filterForm.merchantId = ''
  filterForm.timeRange = ''
  filterForm.customDateRange = []
  filterForm.dateRange = []
}

const generateLicenses = () => {
  if (!generateForm.merchantId) {
    ElMessage.warning('请选择商户')
    return
  }
  if (generateForm.count < 1) {
    ElMessage.warning('生成数量不能小于1')
    return
  }
  generating.value = true
  setTimeout(() => {
    ElMessage.success(`成功为「${selectedMerchant.value?.name}」生成 ${generateForm.count} 个授权码`)
    generating.value = false
    showGenerateDialog.value = false
    // 重置表单
    generateForm.merchantId = ''
    generateForm.count = 1
    generateForm.remark = ''
  }, 1000)
}
</script>

<style scoped>
.license-management {
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
.stat-icon.purple { background: #f9f0ff; }

.purchase-price {
  color: #e6a23c;
  font-size: 24px;
}

.price-info-card {
  margin-bottom: 20px;
}

.highlight-price {
  color: #f56c6c;
  font-size: 20px;
  font-weight: bold;
}

.price-calc-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 13px;
}

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

.filter-card, .list-card {
  margin-bottom: 20px;
}

.code-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.code-text {
  font-family: monospace;
  font-weight: 500;
  color: #1677ff;
}

.text-gray {
  color: #909399;
}

.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 13px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
