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
        <h3 v-if="!isCollapse">EAMS</h3>
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
        
        <el-menu-item index="/inbox">
          <el-icon><MessageBox /></el-icon>
          <template #title>消息中心</template>
        </el-menu-item>
        
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
        
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>设置</template>
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
          <h3 class="page-title">{{ $route.meta.title || 'EAMS' }}</h3>
        </div>
        <el-dropdown>
          <span class="user-info">
            <el-avatar :size="32" :icon="UserFilled" />
            <span class="username">{{ userStore.username }}</span>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Odometer, ChatDotRound, Collection, Setting, UserFilled, Fold, Expand, MessageBox, Shop, Lightning, Box, Tickets, TrendCharts } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 响应式状态
const isCollapse = ref(false)
const isMobile = ref(false)

// 切换侧边栏
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

// 检查屏幕尺寸
const checkScreenSize = () => {
  const width = window.innerWidth
  isMobile.value = width < 768
  if (isMobile.value) {
    isCollapse.value = true
  } else if (width >= 1200) {
    isCollapse.value = false
  }
}

// 监听窗口大小变化
onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

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
  background: #304156;
  transition: width 0.3s;
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

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

/* 移动端样式 */
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

/* 响应式适配 */
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

@media screen and (min-width: 769px) and (max-width: 1199px) {
  .sidebar {
    width: 64px !important;
  }
  
  .sidebar:not(.collapsed) {
    width: 200px !important;
  }
}
</style>
