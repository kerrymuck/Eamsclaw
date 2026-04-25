<template>
  <div class="provider-layout">
    <!-- 侧边栏 -->
    <el-aside 
      :width="isCollapse ? '64px' : '220px'"
      class="sidebar"
    >
      <div class="logo">
        <h3 v-if="!isCollapse">🏢 服务商中心</h3>
        <span v-else>🏢</span>
      </div>
      
      <el-menu
        :default-active="$route.path"
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        background-color="#1a1a2e"
        text-color="#a0a3bd"
        active-text-color="#fff"
      >
        <el-menu-item index="/provider/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>数据面板</template>
        </el-menu-item>
        
        <el-menu-item index="/provider/merchants">
          <el-icon><Shop /></el-icon>
          <template #title>商户管理</template>
        </el-menu-item>
        
        <el-menu-item index="/provider/plans">
          <el-icon><Box /></el-icon>
          <template #title>套餐管理</template>
        </el-menu-item>
        
        <el-menu-item index="/provider/license">
          <el-icon><Key /></el-icon>
          <template #title>授权码管理</template>
        </el-menu-item>
        
        <el-menu-item index="/provider/ai-power">
          <el-icon><Cpu /></el-icon>
          <template #title>AI算力管理</template>
        </el-menu-item>
        
        <el-menu-item index="/provider/finance">
          <el-icon><Money /></el-icon>
          <template #title>财务管理</template>
        </el-menu-item>
        
        <el-menu-item index="/provider/account">
          <el-icon><User /></el-icon>
          <template #title>账号管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-button
            class="collapse-btn"
            :icon="isCollapse ? Expand : Fold"
            @click="toggleSidebar"
          />
          <!-- <breadcrumb /> -->
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ userStore.username || '服务商' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="goToAccount">账号设置</el-dropdown-item>
                <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Odometer, Shop, Box, Key, Cpu, Money, User, UserFilled, Fold, Expand, ArrowDown 
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
// import Breadcrumb from '@/components/Breadcrumb.vue'

const router = useRouter()
const userStore = useUserStore()
const isCollapse = ref(false)

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const goToAccount = () => {
  router.push('/provider/account')
}

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
.provider-layout {
  height: 100vh;
  display: flex;
}

.sidebar {
  background: #1a1a2e;
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
  border-bottom: 1px solid #2d2d44;
}

.logo h3 {
  color: #fff;
  margin: 0;
  font-size: 16px;
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

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.user-info:hover {
  background: #f5f5f5;
}

.username {
  font-size: 14px;
  color: #606266;
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
</style>
