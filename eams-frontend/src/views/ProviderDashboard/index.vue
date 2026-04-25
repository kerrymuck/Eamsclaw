<template>
  <div class="provider-dashboard">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>🏢 服务商工作台</h2>
        <p class="subtitle">管理您的签约商家，查看业绩数据</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showAddMerchantDialog = true">
          <el-icon><Plus /></el-icon>
          添加商家
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #e6f7ff; color: #1890ff;">🏪</div>
          <div class="stat-info">
            <div class="stat-value">{{ merchants.length }}</div>
            <div class="stat-label">签约商家</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #f6ffed; color: #52c41a;">💰</div>
          <div class="stat-info">
            <div class="stat-value">¥{{ totalRevenue }}</div>
            <div class="stat-label">本月收益</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #fff7e6; color: #fa8c16;">📈</div>
          <div class="stat-info">
            <div class="stat-value">{{ activeMerchants }}</div>
            <div class="stat-label">活跃商家</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #f9f0ff; color: #722ed1;">🆕</div>
          <div class="stat-info">
            <div class="stat-value">{{ newMerchantsThisMonth }}</div>
            <div class="stat-label">本月新增</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 商家列表 -->
    <el-card class="merchant-list-card">
      <template #header>
        <div class="card-header">
          <span>商家管理</span>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索商家名称"
            style="width: 240px"
            :prefix-icon="Search"
            clearable
          />
        </div>
      </template>

      <el-table :data="filteredMerchants" style="width: 100%" v-loading="loading">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column label="商家信息" min-width="200">
          <template #default="{ row }">
            <div class="merchant-info">
              <el-avatar :size="40" :src="row.logo">{{ row.name.charAt(0) }}</el-avatar>
              <div class="merchant-detail">
                <div class="merchant-name">{{ row.name }}</div>
                <div class="merchant-contact">{{ row.contact }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="shopCount" label="店铺数" width="100" />
        <el-table-column prop="staffCount" label="员工数" width="100" />
        <el-table-column prop="monthlyFee" label="月费" width="120">
          <template #default="{ row }">
            ¥{{ row.monthlyFee }}
          </template>
        </el-table-column>
        <el-table-column prop="expireDate" label="到期时间" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewMerchant(row)">查看</el-button>
            <el-button link type="primary" @click="editMerchant(row)">编辑</el-button>
            <el-button link type="danger" @click="disableMerchant(row)">
              {{ row.status === 'active' ? '停用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
        />
      </div>
    </el-card>

    <!-- 添加商家弹窗 -->
    <el-dialog
      v-model="showAddMerchantDialog"
      title="添加商家"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="商家名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入商家名称" />
        </el-form-item>

        <el-form-item label="联系人" prop="contact">
          <el-input v-model="form.contact" placeholder="请输入联系人姓名" />
        </el-form-item>

        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系电话" />
        </el-form-item>

        <el-form-item label="月费金额" prop="monthlyFee">
          <el-input-number v-model="form.monthlyFee" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>

        <el-form-item label="到期时间" prop="expireDate">
          <el-date-picker
            v-model="form.expireDate"
            type="date"
            placeholder="选择到期时间"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="可选填" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddMerchantDialog = false">取消</el-button>
        <el-button type="primary" @click="saveMerchant" :loading="saving">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const loading = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)

// 商家数据
const merchants = ref([
  { id: 1, name: '龙猫数码旗舰店', contact: '张三', phone: '13800138001', logo: '', shopCount: 5, staffCount: 12, monthlyFee: 2999, expireDate: '2026-12-31', status: 'active' },
  { id: 2, name: '潮流服饰专营店', contact: '李四', phone: '13800138002', logo: '', shopCount: 3, staffCount: 8, monthlyFee: 1999, expireDate: '2026-11-30', status: 'active' },
  { id: 3, name: '美妆护肤集合店', contact: '王五', phone: '13800138003', logo: '', shopCount: 2, staffCount: 5, monthlyFee: 1499, expireDate: '2026-10-31', status: 'active' },
  { id: 4, name: '食品生鲜超市', contact: '赵六', phone: '13800138004', logo: '', shopCount: 4, staffCount: 15, monthlyFee: 2499, expireDate: '2026-09-30', status: 'inactive' },
  { id: 5, name: '家居生活馆', contact: '孙七', phone: '13800138005', logo: '', shopCount: 2, staffCount: 6, monthlyFee: 1299, expireDate: '2026-12-31', status: 'active' },
])

// 统计数据
const totalRevenue = computed(() => {
  return merchants.value.reduce((sum, m) => sum + m.monthlyFee, 0).toLocaleString()
})

const activeMerchants = computed(() => {
  return merchants.value.filter(m => m.status === 'active').length
})

const newMerchantsThisMonth = ref(3)

// 筛选商家
const filteredMerchants = computed(() => {
  if (!searchKeyword.value) return merchants.value
  return merchants.value.filter(m => 
    m.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

// 添加商家弹窗
const showAddMerchantDialog = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  contact: '',
  phone: '',
  monthlyFee: 1999,
  expireDate: '',
  remark: ''
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入商家名称', trigger: 'blur' }],
  contact: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  monthlyFee: [{ required: true, message: '请输入月费金额', trigger: 'blur' }],
  expireDate: [{ required: true, message: '请选择到期时间', trigger: 'change' }]
}

const saveMerchant = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (!valid) return
    
    saving.value = true
    setTimeout(() => {
      const newMerchant = {
        id: Date.now(),
        name: form.name,
        contact: form.contact,
        phone: form.phone,
        logo: '',
        shopCount: 0,
        staffCount: 0,
        monthlyFee: form.monthlyFee,
        expireDate: form.expireDate,
        status: 'active'
      }
      merchants.value.unshift(newMerchant)
      ElMessage.success('商家添加成功')
      saving.value = false
      showAddMerchantDialog.value = false
    }, 500)
  })
}

const viewMerchant = (row: any) => {
  ElMessage.info(`查看商家: ${row.name}`)
}

const editMerchant = (row: any) => {
  ElMessage.info(`编辑商家: ${row.name}`)
}

const disableMerchant = (row: any) => {
  const action = row.status === 'active' ? '停用' : '启用'
  ElMessageBox.confirm(
    `确定要${action}商家「${row.name}」吗？`,
    '确认操作',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    row.status = row.status === 'active' ? 'inactive' : 'active'
    ElMessage.success(`商家已${action}`)
  })
}
</script>

<style scoped>
.provider-dashboard {
  padding: 20px;
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
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 12px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.merchant-list-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.merchant-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.merchant-detail {
  display: flex;
  flex-direction: column;
}

.merchant-name {
  font-weight: 500;
  color: #303133;
}

.merchant-contact {
  font-size: 12px;
  color: #909399;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
