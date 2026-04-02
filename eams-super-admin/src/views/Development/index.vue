<template>
  <div class="dev-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>平台列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 新增平台
          </el-button>
        </div>
      </template>

      <el-table :data="platformList" stripe>
        <el-table-column type="index" width="50" />
        <el-table-column prop="name" label="平台名称" min-width="120">
          <template #default="{ row }">
            <div class="platform-info">
              <span class="platform-icon">{{ row.icon }}</span>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="平台代码" min-width="100" />
        <el-table-column prop="type" label="平台类型" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeType(row.type)">{{ getTypeText(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="apiVersion" label="API版本" min-width="100" />
        <el-table-column prop="authType" label="认证方式" min-width="120" />
        <el-table-column prop="status" label="状态" min-width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '已启用' : '未启用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="shopCount" label="接入店铺" min-width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleConfig(row)">配置</el-button>
            <el-button link :type="row.status === 'active' ? 'danger' : 'success'" @click="handleToggle(row)">
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogType === 'add' ? '新增平台' : '编辑平台'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="平台名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="平台代码" prop="code">
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="平台图标" prop="icon">
          <el-input v-model="form.icon" placeholder="输入emoji或图标URL" />
        </el-form-item>
        <el-form-item label="平台类型" prop="type">
          <el-select v-model="form.type" style="width: 100%">
            <el-option label="国内电商" value="domestic" />
            <el-option label="跨境电商" value="crossborder" />
            <el-option label="B2B平台" value="b2b" />
            <el-option label="独立站" value="independent" />
          </el-select>
        </el-form-item>
        <el-form-item label="API版本">
          <el-input v-model="form.apiVersion" />
        </el-form-item>
        <el-form-item label="认证方式">
          <el-select v-model="form.authType" style="width: 100%">
            <el-option label="OAuth2.0" value="oauth2" />
            <el-option label="API Key" value="apikey" />
            <el-option label="HMAC签名" value="hmac" />
          </el-select>
        </el-form-item>
        <el-form-item label="API文档地址">
          <el-input v-model="form.docUrl" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 配置对话框 -->
    <el-dialog v-model="configVisible" title="平台配置" width="700px">
      <el-tabs v-model="configTab">
        <el-tab-pane label="基础配置" name="basic">
          <el-form :model="configForm" label-width="150px">
            <el-form-item label="AppKey">
              <el-input v-model="configForm.appKey" />
            </el-form-item>
            <el-form-item label="AppSecret">
              <el-input v-model="configForm.appSecret" type="password" show-password />
            </el-form-item>
            <el-form-item label="API基础地址">
              <el-input v-model="configForm.baseUrl" />
            </el-form-item>
            <el-form-item label="授权回调地址">
              <el-input v-model="configForm.callbackUrl" />
            </el-form-item>
            <el-form-item label="Webhook密钥">
              <el-input v-model="configForm.webhookSecret" type="password" show-password />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="消息配置" name="message">
          <el-form :model="configForm" label-width="150px">
            <el-form-item label="消息接收URL">
              <el-input v-model="configForm.messageUrl" />
            </el-form-item>
            <el-form-item label="消息加密方式">
              <el-radio-group v-model="configForm.encryptType">
                <el-radio label="none">不加密</el-radio>
                <el-radio label="aes">AES加密</el-radio>
                <el-radio label="rsa">RSA加密</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="消息格式">
              <el-radio-group v-model="configForm.messageFormat">
                <el-radio label="json">JSON</el-radio>
                <el-radio label="xml">XML</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="限流配置" name="rate">
          <el-form :model="configForm" label-width="150px">
            <el-form-item label="QPS限制">
              <el-input-number v-model="configForm.qps" :min="1" :max="1000" />
            </el-form-item>
            <el-form-item label="日调用上限">
              <el-input-number v-model="configForm.dailyLimit" :min="1000" :max="10000000" :step="1000" />
            </el-form-item>
            <el-form-item label="并发连接数">
              <el-input-number v-model="configForm.concurrency" :min="1" :max="100" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="configVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfigSubmit">保存配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const dialogVisible = ref(false)
const configVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const configTab = ref('basic')

const form = reactive({
  id: '',
  name: '',
  code: '',
  icon: '',
  type: 'domestic',
  apiVersion: '',
  authType: 'oauth2',
  docUrl: '',
  description: ''
})

const configForm = reactive({
  appKey: '',
  appSecret: '',
  baseUrl: '',
  callbackUrl: '',
  webhookSecret: '',
  messageUrl: '',
  encryptType: 'aes',
  messageFormat: 'json',
  qps: 100,
  dailyLimit: 100000,
  concurrency: 10
})

const rules = {
  name: [{ required: true, message: '请输入平台名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入平台代码', trigger: 'blur' }],
  type: [{ required: true, message: '请选择平台类型', trigger: 'change' }]
}

const platformList = ref([
  { id: '1', name: '淘宝', code: 'taobao', icon: '🍑', type: 'domestic', apiVersion: 'v2.0', authType: 'OAuth2.0', status: 'active', shopCount: 1256 },
  { id: '2', name: '京东', code: 'jd', icon: '🐕', type: 'domestic', apiVersion: 'v1.0', authType: 'HMAC签名', status: 'active', shopCount: 892 },
  { id: '3', name: '拼多多', code: 'pdd', icon: '🟥', type: 'domestic', apiVersion: 'v3.0', authType: 'MD5签名', status: 'active', shopCount: 2341 },
  { id: '4', name: '抖店', code: 'douyin', icon: '🎵', type: 'domestic', apiVersion: 'v1.0', authType: 'OAuth2.0', status: 'active', shopCount: 567 },
  { id: '5', name: 'Amazon', code: 'amazon', icon: '🅰️', type: 'crossborder', apiVersion: 'v2024', authType: 'OAuth2.0', status: 'active', shopCount: 423 },
  { id: '6', name: 'Shopee', code: 'shopee', icon: '🧡', type: 'crossborder', apiVersion: 'v2.0', authType: 'API Key', status: 'active', shopCount: 312 },
  { id: '7', name: 'Shopify', code: 'shopify', icon: '🛍️', type: 'independent', apiVersion: 'v2024-01', authType: 'API Key', status: 'active', shopCount: 189 }
])

const getTypeType = (type: string) => {
  const map: Record<string, string> = {
    domestic: 'success',
    crossborder: 'warning',
    b2b: 'info',
    independent: ''
  }
  return map[type] || ''
}

const getTypeText = (type: string) => {
  const map: Record<string, string> = {
    domestic: '国内电商',
    crossborder: '跨境电商',
    b2b: 'B2B平台',
    independent: '独立站'
  }
  return map[type] || type
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

const handleConfig = (_row: any) => {
  configVisible.value = true
}

const handleToggle = (row: any) => {
  const action = row.status === 'active' ? '禁用' : '启用'
  ElMessageBox.confirm(`确定要${action}该平台吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    row.status = row.status === 'active' ? 'inactive' : 'active'
    ElMessage.success(`${action}成功`)
  })
}

const handleSubmit = () => {
  ElMessage.success(dialogType.value === 'add' ? '新增成功' : '编辑成功')
  dialogVisible.value = false
}

const handleConfigSubmit = () => {
  ElMessage.success('配置保存成功')
  configVisible.value = false
}
</script>

<style scoped>
.dev-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.platform-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.platform-icon {
  font-size: 20px;
}
</style>
