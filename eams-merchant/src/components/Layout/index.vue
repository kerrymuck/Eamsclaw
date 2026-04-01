<template>
  <div class="merchant-layout">
    <!-- 移动端顶部导航 -->
    <header class="mobile-header" v-if="isMobile">
      <button class="menu-btn" @click="showSidebar = true">
        <el-icon :size="24"><Menu /></el-icon>
      </button>
      <h1 class="page-title">{{ $route.meta.title }}</h1>
      <el-dropdown>
        <el-avatar :size="32" :icon="UserFilled" />
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </header>

    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ open: showSidebar, mobile: isMobile }">
      <div class="sidebar-header">
        <div class="logo">
          <el-icon :size="28"><Shop /></el-icon>
          <span>商家中心</span>
        </div>
        <button v-if="isMobile" class="close-btn" @click="showSidebar = false">
          <el-icon :size="24"><Close /></el-icon>
        </button>
      </div>
      
      <nav class="sidebar-nav">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          :class="['nav-item', { active: $route.path === item.path }]"
          @click="isMobile && (showSidebar = false)"
        >
          <el-icon :size="20">
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.title }}</span>
          <el-badge v-if="item.badge" :value="item.badge" class="nav-badge" />
        </router-link>
      </nav>
    </aside>

    <!-- 遮罩层 -->
    <div v-if="isMobile && showSidebar" class="sidebar-overlay" @click="showSidebar = false"></div>

    <!-- 主内容区 -->
    <main class="main-content" :class="{ mobile: isMobile }">
      <!-- PC端顶部栏 -->
      <header class="pc-header" v-if="!isMobile">
        <h2>{{ $route.meta.title }}</h2>
        <div class="header-actions">
          <el-badge :value="3" class="message-badge">
            <el-button :icon="Bell" circle />
          </el-badge>
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ userStore.username || '商家用户' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>店铺设置</el-dropdown-item>
                <el-dropdown-item>账号管理</el-dropdown-item>
                <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  Odometer, ChatDotRound, Shop, User, Collection, Setting,
  Menu, Close, UserFilled, Bell, ArrowDown
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isMobile = ref(false)
const showSidebar = ref(false)

const menuItems = [
  { path: '/dashboard', title: '数据概览', icon: 'Odometer' },
  { path: '/chat', title: '消息中心', icon: 'ChatDotRound', badge: 3 },
  { path: '/shop', title: '店铺管理', icon: 'Shop' },
  { path: '/knowledge', title: '知识库', icon: 'Collection' },
  { path: '/settings', title: '系统设置', icon: 'Setting' }
]

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) {
    showSidebar.value = false
  }
}

const logout = () => {
  userStore.logout()
  router.push('/login')
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.merchant-layout {
  display: flex;
  min-height: 100vh;
  background: #f0f2f5;
}

/* 移动端头部 */
.mobile-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: #fff;
  display: flex;
  align-items: center;
  padding: 0 16px;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.menu-btn {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: #333;
  margin-right: 12px;
}

.page-title {
  flex: 1;
  font-size: 17px;
  font-weight: 600;
  margin: 0;
}

/* 侧边栏 */
.sidebar {
  width: 220px;
  background: #001529;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 200;
  transition: transform 0.3s;
}

.sidebar.mobile {
  transform: translateX(-100%);
}

.sidebar.mobile.open {
  transform: translateX(0);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  padding: 4px;
}

.sidebar-nav {
  padding: 12px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  color: rgba(255,255,255,0.65);
  text-decoration: none;
  transition: all 0.3s;
  position: relative;
}

.nav-item:hover {
  color: #fff;
  background: rgba(255,255,255,0.05);
}

.nav-item.active {
  color: #fff;
  background: #1677ff;
}

.nav-item span {
  margin-left: 12px;
  font-size: 14px;
}

.nav-badge {
  margin-left: auto;
}

/* 遮罩层 */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 150;
}

/* 主内容区 */
.main-content {
  flex: 1;
  margin-left: 220px;
  min-height: 100vh;
}

.main-content.mobile {
  margin-left: 0;
  padding-top: 56px;
}

/* PC端头部 */
.pc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.pc-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.message-badge :deep(.el-badge__content) {
  top: 8px;
  right: 8px;
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
  color: #333;
}

/* 内容区 */
.content-wrapper {
  padding: 24px;
}

.main-content.mobile .content-wrapper {
  padding: 16px;
}

/* 响应式适配 */
@media (max-width: 1024px) {
  .sidebar {
    width: 200px;
  }
  
  .main-content {
    margin-left: 200px;
  }
}

@media (max-width: 767px) {
  .content-wrapper {
    padding: 12px;
  }
}
</style>
