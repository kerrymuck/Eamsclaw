<template>
  <div class="settings-container">
    <h3>授权设置</h3>
    <p>配置授权码生成和验证规则</p>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>基础设置</span>
      </template>
      
      <el-form :model="form" label-width="150px">
        <el-form-item label="授权码前缀">
          <el-input v-model="form.prefix" style="width: 200px;" />
        </el-form-item>
        <el-form-item label="授权码价格">
          <el-input-number v-model="form.licensePrice" :min="0" :precision="2" style="width: 200px;" />
          <span style="margin-left: 10px;">元/个/年</span>
          <div class="form-tip">授权码按年收费，服务商拿货价在此基础上按等级折扣计算</div>
        </el-form-item>
        <el-form-item label="默认有效期">
          <el-input-number v-model="form.defaultExpireMonths" :min="1" :max="120" />
          <span style="margin-left: 10px;">个月</span>
        </el-form-item>
        <el-form-item label="允许解绑">
          <el-switch v-model="form.allowUnbind" />
        </el-form-item>
        <el-form-item label="解绑冷却期">
          <el-input-number v-model="form.unbindCooldownDays" :min="0" :max="30" />
          <span style="margin-left: 10px;">天</span>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 服务商等级授权配置 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>服务商等级授权配置</span>
          <el-button type="primary" @click="handleAddLevel">
            <el-icon><Plus /></el-icon> 添加等级配置
          </el-button>
        </div>
      </template>

      <el-alert
        title="授权类型已改为按服务商等级划分"
        description="不同等级的服务商可生成不同级别的授权码，高等级服务商享受更多权益"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px;"
      />

      <el-table :data="levelAuthList" stripe border>
        <el-table-column prop="levelName" label="服务商等级" min-width="120" />
        <el-table-column prop="authLevel" label="授权等级" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getAuthLevelType(row.authLevel)">{{ row.authLevel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="maxAuthCount" label="最大授权数" min-width="100" align="center" />
        <el-table-column prop="price" label="授权单价" min-width="120" align="right">
          <template #default="{ row }">
            <span class="price-text">¥{{ row.price.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="discount" label="折扣" min-width="100" align="center">
          <template #default="{ row }">
            <span class="discount-text">{{ row.discount }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="拿货价" min-width="120" align="right">
          <template #default="{ row }">
            <span class="purchase-price">¥{{ calculatePurchasePrice(row).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="200" />
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row, $index }">
            <el-button link type="primary" @click="handleEditLevel(row, $index)">编辑</el-button>
            <el-button link type="danger" @click="handleDeleteLevel($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 等级配置对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑等级配置' : '添加等级配置'" width="500px">
      <el-form :model="levelForm" :rules="rules" ref="formRef" label-width="140px">
        <el-form-item label="服务商等级" prop="levelName">
          <el-select v-model="levelForm.levelName" style="width: 100%" placeholder="选择服务商等级">
            <el-option label="普通服务商" value="普通服务商" />
            <el-option label="铜牌服务商" value="铜牌服务商" />
            <el-option label="银牌服务商" value="银牌服务商" />
            <el-option label="金牌服务商" value="金牌服务商" />
          </el-select>
        </el-form-item>
        <el-form-item label="授权等级" prop="authLevel">
          <el-select v-model="levelForm.authLevel" style="width: 100%" placeholder="选择授权等级">
            <el-option label="基础版" value="基础版" />
            <el-option label="专业版" value="专业版" />
            <el-option label="企业版" value="企业版" />
            <el-option label="旗舰版" value="旗舰版" />
          </el-select>
        </el-form-item>
        <el-form-item label="最大授权数" prop="maxAuthCount">
          <el-input-number v-model="levelForm.maxAuthCount" :min="1" :max="999999" style="width: 100%" />
        </el-form-item>
        <el-form-item label="授权单价" prop="price">
          <el-input-number v-model="levelForm.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="折扣(%)" prop="discount">
          <el-input-number v-model="levelForm.discount" :min="0" :max="100" style="width: 100%" />
          <span class="form-tip">实际售价 = 单价 × 折扣%</span>
        </el-form-item>
        <el-form-item label="说明" prop="description">
          <el-input v-model="levelForm.description" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <div style="margin-top: 20px;">
      <el-button type="primary" @click="handleSave">保存所有设置</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

interface LevelAuth {
  levelName: string
  authLevel: string
  maxAuthCount: number
  price: number
  discount: number
  description: string
}

const form = reactive({
  prefix: 'EAMS',
  licensePrice: 19.9,
  defaultExpireMonths: 12,
  allowUnbind: true,
  unbindCooldownDays: 7
})

// 服务商等级授权配置
const levelAuthList = ref<LevelAuth[]>([
  { levelName: '普通服务商', authLevel: '基础版', maxAuthCount: 20, price: 599, discount: 100, description: '基础功能，适合小型商户' },
  { levelName: '铜牌服务商', authLevel: '专业版', maxAuthCount: 49, price: 999, discount: 85, description: '专业功能，适合中型商户' },
  { levelName: '银牌服务商', authLevel: '企业版', maxAuthCount: 99, price: 1999, discount: 75, description: '企业功能，适合大型商户' },
  { levelName: '金牌服务商', authLevel: '旗舰版', maxAuthCount: 999999, price: 3999, discount: 60, description: '全部功能，无限制使用' }
])

const dialogVisible = ref(false)
const isEdit = ref(false)
const editIndex = ref(-1)
const formRef = ref<FormInstance>()

const levelForm = reactive<LevelAuth>({
  levelName: '',
  authLevel: '',
  maxAuthCount: 100,
  price: 0,
  discount: 100,
  description: ''
})

const rules: FormRules = {
  levelName: [{ required: true, message: '请选择服务商等级', trigger: 'change' }],
  authLevel: [{ required: true, message: '请选择授权等级', trigger: 'change' }],
  maxAuthCount: [{ required: true, message: '请输入最大授权数', trigger: 'blur' }],
  price: [{ required: true, message: '请输入授权单价', trigger: 'blur' }],
  discount: [{ required: true, message: '请输入折扣', trigger: 'blur' }]
}

const getAuthLevelType = (level: string) => {
  const types: Record<string, string> = {
    '基础版': 'info',
    '专业版': '',
    '企业版': 'success',
    '旗舰版': 'danger'
  }
  return types[level] || ''
}

// 计算服务商拿货价
const calculatePurchasePrice = (row: LevelAuth) => {
  return form.licensePrice * (row.discount / 100)
}

const handleAddLevel = () => {
  isEdit.value = false
  editIndex.value = -1
  levelForm.levelName = ''
  levelForm.authLevel = ''
  levelForm.maxAuthCount = 100
  levelForm.price = 0
  levelForm.discount = 100
  levelForm.description = ''
  dialogVisible.value = true
}

const handleEditLevel = (row: LevelAuth, index: number) => {
  isEdit.value = true
  editIndex.value = index
  levelForm.levelName = row.levelName
  levelForm.authLevel = row.authLevel
  levelForm.maxAuthCount = row.maxAuthCount
  levelForm.price = row.price
  levelForm.discount = row.discount
  levelForm.description = row.description
  dialogVisible.value = true
}

const handleDeleteLevel = (index: number) => {
  ElMessageBox.confirm('确定要删除该等级配置吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    levelAuthList.value.splice(index, 1)
    ElMessage.success('删除成功')
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (valid) {
      if (isEdit.value && editIndex.value >= 0) {
        levelAuthList.value[editIndex.value] = { ...levelForm }
        ElMessage.success('编辑成功')
      } else {
        levelAuthList.value.push({ ...levelForm })
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
    }
  })
}

const handleSave = () => {
  ElMessage.success('保存成功')
}
</script>

<style scoped>
.settings-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-text {
  font-weight: bold;
  color: #f56c6c;
}

.discount-text {
  font-weight: bold;
  color: #67c23a;
}

.purchase-price {
  font-weight: bold;
  color: #e6a23c;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
