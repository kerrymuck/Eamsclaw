<template>
  <div class="page-container">
    <h3>算力价格体系</h3>
    <p>配置AI算力供货体系，设置不同等级服务商的折扣权益</p>
    
    <!-- 服务商等级折扣体系 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <div>
            <span>服务商等级折扣体系</span>
            <el-tag type="info" style="margin-left: 10px;">算力供货体系</el-tag>
          </div>
          <el-button type="primary" @click="handleAddLevel">
            <el-icon><Plus /></el-icon> 添加等级
          </el-button>
        </div>
      </template>
      
      <el-alert
        title="折扣体系说明"
        description="不同等级的服务商享受不同的算力折扣，高等级服务商可获得更低的算力采购价格"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      />
      
      <el-table :data="levelList" stripe border>
        <el-table-column prop="level" label="等级" width="100" align="center">
          <template #default="{ $index }">
            <el-tag :type="getLevelTagType($index)">Level {{ $index + 1 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="等级名称" min-width="120" />
        <el-table-column prop="discountRate" label="算力折扣" min-width="100" align="center">
          <template #default="{ row }">
            <span class="discount-text">{{ row.discountRate }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="等级说明" min-width="200" />
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row, $index }">
            <el-button link type="primary" @click="handleEditLevel(row, $index)">编辑</el-button>
            <el-button link type="danger" @click="handleDeleteLevel($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 升级设置 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <div>
            <span>升级设置</span>
            <el-tag type="success" style="margin-left: 10px;">自动升级规则</el-tag>
          </div>
          <el-button type="success" @click="handleAddUpgradeRule">
            <el-icon><Plus /></el-icon> 添加升级规则
          </el-button>
        </div>
      </template>
      
      <el-alert
        title="自动升级规则"
        description="按不同服务商等级一次性充值不同金额则自动升级到对应的服务商等级，无需手动操作升级"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px;"
      />
      
      <el-table :data="upgradeRuleList" stripe border>
        <el-table-column prop="fromLevel" label="当前等级" min-width="120">
          <template #default="{ row }">
            {{ getLevelName(row.fromLevel) }}
          </template>
        </el-table-column>
        <el-table-column prop="toLevel" label="目标等级" min-width="120">
          <template #default="{ row }">
            <el-tag type="success">{{ getLevelName(row.toLevel) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="upgradeAmount" label="升级所需充值金额" min-width="150" align="right">
          <template #default="{ row }">
            <span class="amount-text">¥{{ row.upgradeAmount.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="200" />
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row, $index }">
            <el-button link type="primary" @click="handleEditUpgradeRule(row, $index)">编辑</el-button>
            <el-button link type="danger" @click="handleDeleteUpgradeRule($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 模型基础价格 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>模型基础价格配置</span>
          <el-button type="primary" @click="handleSaveAll">保存所有设置</el-button>
        </div>
      </template>
      
      <el-table :data="modelPricingList" stripe border>
        <el-table-column prop="modelName" label="模型名称" min-width="150" />
        <el-table-column prop="costPrice" label="成本价" min-width="120" align="right">
          <template #default="{ row }">
            <span class="cost-price">¥{{ row.costPrice }}/1K tokens</span>
          </template>
        </el-table-column>
        <el-table-column prop="basePrice" label="基础销售价" min-width="150" align="right">
          <template #default="{ row }">
            <el-input-number v-model="row.basePrice" :min="row.costPrice" :precision="4" :step="0.001" style="width: 120px" />
          </template>
        </el-table-column>
        <el-table-column label="各等级实际售价" min-width="400">
          <template #default="{ row }">
            <div class="level-prices">
              <div v-for="(level, idx) in levelList" :key="idx" class="level-price-item">
                <el-tag size="small" :type="getLevelTagType(idx)">{{ level.name }}</el-tag>
                <span class="level-price">¥{{ (row.basePrice * level.discountRate / 100).toFixed(4) }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 等级设置对话框 -->
    <el-dialog v-model="levelDialogVisible" :title="isEditLevel ? '编辑等级' : '添加等级'" width="500px">
      <el-form :model="levelForm" :rules="levelRules" ref="levelFormRef" label-width="120px">
        <el-form-item label="等级名称" prop="name">
          <el-input v-model="levelForm.name" placeholder="如：金牌服务商" />
        </el-form-item>
        <el-form-item label="算力折扣(%)" prop="discountRate">
          <el-input-number v-model="levelForm.discountRate" :min="1" :max="100" style="width: 100%" />
          <span class="form-tip">折扣比例越低，算力采购价格越优惠</span>
        </el-form-item>
        <el-form-item label="等级说明" prop="description">
          <el-input v-model="levelForm.description" type="textarea" rows="2" placeholder="描述该等级的算力权益" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="levelDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitLevel">确定</el-button>
      </template>
    </el-dialog>

    <!-- 升级规则对话框 -->
    <el-dialog v-model="upgradeDialogVisible" :title="isEditUpgrade ? '编辑升级规则' : '添加升级规则'" width="500px">
      <el-form :model="upgradeForm" :rules="upgradeFormRules" ref="upgradeFormRef" label-width="140px">
        <el-form-item label="当前等级" prop="fromLevel">
          <el-select v-model="upgradeForm.fromLevel" style="width: 100%" placeholder="选择当前等级">
            <el-option 
              v-for="(level, index) in levelList" 
              :key="index" 
              :label="level.name" 
              :value="index" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="目标等级" prop="toLevel">
          <el-select v-model="upgradeForm.toLevel" style="width: 100%" placeholder="选择目标等级">
            <el-option 
              v-for="(level, index) in levelList" 
              :key="index" 
              :label="level.name" 
              :value="index"
              :disabled="index <= upgradeForm.fromLevel"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="升级充值金额" prop="upgradeAmount">
          <el-input-number v-model="upgradeForm.upgradeAmount" :min="0" :precision="2" style="width: 100%" />
          <span class="form-tip">一次性充值达到此金额自动升级</span>
        </el-form-item>
        <el-form-item label="说明" prop="description">
          <el-input v-model="upgradeForm.description" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="upgradeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitUpgrade">确定</el-button>
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
  discountRate: number
  description: string
}

interface UpgradeRule {
  fromLevel: number
  toLevel: number
  upgradeAmount: number
  description: string
}

interface ModelPricing {
  modelName: string
  costPrice: number
  basePrice: number
}

// 等级列表
const levelList = ref<Level[]>([
  { name: '普通服务商', discountRate: 100, description: '基础等级，无算力折扣' },
  { name: '铜牌服务商', discountRate: 85, description: '享受8.5折算力优惠' },
  { name: '银牌服务商', discountRate: 75, description: '享受7.5折算力优惠' },
  { name: '金牌服务商', discountRate: 60, description: '享受6折算力优惠' }
])

// 升级规则列表
const upgradeRuleList = ref<UpgradeRule[]>([
  { fromLevel: 0, toLevel: 1, upgradeAmount: 20000, description: '累计充值满2万升级为铜牌' },
  { fromLevel: 0, toLevel: 2, upgradeAmount: 50000, description: '累计充值满5万直接升级为银牌' },
  { fromLevel: 1, toLevel: 2, upgradeAmount: 50000, description: '铜牌累计充值满5万升级为银牌' },
  { fromLevel: 2, toLevel: 3, upgradeAmount: 100000, description: '银牌累计充值满10万升级为金牌' }
])

// 模型基础价格
const modelPricingList = ref<ModelPricing[]>([
  { modelName: 'GPT-4 Turbo', costPrice: 0.04, basePrice: 0.08 },
  { modelName: 'GPT-3.5 Turbo', costPrice: 0.002, basePrice: 0.005 },
  { modelName: 'Claude 3 Opus', costPrice: 0.09, basePrice: 0.18 },
  { modelName: 'Claude 3 Sonnet', costPrice: 0.018, basePrice: 0.036 },
  { modelName: '文心一言4.0', costPrice: 0.024, basePrice: 0.048 },
  { modelName: '通义千问Max', costPrice: 0.04, basePrice: 0.08 },
  { modelName: 'GLM-4', costPrice: 0.02, basePrice: 0.04 },
  { modelName: 'Kimi', costPrice: 0.012, basePrice: 0.024 }
])

// 等级对话框
const levelDialogVisible = ref(false)
const isEditLevel = ref(false)
const editLevelIndex = ref(-1)
const levelFormRef = ref<FormInstance>()

const levelForm = reactive<Level>({
  name: '',
  discountRate: 100,
  description: ''
})

const levelRules: FormRules = {
  name: [{ required: true, message: '请输入等级名称', trigger: 'blur' }],
  discountRate: [{ required: true, message: '请输入折扣比例', trigger: 'blur' }],
  description: [{ required: true, message: '请输入等级说明', trigger: 'blur' }]
}

// 升级规则对话框
const upgradeDialogVisible = ref(false)
const isEditUpgrade = ref(false)
const editUpgradeIndex = ref(-1)
const upgradeFormRef = ref<FormInstance>()

const upgradeForm = reactive<UpgradeRule>({
  fromLevel: 0,
  toLevel: 1,
  upgradeAmount: 0,
  description: ''
})

const upgradeFormRules: FormRules = {
  fromLevel: [{ required: true, message: '请选择当前等级', trigger: 'change' }],
  toLevel: [{ required: true, message: '请选择目标等级', trigger: 'change' }],
  upgradeAmount: [{ required: true, message: '请输入升级金额', trigger: 'blur' }]
}

// 获取等级标签类型
const getLevelTagType = (index: number) => {
  const types = ['info', 'success', 'warning', 'danger']
  return types[index % types.length]
}

// 获取等级名称
const getLevelName = (index: number) => {
  return levelList.value[index]?.name || '未知等级'
}

// 等级操作
const handleAddLevel = () => {
  isEditLevel.value = false
  editLevelIndex.value = -1
  levelForm.name = ''
  levelForm.discountRate = 100
  levelForm.description = ''
  levelDialogVisible.value = true
}

const handleEditLevel = (row: Level, index: number) => {
  isEditLevel.value = true
  editLevelIndex.value = index
  levelForm.name = row.name
  levelForm.discountRate = row.discountRate
  levelForm.description = row.description
  levelDialogVisible.value = true
}

const handleDeleteLevel = (index: number) => {
  ElMessageBox.confirm('确定要删除该等级吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    levelList.value.splice(index, 1)
    ElMessage.success('删除成功')
  })
}

const handleSubmitLevel = async () => {
  if (!levelFormRef.value) return
  
  await levelFormRef.value.validate((valid) => {
    if (valid) {
      if (isEditLevel.value && editLevelIndex.value >= 0) {
        levelList.value[editLevelIndex.value] = { ...levelForm }
        ElMessage.success('编辑成功')
      } else {
        levelList.value.push({ ...levelForm })
        ElMessage.success('添加成功')
      }
      levelDialogVisible.value = false
    }
  })
}

// 升级规则操作
const handleAddUpgradeRule = () => {
  isEditUpgrade.value = false
  editUpgradeIndex.value = -1
  upgradeForm.fromLevel = 0
  upgradeForm.toLevel = 1
  upgradeForm.upgradeAmount = 0
  upgradeForm.description = ''
  upgradeDialogVisible.value = true
}

const handleEditUpgradeRule = (row: UpgradeRule, index: number) => {
  isEditUpgrade.value = true
  editUpgradeIndex.value = index
  upgradeForm.fromLevel = row.fromLevel
  upgradeForm.toLevel = row.toLevel
  upgradeForm.upgradeAmount = row.upgradeAmount
  upgradeForm.description = row.description
  upgradeDialogVisible.value = true
}

const handleDeleteUpgradeRule = (index: number) => {
  ElMessageBox.confirm('确定要删除该升级规则吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    upgradeRuleList.value.splice(index, 1)
    ElMessage.success('删除成功')
  })
}

const handleSubmitUpgrade = async () => {
  if (!upgradeFormRef.value) return
  
  await upgradeFormRef.value.validate((valid) => {
    if (valid) {
      if (upgradeForm.fromLevel >= upgradeForm.toLevel) {
        ElMessage.error('目标等级必须高于当前等级')
        return
      }
      
      if (isEditUpgrade.value && editUpgradeIndex.value >= 0) {
        upgradeRuleList.value[editUpgradeIndex.value] = { ...upgradeForm }
        ElMessage.success('编辑成功')
      } else {
        upgradeRuleList.value.push({ ...upgradeForm })
        ElMessage.success('添加成功')
      }
      upgradeDialogVisible.value = false
    }
  })
}

const handleSaveAll = () => {
  ElMessage.success('所有设置已保存')
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

.discount-text {
  font-weight: bold;
  color: #f56c6c;
}

.amount-text {
  font-weight: bold;
  color: #67c23a;
}

.cost-price {
  color: #909399;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.level-prices {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.level-price-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.level-price {
  font-weight: bold;
  color: #409eff;
  font-size: 13px;
}
</style>
