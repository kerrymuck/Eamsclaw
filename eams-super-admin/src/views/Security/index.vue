<template>
  <div class="security-container">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 防破解 -->
      <el-tab-pane label="防破解" name="anti-crack">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>防破解设置</span>
              <el-button type="primary" @click="handleSaveAntiCrack">保存设置</el-button>
            </div>
          </template>

          <el-form :model="antiCrackForm" label-width="180px">
            <h4>基础防护</h4>
            <el-form-item label="启用代码混淆">
              <el-switch v-model="antiCrackForm.enableObfuscation" />
              <span class="form-tip">对前端代码进行混淆，增加逆向难度</span>
            </el-form-item>
            <el-form-item label="启用防调试">
              <el-switch v-model="antiCrackForm.enableAntiDebug" />
              <span class="form-tip">检测开发者工具，发现调试行为自动阻断</span>
            </el-form-item>
            <el-form-item label="启用签名验证">
              <el-switch v-model="antiCrackForm.enableSignature" />
              <span class="form-tip">所有API请求需要携带有效签名</span>
            </el-form-item>

            <el-divider />

            <h4>高级防护</h4>
            <el-form-item label="设备指纹绑定">
              <el-switch v-model="antiCrackForm.enableDeviceBind" />
              <span class="form-tip">授权码与设备指纹绑定，防止非法复制</span>
            </el-form-item>
            <el-form-item label="异地登录检测">
              <el-switch v-model="antiCrackForm.enableLocationCheck" />
              <span class="form-tip">检测异常登录地点，触发二次验证</span>
            </el-form-item>
            <el-form-item label="并发连接限制">
              <el-input-number v-model="antiCrackForm.maxConnections" :min="1" :max="100" />
              <span class="form-tip">单个授权码最大并发连接数</span>
            </el-form-item>

            <el-divider />

            <h4>风险阈值设置</h4>
            <el-form-item label="异常请求阈值">
              <el-input-number v-model="antiCrackForm.abnormalRequestThreshold" :min="10" :max="1000" />
              <span class="form-tip">每分钟请求数超过阈值视为异常</span>
            </el-form-item>
            <el-form-item label="IP切换检测">
              <el-switch v-model="antiCrackForm.enableIpCheck" />
              <span class="form-tip">检测短时间内IP频繁切换</span>
            </el-form-item>
            <el-form-item label="自动封禁时长(小时)">
              <el-input-number v-model="antiCrackForm.banDuration" :min="1" :max="168" />
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="risk-log-card">
          <template #header>
            <div class="card-header">
              <span>风险日志</span>
              <el-button type="danger" size="small" @click="handleClearLogs">清空日志</el-button>
            </div>
          </template>
          <el-table :data="riskLogs" stripe>
            <el-table-column prop="time" label="时间" width="180" />
            <el-table-column prop="level" label="级别" width="100">
              <template #default="{ row }">
                <el-tag :type="row.level === 'high' ? 'danger' : row.level === 'medium' ? 'warning' : 'info'">
                  {{ row.level === 'high' ? '高危' : row.level === 'medium' ? '中危' : '低危' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="150" />
            <el-table-column prop="ip" label="IP地址" width="150" />
            <el-table-column prop="license" label="授权码" width="200" />
            <el-table-column prop="description" label="描述" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleViewDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 加密管理 -->
      <el-tab-pane label="加密管理" name="encryption">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>加密密钥管理</span>
              <el-button type="primary" @click="handleGenerateKey">生成新密钥</el-button>
            </div>
          </template>

          <el-alert
            title="密钥用于系统核心数据的加密，请妥善保管"
            type="warning"
            :closable="false"
            style="margin-bottom: 20px;"
          />

          <el-table :data="keyList" stripe>
            <el-table-column prop="name" label="密钥名称" min-width="150" />
            <el-table-column prop="type" label="类型" min-width="100">
              <template #default="{ row }">
                <el-tag>{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="algorithm" label="算法" min-width="100" />
            <el-table-column prop="length" label="密钥长度" min-width="100">
              <template #default="{ row }">
                {{ row.length }} bit
              </template>
            </el-table-column>
            <el-table-column prop="createTime" label="创建时间" min-width="150" />
            <el-table-column prop="status" label="状态" min-width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                  {{ row.status === 'active' ? '使用中' : '已轮换' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleViewKey(row)">查看</el-button>
                <el-button link type="warning" @click="handleRotateKey(row)">轮换</el-button>
                <el-button link type="danger" @click="handleRevokeKey(row)">吊销</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card class="encrypt-config-card">
          <template #header>
            <span>加密配置</span>
          </template>
          <el-form :model="encryptConfig" label-width="180px">
            <el-form-item label="数据库加密">
              <el-switch v-model="encryptConfig.dbEncrypt" />
              <span class="form-tip">对敏感字段进行数据库层加密</span>
            </el-form-item>
            <el-form-item label="传输加密">
              <el-switch v-model="encryptConfig.tlsEncrypt" />
              <span class="form-tip">强制使用TLS 1.3加密传输</span>
            </el-form-item>
            <el-form-item label="静态数据加密">
              <el-switch v-model="encryptConfig.staticEncrypt" />
              <span class="form-tip">对存储的静态文件进行加密</span>
            </el-form-item>
            <el-form-item label="密钥轮换周期(天)">
              <el-input-number v-model="encryptConfig.rotationDays" :min="30" :max="365" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- Ecode设置 -->
      <el-tab-pane label="Ecode设置" name="ecode">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>商户授权码(Ecode)设置</span>
              <el-button type="primary" @click="handleSaveEcode">保存设置</el-button>
            </div>
          </template>

          <el-alert
            title="Ecode是商户授权凭证，用于验证商户身份和权限"
            type="info"
            :closable="false"
            style="margin-bottom: 20px;"
          />

          <el-form :model="ecodeForm" label-width="180px">
            <h4>生成规则</h4>
            <el-form-item label="Ecode长度">
              <el-input-number v-model="ecodeForm.length" :min="16" :max="64" :step="4" />
            </el-form-item>
            <el-form-item label="包含大写字母">
              <el-switch v-model="ecodeForm.includeUpper" />
            </el-form-item>
            <el-form-item label="包含小写字母">
              <el-switch v-model="ecodeForm.includeLower" />
            </el-form-item>
            <el-form-item label="包含数字">
              <el-switch v-model="ecodeForm.includeNumber" />
            </el-form-item>
            <el-form-item label="包含特殊字符">
              <el-switch v-model="ecodeForm.includeSpecial" />
            </el-form-item>
            <el-form-item label="分隔符">
              <el-select v-model="ecodeForm.separator" style="width: 200px">
                <el-option label="无" value="" />
                <el-option label="-" value="-" />
                <el-option label="_" value="_" />
                <el-option label="空格" value=" " />
              </el-select>
            </el-form-item>
            <el-form-item label="分组长度">
              <el-input-number v-model="ecodeForm.groupLength" :min="4" :max="16" :disabled="!ecodeForm.separator" />
            </el-form-item>

            <el-divider />

            <h4>验证规则</h4>
            <el-form-item label="启用签名验证">
              <el-switch v-model="ecodeForm.enableSignature" />
              <span class="form-tip">Ecode包含签名信息，防止伪造</span>
            </el-form-item>
            <el-form-item label="启用有效期">
              <el-switch v-model="ecodeForm.enableExpire" />
            </el-form-item>
            <el-form-item label="默认有效期(天)">
              <el-input-number v-model="ecodeForm.defaultExpireDays" :min="1" :max="3650" :disabled="!ecodeForm.enableExpire" />
            </el-form-item>
            <el-form-item label="允许绑定设备数">
              <el-input-number v-model="ecodeForm.maxDevices" :min="1" :max="100" />
            </el-form-item>

            <el-divider />

            <h4>格式预览</h4>
            <el-form-item label="预览">
              <div class="ecode-preview">
                <code>{{ generatePreview() }}</code>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('anti-crack')

const antiCrackForm = reactive({
  enableObfuscation: true,
  enableAntiDebug: true,
  enableSignature: true,
  enableDeviceBind: true,
  enableLocationCheck: true,
  maxConnections: 10,
  abnormalRequestThreshold: 100,
  enableIpCheck: true,
  banDuration: 24
})

const encryptConfig = reactive({
  dbEncrypt: true,
  tlsEncrypt: true,
  staticEncrypt: true,
  rotationDays: 90
})

const ecodeForm = reactive({
  length: 32,
  includeUpper: true,
  includeLower: true,
  includeNumber: true,
  includeSpecial: false,
  separator: '-',
  groupLength: 8,
  enableSignature: true,
  enableExpire: true,
  defaultExpireDays: 365,
  maxDevices: 5
})

const riskLogs = ref([
  { time: '2026-03-31 14:30:25', level: 'high', type: '调试工具检测', ip: '192.168.1.100', license: 'EAMS-PRO-2026-X8K9M2N4P5', description: '检测到Chrome DevTools开启' },
  { time: '2026-03-31 13:15:10', level: 'medium', type: '异常请求', ip: '192.168.1.101', license: 'EAMS-ENT-2026-Q7W3E4R5T6', description: '1分钟内请求超过500次' },
  { time: '2026-03-31 11:45:33', level: 'low', type: 'IP切换', ip: '192.168.1.102', license: 'EAMS-ULT-2026-Y2U8I9O0P1', description: '1小时内IP切换3次' },
  { time: '2026-03-31 10:20:18', level: 'high', type: '签名验证失败', ip: '192.168.1.103', license: 'EAMS-PRO-2026-A1S2D3F4G5', description: '连续10次签名验证失败' }
])

const keyList = ref([
  { id: '1', name: '主加密密钥', type: 'AES', algorithm: 'AES-256-GCM', length: 256, createTime: '2026-01-15 08:00:00', status: 'active' },
  { id: '2', name: 'API签名密钥', type: 'HMAC', algorithm: 'HMAC-SHA256', length: 256, createTime: '2026-02-01 10:30:00', status: 'active' },
  { id: '3', name: '数据库加密密钥', type: 'AES', algorithm: 'AES-256-CBC', length: 256, createTime: '2025-12-01 09:00:00', status: 'rotated' },
  { id: '4', name: 'JWT签名密钥', type: 'RSA', algorithm: 'RSA-2048', length: 2048, createTime: '2026-03-01 14:00:00', status: 'active' }
])

const handleSaveAntiCrack = () => {
  ElMessage.success('防破解设置已保存')
}

const handleClearLogs = () => {
  ElMessageBox.confirm('确定要清空所有风险日志吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    riskLogs.value = []
    ElMessage.success('日志已清空')
  })
}

const handleViewDetail = (row: any) => {
  ElMessage.info('查看详情: ' + row?.description || '')
}

const handleGenerateKey = () => {
  ElMessage.success('新密钥已生成')
}

const handleViewKey = (_row: any) => {
  ElMessageBox.alert('密钥内容已复制到剪贴板', '查看密钥', {
    confirmButtonText: '确定'
  })
}

const handleRotateKey = (row: any) => {
  ElMessageBox.confirm(`确定要轮换密钥「${row.name}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('密钥轮换成功')
  })
}

const handleRevokeKey = (row: any) => {
  ElMessageBox.confirm(`确定要吊销密钥「${row.name}」吗？此操作不可恢复！`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'error'
  }).then(() => {
    ElMessage.success('密钥已吊销')
  })
}

const handleSaveEcode = () => {
  ElMessage.success('Ecode设置已保存')
}

const generatePreview = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  let result = ''
  for (let i = 0; i < ecodeForm.length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  if (ecodeForm.separator && ecodeForm.groupLength) {
    result = result.match(new RegExp(`.{1,${ecodeForm.groupLength}}`, 'g'))?.join(ecodeForm.separator) || result
  }
  return 'EAMS-' + result
}
</script>

<style scoped>
.security-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.risk-log-card {
  margin-top: 20px;
}

.encrypt-config-card {
  margin-top: 20px;
}

.ecode-preview {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  font-family: monospace;
  font-size: 16px;
}

.ecode-preview code {
  color: #409eff;
  font-weight: bold;
}

h4 {
  margin: 20px 0 15px;
  color: #303133;
}
</style>
