<template>
  <div class="license-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #409eff;">
            <el-icon :size="28"><Key /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">总授权数</div>
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
            <div class="stat-label">已激活</div>
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
            <div class="stat-label">未激活</div>
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
            <div class="stat-label">已过期</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="授权码">
          <el-input v-model="searchForm.code" placeholder="请输入授权码" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="服务商">
          <el-select v-model="searchForm.providerId" placeholder="全部服务商" clearable style="width: 150px">
            <el-option label="科技云" value="1" />
            <el-option label="智慧零售" value="2" />
            <el-option label="未来电商" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="未激活" value="pending" />
            <el-option label="已激活" value="active" />
            <el-option label="已过期" value="expired" />
            <el-option label="已禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="服务商等级">
          <el-select v-model="searchForm.providerLevel" placeholder="全部等级" clearable style="width: 120px">
            <el-option label="普通服务商" value="normal" />
            <el-option label="铜牌服务商" value="bronze" />
            <el-option label="银牌服务商" value="silver" />
            <el-option label="金牌服务商" value="gold" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>授权列表</span>
          <div>
            <el-button type="success" @click="handleBatchGenerate">
              <el-icon><Plus /></el-icon> 批量生成
            </el-button>
            <el-button type="primary" @click="handleExport">
              <el-icon><Download /></el-icon> 导出
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="licenseList" stripe @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
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
        <el-table-column prop="providerLevel" label="服务商等级" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.providerLevel)">{{ getLevelText(row.providerLevel) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="providerName" label="所属服务商" min-width="120" />
        <el-table-column prop="merchantName" label="绑定商户" min-width="120">
          <template #default="{ row }">
            <span v-if="row.merchantName">{{ row.merchantName }}</span>
            <el-tag v-else type="info" size="small">未绑定</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="expireDate" label="到期时间" min-width="150" />
        <el-table-column prop="createTime" label="创建时间" min-width="150" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" @click="handleRenew(row)">续期</el-button>
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

    <!-- 批量生成对话框 -->
    <el-dialog v-model="generateVisible" title="批量生成授权码" width="500px">
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="服务商等级">
          <el-select v-model="generateForm.providerLevel" style="width: 100%">
            <el-option label="普通服务商" value="normal" />
            <el-option label="铜牌服务商" value="bronze" />
            <el-option label="银牌服务商" value="silver" />
            <el-option label="金牌服务商" value="gold" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属服务商">
          <el-select v-model="generateForm.providerId" style="width: 100%">
            <el-option label="科技云" value="1" />
            <el-option label="智慧零售" value="2" />
            <el-option label="未来电商" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="有效期">
          <el-select v-model="generateForm.duration" style="width: 100%">
            <el-option label="1个月" :value="1" />
            <el-option label="3个月" :value="3" />
            <el-option label="6个月" :value="6" />
            <el-option label="1年" :value="12" />
            <el-option label="永久" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="生成数量">
          <el-input-number v-model="generateForm.count" :min="1" :max="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="generateForm.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateVisible = false">取消</el-button>
        <el-button type="primary" @click="handleGenerateSubmit">生成</el-button>
      </template>
    </el-dialog>

    <!-- 续期对话框 -->
    <el-dialog v-model="renewVisible" title="授权续期" width="400px">
      <el-form :model="renewForm" label-width="100px">
        <el-form-item label="授权码">
          <span>{{ currentLicense?.code }}</span>
        </el-form-item>
        <el-form-item label="当前到期">
          <span>{{ currentLicense?.expireDate }}</span>
        </el-form-item>
        <el-form-item label="续期时长">
          <el-select v-model="renewForm.duration" style="width: 100%">
            <el-option label="1个月" :value="1" />
            <el-option label="3个月" :value="3" />
            <el-option label="6个月" :value="6" />
            <el-option label="1年" :value="12" />
            <el-option label="永久" :value="0" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renewVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRenewSubmit">确认续期</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Key, CircleCheck, Timer, Warning, Search, Plus, Download, CopyDocument } from '@element-plus/icons-vue'

const stats = reactive({
  total: 12580,
  active: 10234,
  pending: 1567,
  expired: 589
})

