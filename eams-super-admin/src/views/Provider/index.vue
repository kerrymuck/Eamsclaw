<template>
  <div class="provider-container">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="服务商名称">
          <el-input v-model="searchForm.name" placeholder="请输入服务商名称" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable>
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="disabled" />
            <el-option label="待审核" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="searchForm.level" placeholder="全部等级" clearable>
            <el-option label="金牌服务商" value="gold" />
            <el-option label="银牌服务商" value="silver" />
            <el-option label="铜牌服务商" value="bronze" />
            <el-option label="普通服务商" value="normal" />
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
          <span>服务商列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 新增服务商
          </el-button>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table :data="providerList" v-loading="loading" stripe>
        <el-table-column type="index" width="50" />
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
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="level" label="等级" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)">{{ getLevelText(row.level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="licenseCount" label="授权数" min-width="80" />
        <el-table-column prop="balance" label="账户余额" min-width="120">
          <template #default="{ row }">
            <span class="balance">¥{{ row.balance.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : row.status === 'pending' ? 'warning' : 'danger'">
              {{ row.status === 'active' ? '正常' : row.status === 'pending' ? '待审核' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" min-width="150" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleRecharge(row)">充值</el-button>
            <el-button link :type="row.status === 'active' ? 'danger' : 'success'" @click="handleToggleStatus(row)">
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增服务商' : '编辑服务商'"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="服务商名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="Logo">
          <el-upload
            class="avatar-uploader"
            action="#"
            :show-file-list="false"
            :auto-upload="false"
          >
            <img v-if="form.logo" :src="form.logo" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="联系人" prop="contact">
          <el-input v-model="form.contact" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="等级" prop="level">
          <el-select v-model="form.level" style="width: 100%">
            <el-option label="金牌服务商" value="gold" />
            <el-option label="银牌服务商" value="silver" />
            <el-option label="铜牌服务商" value="bronze" />
            <el-option label="普通服务商" value="normal" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 充值对话框 -->
    <el-dialog v-model="rechargeVisible" title="账户充值" width="400px">
      <el-form :model="rechargeForm" label-width="100px">
        <el-form-item label="服务商">
          <span>{{ currentProvider?.name }}</span>
        </el-form-item>
        <el-form-item label="当前余额">
          <span class="balance">¥{{ currentProvider?.balance?.toLocaleString() }}</span>
        </el-form-item>
        <el-form-item label="充值金额">
          <el-input-number v-model="rechargeForm.amount" :min="1" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="rechargeForm.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rechargeVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRechargeSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'

const loading = ref(false)
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const rechargeVisible = ref(false)
const currentProvider = ref<any>(null)

const searchForm = reactive({
  name: '',
  status: '',
  level: ''
})

const page = reactive({
  current: 1,
  size: 10,
  total: 100
})

const form = reactive({
  id: '',
  name: '',
  logo: '',
  contact: '',
  phone: '',
  email: '',
  level: 'normal',
  remark: ''
})

const rechargeForm = reactive({
  amount: 1000,
  remark: ''
})

const rules = {
  name: [{ required: true, message: '请输入服务商名称', trigger: 'blur' }],
  contact: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  level: [{ required: true, message: '请选择等级', trigger: 'change' }]
}

// 模拟数据
const providerList = ref([
  { id: '1', name: '科技云', logo: '', contact: '张三', phone: '13800138001', email: 'zhangsan@kejiyun.com', level: 'gold', licenseCount: 156, balance: 125800, status: 'active', createTime: '2026-01-15 10:30:00' },
  { id: '2', name: '智慧零售', logo: '', contact: '李四', phone: '13800138002', email: 'lisi@zhihui.com', level: 'silver', licenseCount: 89, balance: 67800, status: 'active', createTime: '2026-01-20 14:20:00' },
  { id: '3', name: '未来电商', logo: '', contact: '王五', phone: '13800138003', email: 'wangwu@weilai.com', level: 'bronze', licenseCount: 45, balance: 23400, status: 'pending', createTime: '2026-03-01 09:00:00' },
  { id: '4', name: '星辰科技', logo: '', contact: '赵六', phone: '13800138004', email: 'zhaoliu@xingchen.com', level: 'normal', licenseCount: 23, balance: 8900, status: 'active', createTime: '2026-02-10 16:45:00' },
  { id: '5', name: '云端商务', logo: '', contact: '钱七', phone: '13800138005', email: 'qianqi@yunduan.com', level: 'gold', licenseCount: 234, balance: 256000, status: 'disabled', createTime: '2025-12-01 08:00:00' }
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
    gold: '金牌',
    silver: '银牌',
    bronze: '铜牌',
    normal: '普通'
  }
  return map[level] || level
}

const handleSearch = () => {
  ElMessage.success('搜索完成')
}

const resetSearch = () => {
  searchForm.name = ''
  searchForm.status = ''
  searchForm.level = ''
}

const handleAdd = () => {
  dialogType.value = 'add'
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  dialogType.value = 'edit'
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleSubmit = () => {
  ElMessage.success(dialogType.value === 'add' ? '新增成功' : '编辑成功')
  dialogVisible.value = false
}

const handleRecharge = (row: any) => {
  currentProvider.value = row
  rechargeVisible.value = true
}

const handleRechargeSubmit = () => {
  ElMessage.success(`充值 ¥${rechargeForm.amount} 成功`)
  rechargeVisible.value = false
}

const handleToggleStatus = (row: any) => {
  const action = row.status === 'active' ? '禁用' : '启用'
  ElMessageBox.confirm(`确定要${action}该服务商吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    row.status = row.status === 'active' ? 'disabled' : 'active'
    ElMessage.success(`${action}成功`)
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
.provider-container {
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

.balance {
  color: #f56c6c;
  font-weight: bold;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.avatar-uploader {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 80px;
  height: 80px;
}

.avatar-uploader-icon {
  font-size: 20px;
  color: #8c939d;
  width: 80px;
  height: 80px;
  text-align: center;
  line-height: 80px;
}

.avatar {
  width: 80px;
  height: 80px;
  display: block;
}
</style>
