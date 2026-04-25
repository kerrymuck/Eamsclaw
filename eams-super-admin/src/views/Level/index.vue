<template>
  <div class="page-container">
    <h3>服务商等级</h3>
    <p>管理服务商等级体系</p>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>等级列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 添加等级
          </el-button>
        </div>
      </template>
      
      <el-table :data="levelList" stripe>
        <el-table-column prop="name" label="等级名称" />
        <el-table-column prop="minLicenses" label="最小授权数" />
        <el-table-column prop="maxLicenses" label="最大授权数" />
        <el-table-column prop="discount" label="折扣率">
          <template #default="{ row }">
            {{ row.discount }}%
          </template>
        </el-table-column>
        <el-table-column prop="upgradeAmount" label="升级所需充值金额">
          <template #default="{ row }">
            <span v-if="row.upgradeAmount">¥{{ row.upgradeAmount.toLocaleString() }}</span>
            <el-tag v-else type="info" size="small">无</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row, $index }">
            <el-button link type="primary" @click="handleEdit(row, $index)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑等级对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑等级' : '添加等级'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="140px">
        <el-form-item label="等级名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入等级名称" />
        </el-form-item>
        <el-form-item label="最小授权数" prop="minLicenses">
          <el-input-number v-model="form.minLicenses" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="最大授权数" prop="maxLicenses">
          <el-input-number v-model="form.maxLicenses" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="折扣率(%)" prop="discount">
          <el-input-number v-model="form.discount" :min="0" :max="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="升级所需充值金额" prop="upgradeAmount">
          <el-input-number v-model="form.upgradeAmount" :min="0" :precision="2" style="width: 100%" />
          <span class="form-tip">达到此金额自动升级到该等级（0表示不自动升级）</span>
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
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

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

const dialogVisible = ref(false)
const isEdit = ref(false)
const editIndex = ref(-1)
const formRef = ref<FormInstance>()

const form = reactive<Level>({
  name: '',
  minLicenses: 0,
  maxLicenses: 0,
  discount: 100,
  upgradeAmount: 0
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入等级名称', trigger: 'blur' }],
  minLicenses: [{ required: true, message: '请输入最小授权数', trigger: 'blur' }],
  maxLicenses: [{ required: true, message: '请输入最大授权数', trigger: 'blur' }],
  discount: [{ required: true, message: '请输入折扣率', trigger: 'blur' }]
}

const resetForm = () => {
  form.name = ''
  form.minLicenses = 0
  form.maxLicenses = 0
  form.discount = 100
  form.upgradeAmount = 0
}

const handleAdd = () => {
  isEdit.value = false
  editIndex.value = -1
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: Level, index: number) => {
  isEdit.value = true
  editIndex.value = index
  form.name = row.name
  form.minLicenses = row.minLicenses
  form.maxLicenses = row.maxLicenses
  form.discount = row.discount
  form.upgradeAmount = row.upgradeAmount
  dialogVisible.value = true
}

const handleDelete = (index: number) => {
  ElMessageBox.confirm('确定要删除该等级吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    levelList.value.splice(index, 1)
    ElMessage.success('删除成功')
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (valid) {
      if (isEdit.value && editIndex.value >= 0) {
        levelList.value[editIndex.value] = { ...form }
        ElMessage.success('编辑成功')
      } else {
        levelList.value.push({ ...form })
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

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
