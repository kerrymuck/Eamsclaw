<template>
  <div class="blacklist-container">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="服务商名称">
          <el-input v-model="searchForm.name" placeholder="请输入服务商名称" clearable />
        </el-form-item>
        <el-form-item label="拉黑原因">
          <el-select v-model="searchForm.reason" placeholder="全部原因" clearable>
            <el-option label="违规操作" value="violation" />
            <el-option label="欠费" value="arrears" />
            <el-option label="投诉过多" value="complaint" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间周期">
          <el-select v-model="searchForm.timeRange" placeholder="全部时间" clearable @change="handleTimeRangeChange">
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

    <!-- 黑名单列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>服务商黑名单</span>
          <el-button type="danger" @click="handleBatchRemove">
            <el-icon><Delete /></el-icon> 批量移出黑名单
          </el-button>
        </div>
      </template>

      <el-table :data="blacklist" v-loading="loading" stripe @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="服务商名称" min-width="150">
          <template #default="{ row }">
            <div class="provider-info">
              <el-avatar :size="32" :src="row.logo" />
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="contact" label="联系人" min-width="100" />
        <el-table-column prop="phone" label="联系电话" min-width="120" />
        <el-table-column prop="reason" label="拉黑原因" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getReasonType(row.reason)">{{ getReasonText(row.reason) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注说明" min-width="200" show-overflow-tooltip />
        <el-table-column prop="blacklistTime" label="拉黑时间" min-width="150" />
        <el-table-column prop="operator" label="操作人" min-width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleViewDetail(row)">查看详情</el-button>
            <el-button link type="success" @click="handleRemove(row)">移出黑名单</el-button>
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
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 查看详情对话框 -->
    <el-dialog v-model="detailVisible" title="黑名单详情" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="服务商名称">{{ currentProvider?.name }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ currentProvider?.contact }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentProvider?.phone }}</el-descriptions-item>
        <el-descriptions-item label="拉黑原因">
          <el-tag :type="getReasonType(currentProvider?.reason)">{{ getReasonText(currentProvider?.reason) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注说明">{{ currentProvider?.remark || '无' }}</el-descriptions-item>
        <el-descriptions-item label="拉黑时间">{{ currentProvider?.blacklistTime }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ currentProvider?.operator }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="success" @click="handleRemove(currentProvider)">移出黑名单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const detailVisible = ref(false)
const currentProvider = ref<any>(null)
const selectedProviders = ref<any[]>([])

const searchForm = reactive({
  name: '',
  reason: '',
  timeRange: '',
  customDateRange: [] as string[]
})

const page = reactive({
  current: 1,
  size: 10,
  total: 5
})

// 模拟黑名单数据
const blacklist = ref([
  { id: '1', name: '问题服务商A', logo: '', contact: '张三', phone: '13800138001', reason: 'violation', remark: '多次违规操作，恶意刷单', blacklistTime: '2026-03-15 14:30:00', operator: 'admin' },
  { id: '2', name: '欠费服务商B', logo: '', contact: '李四', phone: '13800138002', reason: 'arrears', remark: '欠费超过3个月', blacklistTime: '2026-02-20 10:15:00', operator: 'admin' },
  { id: '3', name: '投诉服务商C', logo: '', contact: '王五', phone: '13800138003', reason: 'complaint', remark: '客户投诉过多，服务态度差', blacklistTime: '2026-01-10 16:45:00', operator: 'admin' },
  { id: '4', name: '异常服务商D', logo: '', contact: '赵六', phone: '13800138004', reason: 'other', remark: '其他原因', blacklistTime: '2025-12-01 09:00:00', operator: 'admin' },
  { id: '5', name: '违规服务商E', logo: '', contact: '钱七', phone: '13800138005', reason: 'violation', remark: '违反平台规定', blacklistTime: '2025-11-15 11:20:00', operator: 'admin' }
])

const getReasonType = (reason?: string) => {
  const map: Record<string, string> = {
    violation: 'danger',
    arrears: 'warning',
    complaint: 'info',
    other: ''
  }
  return map[reason || ''] || ''
}

const getReasonText = (reason?: string) => {
  const map: Record<string, string> = {
    violation: '违规操作',
    arrears: '欠费',
    complaint: '投诉过多',
    other: '其他'
  }
  return map[reason || ''] || reason
}

const handleTimeRangeChange = (val: string) => {
  if (val !== 'custom') {
    searchForm.customDateRange = []
  }
}

const handleSearch = () => {
  ElMessage.success('搜索完成')
}

const resetSearch = () => {
  searchForm.name = ''
  searchForm.reason = ''
  searchForm.timeRange = ''
  searchForm.customDateRange = []
}

const handleSelectionChange = (selection: any[]) => {
  selectedProviders.value = selection
}

const handleViewDetail = (row: any) => {
  currentProvider.value = row
  detailVisible.value = true
}

const handleRemove = (row: any) => {
  ElMessageBox.confirm(`确定要将 "${row.name}" 移出黑名单吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = blacklist.value.findIndex(item => item.id === row.id)
    if (index > -1) {
      blacklist.value.splice(index, 1)
    }
    ElMessage.success('移出黑名单成功')
    detailVisible.value = false
  })
}

const handleBatchRemove = () => {
  if (selectedProviders.value.length === 0) {
    ElMessage.warning('请选择要移出黑名单的服务商')
    return
  }
  ElMessageBox.confirm(`确定要将选中的 ${selectedProviders.value.length} 个服务商移出黑名单吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const ids = selectedProviders.value.map(item => item.id)
    blacklist.value = blacklist.value.filter(item => !ids.includes(item.id))
    ElMessage.success('批量移出黑名单成功')
  })
}

const handleSizeChange = (val: number) => {
  page.size = val
}

const handleCurrentChange = (val: number) => {
  page.current = val
}
</script>

<style scoped>
.blacklist-container {
  padding: 0;
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

.provider-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
