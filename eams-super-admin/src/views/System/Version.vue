<template>
  <div class="version-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h3>版本管理</h3>
        <span class="sub-title">管理商户端版本更新</span>
      </div>
      <el-button type="primary" :icon="Plus" @click="openAddDialog">
        发布新版本
      </el-button>
    </div>

    <!-- 当前版本信息 -->
    <el-card class="current-version-card">
      <template #header>
        <div class="card-header">
          <span>当前最新版本</span>
          <el-tag type="success" effect="dark">已发布</el-tag>
        </div>
      </template>
      <div class="version-info" v-if="latestVersion">
        <div class="version-number">v{{ latestVersion.version }}</div>
        <div class="version-detail">
          <p><strong>更新说明：</strong>{{ latestVersion.description }}</p>
          <p><strong>文件大小：</strong>{{ latestVersion.fileSize }}</p>
          <p><strong>发布时间：</strong>{{ latestVersion.publishTime }}</p>
          <p><strong>强制更新：</strong>{{ latestVersion.forceUpdate ? '是' : '否' }}</p>
        </div>
      </div>
      <el-empty v-else description="暂无已发布版本" />
    </el-card>

    <!-- 版本历史列表 -->
    <el-card class="version-list-card">
      <template #header>
        <div class="card-header">
          <span>版本历史</span>
        </div>
      </template>
      
      <el-table :data="versionList" style="width: 100%" v-loading="loading">
        <el-table-column prop="version" label="版本号" width="120">
          <template #default="{ row }">
            <el-tag :type="row.isLatest ? 'success' : ''">v{{ row.version }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="更新说明" show-overflow-tooltip />
        <el-table-column prop="fileSize" label="文件大小" width="100" />
        <el-table-column prop="forceUpdate" label="强制更新" width="100">
          <template #default="{ row }">
            <el-tag :type="row.forceUpdate ? 'danger' : 'info'" size="small">
              {{ row.forceUpdate ? '强制' : '可选' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publishTime" label="发布时间" width="180" />
        <el-table-column prop="downloadCount" label="下载次数" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button link type="primary" @click="downloadFile(row)">下载</el-button>
            <el-button link type="danger" @click="deleteVersion(row)" :disabled="row.isLatest">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 发布新版本弹窗 -->
    <el-dialog 
      v-model="showDialog" 
      title="发布新版本" 
      width="600px"
      destroy-on-close
    >
      <el-form 
        ref="formRef"
        :model="form" 
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="版本号" prop="version">
          <el-input v-model="form.version" placeholder="例如: 1.2.3" />
          <div class="form-tip">版本号格式: 主版本.次版本.修订号</div>
        </el-form-item>

        <el-form-item label="更新文件" prop="file">
          <el-upload
            ref="uploadRef"
            class="version-uploader"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :limit="1"
            accept=".zip,.exe,.dmg,.apk,.ipa"
          >
            <el-icon class="el-icon--upload"><Upload /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持格式: .zip, .exe, .dmg, .apk, .ipa，文件大小不超过 500MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item label="更新说明" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="4"
            placeholder="请输入本次更新的详细说明..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="强制更新">
          <el-switch
            v-model="form.forceUpdate"
            active-text="是"
            inactive-text="否"
          />
          <div class="form-tip">开启后，商户端必须更新才能继续使用</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="publishVersion" :loading="publishing">
          发布
        </el-button>
      </template>
    </el-dialog>

    <!-- 版本详情弹窗 -->
    <el-dialog v-model="showDetailDialog" title="版本详情" width="500px">
      <el-descriptions :column="1" border v-if="selectedVersion">
        <el-descriptions-item label="版本号">v{{ selectedVersion.version }}</el-descriptions-item>
        <el-descriptions-item label="更新说明">{{ selectedVersion.description }}</el-descriptions-item>
        <el-descriptions-item label="文件大小">{{ selectedVersion.fileSize }}</el-descriptions-item>
        <el-descriptions-item label="文件名称">{{ selectedVersion.fileName }}</el-descriptions-item>
        <el-descriptions-item label="强制更新">
          <el-tag :type="selectedVersion.forceUpdate ? 'danger' : 'info'">
            {{ selectedVersion.forceUpdate ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发布时间">{{ selectedVersion.publishTime }}</el-descriptions-item>
        <el-descriptions-item label="下载次数">{{ selectedVersion.downloadCount }}</el-descriptions-item>
        <el-descriptions-item label="下载地址">
          <el-link type="primary" :href="selectedVersion.downloadUrl" target="_blank">
            {{ selectedVersion.downloadUrl }}
          </el-link>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules, UploadFile, UploadInstance } from 'element-plus'

// 版本数据类型
interface VersionItem {
  id: string
  version: string
  description: string
  fileName: string
  fileSize: string
  filePath: string
  downloadUrl: string
  forceUpdate: boolean
  publishTime: string
  downloadCount: number
  isLatest: boolean
}

// 表单数据类型
interface VersionForm {
  version: string
  description: string
  file: File | null
  forceUpdate: boolean
}

// 加载状态
const loading = ref(false)
const publishing = ref(false)

// 版本列表
const versionList = ref<VersionItem[]>([
  {
    id: 'v1.2.3',
    version: '1.2.3',
    description: '修复已知问题，优化性能，新增店铺管理功能',
    fileName: 'eams-merchant-v1.2.3.zip',
    fileSize: '45.2 MB',
    filePath: '/uploads/versions/v1.2.3.zip',
    downloadUrl: 'https://your-domain.com/downloads/v1.2.3.zip',
    forceUpdate: false,
    publishTime: '2026-04-10 10:00:00',
    downloadCount: 128,
    isLatest: true
  },
  {
    id: 'v1.2.2',
    version: '1.2.2',
    description: '修复消息推送问题',
    fileName: 'eams-merchant-v1.2.2.zip',
    fileSize: '43.8 MB',
    filePath: '/uploads/versions/v1.2.2.zip',
    downloadUrl: 'https://your-domain.com/downloads/v1.2.2.zip',
    forceUpdate: false,
    publishTime: '2026-04-05 15:30:00',
    downloadCount: 356,
    isLatest: false
  },
  {
    id: 'v1.2.1',
    version: '1.2.1',
    description: '紧急修复安全漏洞',
    fileName: 'eams-merchant-v1.2.1.zip',
    fileSize: '43.5 MB',
    filePath: '/uploads/versions/v1.2.1.zip',
    downloadUrl: 'https://your-domain.com/downloads/v1.2.1.zip',
    forceUpdate: true,
    publishTime: '2026-04-01 09:00:00',
    downloadCount: 512,
    isLatest: false
  }
])

// 最新版本
const latestVersion = computed(() => {
  return versionList.value.find(v => v.isLatest) || null
})

// 弹窗相关
const showDialog = ref(false)
const showDetailDialog = ref(false)
const selectedVersion = ref<VersionItem | null>(null)
const formRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()

// 表单数据
const form = reactive<VersionForm>({
  version: '',
  description: '',
  file: null,
  forceUpdate: false
})

// 表单验证规则
const formRules: FormRules = {
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' },
    { pattern: /^\d+\.\d+\.\d+$/, message: '版本号格式错误，例如: 1.2.3', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入更新说明', trigger: 'blur' },
    { min: 10, max: 500, message: '长度在 10 到 500 个字符', trigger: 'blur' }
  ],
  file: [
    { required: true, message: '请上传更新文件', trigger: 'change' }
  ]
}

// 打开添加弹窗
const openAddDialog = () => {
  form.version = ''
  form.description = ''
  form.file = null
  form.forceUpdate = false
  showDialog.value = true
}

// 处理文件选择
const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    form.file = file.raw
  }
}

// 处理文件移除
const handleFileRemove = () => {
  form.file = null
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 发布版本
const publishVersion = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (!valid) return
    
    if (!form.file) {
      ElMessage.error('请上传更新文件')
      return
    }
    
    publishing.value = true
    
    // 模拟API调用和文件上传
    setTimeout(() => {
      const newVersion: VersionItem = {
        id: `v${form.version}`,
        version: form.version,
        description: form.description,
        fileName: form.file?.name || 'unknown',
        fileSize: formatFileSize(form.file?.size || 0),
        filePath: `/uploads/versions/v${form.version}.zip`,
        downloadUrl: `https://your-domain.com/downloads/v${form.version}.zip`,
        forceUpdate: form.forceUpdate,
        publishTime: new Date().toLocaleString('zh-CN'),
        downloadCount: 0,
        isLatest: true
      }
      
      // 将之前的最新版本标记为非最新
      versionList.value.forEach(v => v.isLatest = false)
      
      // 添加到列表顶部
      versionList.value.unshift(newVersion)
      
      ElMessage.success('新版本发布成功')
      publishing.value = false
      showDialog.value = false
      
      // 清空上传组件
      uploadRef.value?.clearFiles()
    }, 2000)
  })
}

