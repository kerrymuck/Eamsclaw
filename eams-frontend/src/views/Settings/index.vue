<template>
  <div class="settings">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- AI设置 -->
      <el-tab-pane label="AI配置" name="ai">
        <el-form :model="aiForm" label-width="120px" style="max-width: 600px">
          <el-form-item label="AI模型">
            <el-select v-model="aiForm.model">
              <el-option label="GPT-4" value="gpt-4" />
              <el-option label="GPT-3.5" value="gpt-3.5-turbo" />
              <el-option label="Claude" value="claude" />
            </el-select>
          </el-form-item>
          <el-form-item label="温度">
            <el-slider v-model="aiForm.temperature" :min="0" :max="1" :step="0.1" show-stops />
          </el-form-item>
          <el-form-item label="最大回复长度">
            <el-input-number v-model="aiForm.max_tokens" :min="100" :max="2000" :step="100" />
          </el-form-item>
          <el-form-item label="自动转人工">
            <el-switch v-model="aiForm.auto_handoff" />
          </el-form-item>
          <el-form-item label="转人工阈值">
            <el-input-number v-model="aiForm.handoff_threshold" :min="1" :max="5" />
            <span style="margin-left: 10px; color: #909399">次未解决后转人工</span>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveAI">保存</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <!-- 平台对接 -->
      <el-tab-pane label="平台对接" name="platform">
        <PlatformSettings />
      </el-tab-pane>
      
      <!-- 成员管理 -->
      <el-tab-pane label="成员管理" name="members">
        <div style="margin-bottom: 20px">
          <el-button type="primary" @click="showAddMember = true">邀请成员</el-button>
        </div>
        <el-table :data="members">
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="nickname" label="昵称" />
          <el-table-column prop="role" label="角色">
            <template #default="{ row }">
              <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
                {{ row.role === 'admin' ? '管理员' : '客服' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                {{ row.status === 'active' ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="primary" link @click="editMember(row)">编辑</el-button>
              <el-button type="danger" link @click="removeMember(row)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 邀请成员对话框 -->
    <el-dialog v-model="showAddMember" title="邀请成员" width="400px">
      <el-form :model="memberForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="memberForm.username" placeholder="输入用户名或邮箱" />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="memberForm.role">
            <el-radio label="agent">客服</el-radio>
            <el-radio label="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddMember = false">取消</el-button>
        <el-button type="primary" @click="inviteMember">邀请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllPlatforms } from '@/config/platforms'
import PlatformSettings from './Platform.vue'

const activeTab = ref('ai')

// AI设置
const aiForm = ref({
  model: 'gpt-3.5-turbo',
  temperature: 0.7,
  max_tokens: 500,
  auto_handoff: true,
  handoff_threshold: 3
})

// 成员管理
const members = ref<any[]>([])
const showAddMember = ref(false)
const memberForm = ref({ username: '', role: 'agent' })

const saveAI = () => {
  ElMessage.success('保存成功')
}

const inviteMember = () => {
  ElMessage.success('邀请已发送')
  showAddMember.value = false
  memberForm.value = { username: '', role: 'agent' }
}

const editMember = (row: any) => {
  // TODO: 编辑成员
}

const removeMember = (row: any) => {
  ElMessageBox.confirm('确定要移除该成员吗？', '提示', { type: 'warning' })
    .then(() => {
      ElMessage.success('已移除')
    })
}

onMounted(() => {
  // TODO: 加载设置数据
})
</script>

<style scoped>
.settings {
  padding: 20px;
}

.platform-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
