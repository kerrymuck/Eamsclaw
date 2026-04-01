<template>
  <div class="shop-page">
    <el-row :gutter="16">
      <!-- 店铺信息 -->
      <el-col :xs="24" :sm="24" :md="8" :lg="6">
        <el-card class="shop-info-card">
          <div class="shop-header">
            <el-avatar :size="80" :src="shopInfo.logo" />
            <h3>{{ shopInfo.name }}</h3>
            <el-tag :type="shopInfo.status === 'active' ? 'success' : 'info'">
              {{ shopInfo.status === 'active' ? '营业中' : '已关闭' }}
            </el-tag>
          </div>
          
          <el-descriptions :column="1" size="small" class="shop-details">
            <el-descriptions-item label="店铺ID">{{ shopInfo.id }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ shopInfo.createdAt }}</el-descriptions-item>
            <el-descriptions-item label="主营类目">{{ shopInfo.category }}</el-descriptions-item>
            <el-descriptions-item label="客服在线">{{ shopInfo.onlineStaff }}人</el-descriptions-item>
          </el-descriptions>
          
          <div class="shop-actions">
            <el-button type="primary" @click="editShop">编辑信息</el-button>
            <el-button @click="toggleStatus">
              {{ shopInfo.status === 'active' ? '暂停营业' : '恢复营业' }}
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 平台接入 -->
      <el-col :xs="24" :sm="24" :md="16" :lg="18">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>平台接入</span>
              <el-button type="primary" :icon="Plus" @click="addPlatform">添加平台</el-button>
            </div>
          </template>
          
          <el-row :gutter="16">
            <el-col :xs="24" :sm="12" :md="8" v-for="platform in platforms" :key="platform.id">
              <div class="platform-card" :class="platform.status">
                <div class="platform-header">
                  <div class="platform-icon" :style="{ background: platform.color }">
                    <el-icon :size="28"><component :is="platform.icon" /></el-icon>
                  </div>
                  <div class="platform-info">
                    <h4>{{ platform.name }}</h4>
                    <el-tag :type="platform.status === 'connected' ? 'success' : 'warning'" size="small">
                      {{ platform.status === 'connected' ? '已连接' : '未连接' }}
                    </el-tag>
                  </div>
                </div>
                <div class="platform-stats">
                  <div class="stat-item">
                    <div class="stat-value">{{ platform.todaySessions }}</div>
                    <div class="stat-label">今日会话</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">{{ platform.unreadCount }}</div>
                    <div class="stat-label">未读消息</div>
                  </div>
                </div>
                <div class="platform-actions">
                  <el-button 
                    v-if="platform.status === 'connected'" 
                    type="danger" 
                    link 
                    @click="disconnectPlatform(platform)"
                  >
                    断开连接
                  </el-button>
                  <el-button v-else type="primary" link @click="connectPlatform(platform)">
                    立即连接
                  </el-button>
                  <el-button link @click="configPlatform(platform)">配置</el-button>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 营业时间设置 -->
        <el-card style="margin-top: 16px;">
          <template #header>
            <div class="card-header">
              <span>营业时间设置</span>
              <el-switch v-model="autoReplyEnabled" active-text="自动回复" />
            </div>
          </template>
          
          <el-form :model="businessHours" label-width="100px">
            <el-form-item label="工作日">
              <el-time-picker
                v-model="businessHours.weekdayStart"
                placeholder="开始时间"
                format="HH:mm"
              />
              <span style="margin: 0 8px;">至</span>
              <el-time-picker
                v-model="businessHours.weekdayEnd"
                placeholder="结束时间"
                format="HH:mm"
              />
            </el-form-item>
            <el-form-item label="周末">
              <el-time-picker
                v-model="businessHours.weekendStart"
                placeholder="开始时间"
                format="HH:mm"
              />
              <span style="margin: 0 8px;">至</span>
              <el-time-picker
                v-model="businessHours.weekendEnd"
                placeholder="结束时间"
                format="HH:mm"
              />
            </el-form-item>
            <el-form-item label="非营业时间">
              <el-input
                v-model="businessHours.autoReply"
                type="textarea"
                :rows="2"
                placeholder="设置非营业时间自动回复内容"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑店铺弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑店铺信息" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="店铺名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="店铺Logo">
          <el-upload
            class="avatar-uploader"
            action="#"
            :show-file-list="false"
            :auto-upload="false"
          >
            <el-avatar v-if="editForm.logo" :size="80" :src="editForm.logo" />
            <el-icon v-else :size="28"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="主营类目">
          <el-select v-model="editForm.category" style="width: 100%;">
            <el-option label="数码家电" value="digital" />
            <el-option label="服装鞋包" value="clothing" />
            <el-option label="美妆护肤" value="beauty" />
            <el-option label="食品生鲜" value="food" />
            <el-option label="家居日用" value="home" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveShop">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus, Shop, Goods, Box } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const shopInfo = ref({
  id: 'SHOP001',
  name: '官方旗舰店',
  logo: '',
  status: 'active',
  createdAt: '2024-01-15',
  category: '数码家电',
  onlineStaff: 5
})

