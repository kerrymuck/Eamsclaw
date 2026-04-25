<template>
  <el-container class="layout-container">
    <!-- 移动端遮罩层 -->
    <div 
      v-if="isMobile && !isCollapse" 
      class="mobile-mask"
      @click="isCollapse = true"
    ></div>
    
    <!-- 侧边栏 -->
    <el-aside 
      :width="isCollapse ? '64px' : '200px'"
      :class="['sidebar', { 'mobile-sidebar': isMobile, 'collapsed': isCollapse }]"
    >
      <div class="logo">
        <h3 v-if="!isCollapse">EAMSCLAW</h3>
        <span v-else class="logo-icon">🐱</span>
      </div>
      
      <el-menu
        :default-active="$route.path"
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        
        <!-- 智能体管理 -->
        <el-sub-menu index="/agent">
          <template #title>
            <el-icon><MessageBox /></el-icon>
            <span>智能体管理</span>
          </template>
          <el-menu-item index="/agent/workspace">
            <el-icon><Monitor /></el-icon>
            <template #title>工作台管理</template>
          </el-menu-item>
          <el-menu-item index="/agent/settings">
            <el-icon><SetUp /></el-icon>
            <template #title>智能体设置</template>
          </el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/knowledge">
          <el-icon><Collection /></el-icon>
          <template #title>知识库</template>
        </el-menu-item>
        
        <el-menu-item index="/tickets">
          <el-icon><Tickets /></el-icon>
          <template #title>工单流转</template>
        </el-menu-item>
        
        <el-menu-item index="/performance">
          <el-icon><TrendCharts /></el-icon>
          <template #title>绩效管理</template>
        </el-menu-item>
        
        <el-menu-item index="/shops">
          <el-icon><Shop /></el-icon>
          <template #title>店铺管理</template>
        </el-menu-item>
        
        <el-menu-item index="/orders">
          <el-icon><Box /></el-icon>
          <template #title>订单管理</template>
        </el-menu-item>
        
        <el-menu-item index="/ai-power">
          <el-icon><Lightning /></el-icon>
          <template #title>AI算力中心</template>
        </el-menu-item>
        
        <el-menu-item index="/plan">
          <el-icon><Wallet /></el-icon>
          <template #title>套餐订阅</template>
        </el-menu-item>
        
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- 主内容 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-button
            class="collapse-btn"
            :icon="isCollapse ? Expand : Fold"
            @click="toggleSidebar"
          />
          <h3 class="page-title">{{ $route.meta.title || 'EAMSCLAW' }}</h3>
        </div>
        <div class="header-right">
          <!-- 我的服务商 -->
          <el-popover
            placement="bottom"
            :width="280"
            trigger="hover"
          >
            <template #reference>
              <div class="provider-info">
                <el-tag type="primary" size="small" class="provider-label">我的服务商</el-tag>
                <el-icon :size="18" color="#409EFF"><OfficeBuilding /></el-icon>
                <span class="provider-name">{{ providerInfo.name }}</span>
                <el-icon :size="12"><ArrowDown /></el-icon>
              </div>
            </template>
            <div class="provider-detail">
              <h4>{{ providerInfo.name }}</h4>
              <div class="detail-item">
                <span class="label">联系人：</span>
                <span>{{ providerInfo.contactName }}</span>
              </div>
              <div class="detail-item">
                <span class="label">联系电话：</span>
                <span>{{ providerInfo.contactPhone }}</span>
              </div>
              <div class="detail-item">
                <span class="label">服务邮箱：</span>
                <span>{{ providerInfo.email }}</span>
              </div>
              <div class="detail-item">
                <span class="label">服务商等级：</span>
                <el-tag :type="providerInfo.levelType" size="small">{{ providerInfo.level }}</el-tag>
              </div>
            </div>
          </el-popover>
          
          <el-divider direction="vertical" />
          
          <el-dropdown trigger="click">
            <span class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ userStore.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="showAccountDialog = true">
                  <el-icon><User /></el-icon> 账号管理
                </el-dropdown-item>
                <el-dropdown-item divided @click="logout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
    
    <!-- 账号管理弹窗 -->
    <el-dialog
      v-model="showAccountDialog"
      title="账号管理"
      width="600px"
      destroy-on-close
    >
      <el-tabs v-model="accountActiveTab" class="account-tabs">
        <!-- 基础资料 -->
        <el-tab-pane label="基础资料" name="profile">
          <div class="account-avatar">
            <el-avatar :size="80" :icon="UserFilled" />
            <el-button size="small" type="primary">更换头像</el-button>
          </div>
          <el-form :model="accountForm" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="accountForm.username" disabled />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="accountForm.nickname" placeholder="请输入昵称" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="accountForm.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="accountForm.phone" placeholder="请输入手机号" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveAccountInfo">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 密码修改 -->
        <el-tab-pane label="密码修改" name="password">
          <el-form :model="passwordForm" label-width="120px">
            <el-form-item label="当前密码">
              <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入当前密码" />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" />
            </el-form-item>
            <el-form-item label="确认新密码">
              <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 安全设置 -->
        <el-tab-pane label="安全设置" name="security">
          <div class="security-list">
            <div class="security-item">
              <div class="security-info">
                <h4>双重验证</h4>
                <p>开启后登录时需要输入手机验证码</p>
              </div>
              <el-switch v-model="securitySettings.twoFactor" />
            </div>
            <div class="security-item">
              <div class="security-info">
                <h4>登录通知</h4>
                <p>新设备登录时发送通知</p>
              </div>
              <el-switch v-model="securitySettings.loginNotify" />
            </div>
            <div class="security-item">
              <div class="security-info">
                <h4>操作通知</h4>
                <p>重要操作后发送通知</p>
              </div>
              <el-switch v-model="securitySettings.operationNotify" />
            </div>
          </div>
          <div style="margin-top: 20px; text-align: center;">
            <el-button type="primary" @click="saveSecuritySettings">保存设置</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Odometer, Collection, Setting, UserFilled, Fold, Expand, MessageBox, Shop, Lightning, Box, Tickets, TrendCharts, Wallet, OfficeBuilding, ArrowDown, User, SwitchButton, Monitor, SetUp } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)