const searchForm = reactive({
  code: '',
  providerId: '',
  status: '',
  providerLevel: ''
})

const page = reactive({
  current: 1,
  size: 10,
  total: 100
})

const generateVisible = ref(false)
const renewVisible = ref(false)
const currentLicense = ref<any>(null)
const selectedLicenses = ref<any[]>([])

const generateForm = reactive({
  providerLevel: 'normal',
  providerId: '',
  duration: 12,
  count: 10,
  remark: ''
})

const renewForm = reactive({
  duration: 12
})

const licenseList = ref([
  { id: '1', code: 'EAMS-PRO-2026-X8K9M2N4P5', providerLevel: 'gold', providerName: '科技云', merchantName: '小明电商', status: 'active', expireDate: '2027-03-31 23:59:59', createTime: '2026-03-31 10:30:00' },
  { id: '2', code: 'EAMS-ENT-2026-Q7W3E4R5T6', providerLevel: 'silver', providerName: '智慧零售', merchantName: '', status: 'pending', expireDate: '2027-03-31 23:59:59', createTime: '2026-03-31 09:15:00' },
  { id: '3', code: 'EAMS-ULT-2026-Y2U8I9O0P1', providerLevel: 'gold', providerName: '未来电商', merchantName: '大伟科技', status: 'active', expireDate: '2026-12-31 23:59:59', createTime: '2026-03-30 16:45:00' },
  { id: '4', code: 'EAMS-PRO-2026-A1S2D3F4G5', providerLevel: 'bronze', providerName: '星辰科技', merchantName: '', status: 'expired', expireDate: '2026-03-15 23:59:59', createTime: '2025-03-15 08:00:00' },
  { id: '5', code: 'EAMS-ENT-2026-H6J7K8L9Z0', providerLevel: 'normal', providerName: '云端商务', merchantName: '云端旗舰店', status: 'disabled', expireDate: '2027-01-31 23:59:59', createTime: '2026-01-31 14:20:00' }
])

const getLevelType = (level: string) => {
  const map: Record<string, string> = {
    normal: 'info',
    bronze: 'warning',
    silver: 'success',
    gold: 'danger'
  }
  return map[level] || ''
}

const getLevelText = (level: string) => {
  const map: Record<string, string> = {
    normal: '普通服务商',
    bronze: '铜牌服务商',
    silver: '银牌服务商',
    gold: '金牌服务商'
  }
  return map[level] || level
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    active: 'success',
    pending: 'info',
    expired: 'danger',
    disabled: 'warning'
  }
  return map[status] || ''
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    active: '已激活',
    pending: '未激活',
    expired: '已过期',
    disabled: '已禁用'
  }
  return map[status] || status
}

const handleSearch = () => {
  ElMessage.success('搜索完成')
}

const resetSearch = () => {
  searchForm.code = ''
  searchForm.providerId = ''
  searchForm.status = ''
  searchForm.providerLevel = ''
}

const handleBatchGenerate = () => {
  generateVisible.value = true
}

const handleGenerateSubmit = () => {
  ElMessage.success(`成功生成 ${generateForm.count} 个授权码`)
  generateVisible.value = false
}

const handleExport = () => {
  ElMessage.success('导出成功')
}

const copyCode = (code: string) => {
  navigator.clipboard.writeText(code)
  ElMessage.success('已复制到剪贴板')
}

const handleView = (_row: any) => {
  ElMessage.info('查看授权详情')
}

const handleRenew = (row: any) => {
  currentLicense.value = row
  renewVisible.value = true
}

const handleRenewSubmit = () => {
  ElMessage.success('续期成功')
  renewVisible.value = false
}

const handleToggle = (row: any) => {
  const action = row.status === 'disabled' ? '启用' : '禁用'
  ElMessageBox.confirm(`确定要${action}该授权码吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    row.status = row.status === 'disabled' ? 'active' : 'disabled'
    ElMessage.success(`${action}成功`)
  })
}

const handleSelectionChange = (selection: any[]) => {
  selectedLicenses.value = selection
}
</script>

<style scoped>
.license-container {
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

.code-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.code-text {
  font-family: monospace;
  font-size: 13px;
  color: #409eff;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