const platforms = ref([
  {
    id: 1,
    name: '淘宝',
    icon: 'Shop',
    color: '#ff5000',
    status: 'connected',
    todaySessions: 45,
    unreadCount: 3
  },
  {
    id: 2,
    name: '京东',
    icon: 'Goods',
    color: '#e4393c',
    status: 'connected',
    todaySessions: 32,
    unreadCount: 0
  },
  {
    id: 3,
    name: '拼多多',
    icon: 'Box',
    color: '#e02e24',
    status: 'disconnected',
    todaySessions: 0,
    unreadCount: 0
  }
])

const autoReplyEnabled = ref(true)
const businessHours = ref({
  weekdayStart: new Date(2024, 0, 1, 9, 0),
  weekdayEnd: new Date(2024, 0, 1, 22, 0),
  weekendStart: new Date(2024, 0, 1, 10, 0),
  weekendEnd: new Date(2024, 0, 1, 21, 0),
  autoReply: '您好，当前为非营业时间，您的留言将在上班后第一时间处理，感谢您的理解！'
})

const showEditDialog = ref(false)
const editForm = ref({ ...shopInfo.value })

const editShop = () => {
  editForm.value = { ...shopInfo.value }
  showEditDialog.value = true
}

const saveShop = () => {
  shopInfo.value = { ...editForm.value }
  showEditDialog.value = false
  ElMessage.success('保存成功')
}

const toggleStatus = () => {
  const newStatus = shopInfo.value.status === 'active' ? 'inactive' : 'active'
  ElMessageBox.confirm(
    `确定要${newStatus === 'active' ? '恢复营业' : '暂停营业'}吗？`,
    '提示',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(() => {
    shopInfo.value.status = newStatus
    ElMessage.success('操作成功')
  })
}

const addPlatform = () => {
  ElMessage.info('添加平台功能开发中')
}

const connectPlatform = (platform: any) => {
  ElMessage.success(`${platform.name}连接成功`)
  platform.status = 'connected'
}

const disconnectPlatform = (platform: any) => {
  ElMessageBox.confirm(`确定要断开${platform.name}的连接吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    platform.status = 'disconnected'
    ElMessage.success('已断开连接')
  })
}

const configPlatform = (platform: any) => {
  ElMessage.info(`${platform.name}配置功能开发中`)
}
</script>

<style scoped>
.shop-page {
  padding: 0;
}

.shop-info-card {
  text-align: center;
}

.shop-header {
  margin-bottom: 24px;
}

.shop-header h3 {
  margin: 12px 0;
  font-size: 18px;
}

.shop-details {
  text-align: left;
  margin: 24px 0;
}

.shop-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.platform-card {
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.3s;
}

.platform-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.platform-card.disconnected {
  opacity: 0.6;
}

.platform-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.platform-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.platform-info h4 {
  margin: 0 0 4px;
  font-size: 16px;
}

.platform-stats {
  display: flex;
  gap: 24px;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 12px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.stat-label {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.platform-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-uploader:hover {
  border-color: #1677ff;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .shop-info-card {
    margin-bottom: 16px;
  }
  
  .platform-stats {
    gap: 16px;
  }
}
</style>