const isMobile = ref(false)

// 服务商信息
const providerInfo = ref({
  name: '科技云',
  contactName: '张经理',
  contactPhone: '400-888-8888',
  email: 'support@techcloud.com',
  level: '金牌服务商',
  levelType: 'danger'
})

// 账号管理弹窗
const showAccountDialog = ref(false)
const accountActiveTab = ref('profile')

// 账号信息
const accountForm = ref({
  username: 'admin',
  nickname: '管理员',
  email: 'admin@example.com',
  phone: '13800138000',
  avatar: ''
})

// 密码修改
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 安全设置
const securitySettings = ref({
  twoFactor: false,
  loginNotify: true,
  operationNotify: true
})

const saveAccountInfo = () => {
  ElMessage.success('账号信息保存成功')
}

const changePassword = () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }
  ElMessage.success('密码修改成功')
  passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
}

const saveSecuritySettings = () => {
  ElMessage.success('安全设置保存成功')
}

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const checkScreenSize = () => {
  const width = window.innerWidth
  isMobile.value = width < 768
  if (isMobile.value) {
    isCollapse.value = true
  } else if (width >= 1200) {
    isCollapse.value = false
  }
}

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

const logout = async () => {
  userStore.logout()
  // 通知 Electron 主进程退出登录
  if (window.electronAPI && window.electronAPI.logout) {
    await window.electronAPI.logout()
  } else {
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.sidebar .el-menu {
  overflow-y: auto;
  overflow-x: hidden;
  height: calc(100vh - 60px);
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.sidebar .el-menu::-webkit-scrollbar {
  display: none;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #1f2d3d;
}

.logo h3 {
  color: #fff;
  margin: 0;
  font-size: 18px;
}

.logo-icon {
  font-size: 24px;
}

.header {
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.collapse-btn {
  font-size: 18px;
}

.page-title {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
}

.provider-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 4px;
  transition: background 0.2s;
}

.provider-label {
  margin-right: 4px;
  font-weight: 500;
}

.provider-info:hover {
  background: #f5f5f5;
}

.provider-name {
  font-size: 14px;
  color: #606266;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.provider-detail h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
}

.provider-detail .detail-item {
  display: flex;
  margin: 8px 0;
  font-size: 13px;
}

.provider-detail .label {
  color: #909399;
  width: 80px;
  flex-shrink: 0;
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.main-content::-webkit-scrollbar {
  display: none;
}

.mobile-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.mobile-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 1000;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
}

.mobile-sidebar.collapsed {
  transform: translateX(-100%);
}

@media screen and (max-width: 768px) {
  .header {
    padding: 0 10px;
  }
  
  .page-title {
    font-size: 16px;
  }
  
  .username {
    display: none;
  }
  
  .main-content {
    padding: 10px;
  }
}

/* 账号管理弹窗样式 */
.account-tabs {
  min-height: 400px;
}

.account-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.account-avatar .el-avatar {
  margin-bottom: 12px;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #ebeef5;
}

.security-item:last-child {
  border-bottom: none;
}

.security-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
}

.security-info p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}
</style>