// 查看详情
const viewDetail = (version: VersionItem) => {
  selectedVersion.value = version
  showDetailDialog.value = true
}

// 下载文件
const downloadFile = (version: VersionItem) => {
  // 模拟下载
  version.downloadCount++
  ElMessage.success(`开始下载 ${version.fileName}`)
  // window.open(version.downloadUrl, '_blank')
}

// 删除版本
const deleteVersion = (version: VersionItem) => {
  ElMessageBox.confirm(
    `确定要删除版本 v${version.version} 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = versionList.value.findIndex(v => v.id === version.id)
    if (index > -1) {
      versionList.value.splice(index, 1)
      ElMessage.success('版本已删除')
    }
  })
}

// 初始化
onMounted(() => {
  // 这里可以调用API获取版本列表
})
</script>

<style scoped>
.version-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.header-left h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.sub-title {
  color: #909399;
  font-size: 14px;
}

.current-version-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.version-info {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

.version-number {
  font-size: 48px;
  font-weight: 700;
  color: #1677ff;
  line-height: 1;
}

.version-detail {
  flex: 1;
}

.version-detail p {
  margin: 8px 0;
  color: #606266;
}

.version-list-card {
  margin-bottom: 24px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.version-uploader {
  width: 100%;
}

:deep(.version-uploader .el-upload) {
  width: 100%;
}

:deep(.version-uploader .el-upload-dragger) {
  width: 100%;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .version-info {
    flex-direction: column;
    gap: 16px;
  }
  
  .version-number {
    font-size: 36px;
  }
}
</style>
