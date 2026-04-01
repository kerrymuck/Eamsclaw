<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside 
      :width="isCollapse ? '64px' : '220px'"
      class="sidebar"
    >
      <div class="logo">
        <h3 v-if="!isCollapse">🐱 EAMS 超管</h3>
        <span v-else class="logo-icon">🐱</span>
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
        <!-- 数据面板 -->
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>数据面板</template>
        </el-menu-item>
        
        <!-- 系统设置 -->
        <el-sub-menu index="/system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </template>
          <el-menu-item index="/system/info">系统信息</el-menu-item>
          <el-menu-item index="/system/params">参数设置</el-menu-item>
          <el-menu-item index="/system/version">版本说明</el-menu-item>
        </el-sub-menu>
        
        <!-- 服务商管理 -->
        <el-sub-menu index="/provider">
          <template #title>
            <el-icon><OfficeBuilding /></el-icon>
            <span>服务商管理</span>
          </template>
          <el-menu-item index="/provider">服务商列表</el-menu-item>
          <el-menu-item index="/provider/settings">服务商设置</el-menu-item>
        </el-sub-menu>
        
        <!-- 级别管理 -->
        <el-sub-menu index="/level">
          <template #title>
            <el-icon><Medal /></el-icon>
            <span>级别管理</span>
          </template>
          <el-menu-item index="/level">服务商等级</el-menu-item>
          <el-menu-item index="/level/settings">等级设置</el-menu-item>
        </el-sub-menu>
        
        <!-- 开发管理 -->
        <el-sub-menu index="/development">
          <template #title>
            <el-icon><Code /></el-icon>
            <span>开发管理</span>
          </template>
          <el-menu-item index="/development">平台列表</el-menu-item>
          <el-menu-item index="/development/settings">平台设置</el-menu-item>
        </el-sub-menu>
        
        <!-- 财务管理 -->
        <el-sub-menu index="/finance">
          <template #title>
            <el-icon><Money /></el-icon>
            <span>财务管理</span>
          </template>
          <el-menu-item index="/finance">收支明细</el-menu-item>
          <el-menu-item index="/finance/recharge">充值明细</el-menu-item>
        </el-sub-menu>
        
        <!-- AI算力中控 -->
        <el-sub-menu index="/ai">
          <template #title>
            <el-icon><Cpu /></el-icon>
            <span>AI算力中控</span>
          </template>
          <el-menu-item index="/ai">大模型管理</el-menu-item>
          <el-menu-item index="/ai/pricing">价格设置</el-menu-item>
        </el-sub-menu>
        
        <!-- 授权码管理 -->
        <el-sub-menu index="/license">
          <template #title>
            <el-icon><Key /></el-icon>
            <span>授权码管理</span>
          </template>
          <el-menu-item index="/license">授权列表</el-menu-item>
          <el-menu-item index="/license/settings">授权设置</el-menu-item>
        </el-sub-menu>
        
        <!-- 安全管理 -->
        <el-sub-menu index="/security">
          <template #title>
            <el-icon><Lock /></el-icon>
            <span>安全管理</span>
          </template>
          <el-menu-item index="/security">防破解</el-menu-item>
          <el-menu-item index="/security/encryption">加密管理</el-menu-item>
          <el-menu-item index="/security/ecode">Ecode设置</el-menu-item>
        </el-sub-menu>
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
          <breadcrumb />
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ userStore.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Odometer, Setting, OfficeBuilding, Medal, Code, 
  Money, Cpu, Key, Lock, UserFilled, Fold, Expand, ArrowDown 
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import Breadcrumb from './Breadcrumb.vue'

const router = useRouter()
const userStore = useUserStore()
const isCollapse = ref(false)

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background: #1a1a2e;
  transition: width 0.3s;
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

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 8px;
}

.username {
  font-size: 14px;
  color: #606266;
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
