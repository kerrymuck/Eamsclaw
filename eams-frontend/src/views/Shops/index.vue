<template>
  <div class="shop-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>🏪 店铺管理</h2>
        <p class="subtitle">管理您的多平台店铺，一个界面统一管理</p>
      </div>
      <el-button type="primary" size="large" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        添加店铺
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #e6f7ff; color: #1890ff;">🏪</div>
          <div class="stat-info">
            <div class="stat-value">{{ shops.length }}</div>
            <div class="stat-label">总店铺数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #f6ffed; color: #52c41a;">✅</div>
          <div class="stat-info">
            <div class="stat-value">{{ activeShops.length }}</div>
            <div class="stat-label">营业中</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #fff7e6; color: #fa8c16;">⚠️</div>
          <div class="stat-info">
            <div class="stat-value">{{ authExpiredShops.length }}</div>
            <div class="stat-label">授权过期</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #f9f0ff; color: #722ed1;">💬</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalUnread }}</div>
            <div class="stat-label">未读消息</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 平台筛选 -->
    <div class="platform-filter">
      <span class="filter-label">平台筛选：</span>
      <el-radio-group v-model="filterPlatform" size="small">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button v-for="p in platformOptions.slice(0,8)" :key="p.id" :label="p.id">
          {{ p.icon }} {{ p.name }}
        </el-radio-button>
      </el-radio-group>
    </div>

    <!-- 店铺列表 -->
    <el-row :gutter="20" class="shop-list">
      <el-col 
        v-for="shop in filteredShops" 
        :key="shop.id"
        :xs="24" 
        :sm="12" 
        :md="8" 
        :lg="6"
      >
        <el-card class="shop-card" :class="{ 'inactive': shop.status !== 'active' }">
          <div class="shop-header">
            <div class="shop-platform">
              <span class="platform-icon">{{ getPlatformIcon(shop.platform) }}</span>
              <el-tag size="small" :type="getPlatformTagType(shop.platform)">
                {{ getPlatformName(shop.platform) }}
              </el-tag>
            </div>
            <el-dropdown>
              <el-button size="small" circle><el-icon><More /></el-icon></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>编辑</el-dropdown-item>
                  <el-dropdown-item v-if="shop.authStatus === 'expired'">重新授权</el-dropdown-item>
                  <el-dropdown-item divided>{{ shop.status === 'active' ? '暂停营业' : '恢复营业' }}</el-dropdown-item>
                  <el-dropdown-item type="danger">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          
          <div class="shop-info">
            <el-avatar :size="64" :src="shop.logo" class="shop-logo">
              {{ shop.name.charAt(0) }}
            </el-avatar>
            <h4 class="shop-name">{{ shop.name }}</h4>
            <p class="shop-id">ID: {{ shop.platformShopId }}</p>
            <el-tag :type="getAuthStatusType(shop.authStatus)" size="small" class="auth-status">
              {{ getAuthStatusText(shop.authStatus) }}
            </el-tag>
          </div>
          
          <div class="shop-stats">
            <div class="stat-item">
              <div class="stat-num">{{ shop.todayOrders }}</div>
              <div class="stat-label">今日订单</div>
            </div>
            <div class="stat-item">
              <div class="stat-num">{{ shop.todaySales }}</div>
              <div class="stat-label">今日销售额</div>
            </div>
            <div class="stat-item">
              <div class="stat-num">{{ shop.unreadMessages }}</div>
              <div class="stat-label">未读消息</div>
            </div>
          </div>
          
          <div class="shop-actions">
            <el-button type="primary" size="small" @click="enterInbox(shop)">
              <el-icon><ChatDotRound /></el-icon> 进入收件箱
            </el-button>
            <el-button size="small" @click="viewOrders(shop)">
              <el-icon><Document /></el-icon> 查看订单
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, More, ChatDotRound, Document } from '@element-plus/icons-vue'
import { getAllPlatforms, getPlatformIcon, getPlatformName, getPlatformTagType } from '@/config/platforms'

const router = useRouter()
const platformOptions = getAllPlatforms()
const filterPlatform = ref('all')
const showAddDialog = ref(false)

// 32个平台的模拟店铺数据
const shops = ref([
  { id: 1, name: '龙猫数码旗舰店', platform: 'taobao', platformShopId: 'TB12345678', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-03-21', todayOrders: 128, todaySales: '¥45,680', unreadMessages: 23 },
  { id: 2, name: '龙猫天猫旗舰店', platform: 'tmall', platformShopId: 'TM87654321', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-06-15', todayOrders: 96, todaySales: '¥52,300', unreadMessages: 18 },
  { id: 3, name: '龙猫1688批发店', platform: 'alibaba', platformShopId: '1688112233', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-04-20', todayOrders: 45, todaySales: '¥128,000', unreadMessages: 12 },
  { id: 4, name: '龙猫京东自营', platform: 'jd', platformShopId: 'JD87654321', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-06-15', todayOrders: 86, todaySales: '¥32,450', unreadMessages: 15 },
  { id: 5, name: '龙猫拼多多店', platform: 'pdd', platformShopId: 'PDD11223344', logo: '', status: 'active', authStatus: 'expired', authExpireTime: '2024-12-01', todayOrders: 0, todaySales: '¥0', unreadMessages: 0 },
  { id: 6, name: '龙猫抖音小店', platform: 'douyin', platformShopId: 'DY55667788', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-05-10', todayOrders: 67, todaySales: '¥28,900', unreadMessages: 9 },
  { id: 7, name: '龙猫小红书店', platform: 'xiaohongshu', platformShopId: 'XHS99887766', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-07-01', todayOrders: 34, todaySales: '¥15,600', unreadMessages: 6 },
  { id: 8, name: 'Longmao Amazon Store', platform: 'amazon', platformShopId: 'A123456789', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-08-15', todayOrders: 45, todaySales: '$3,250', unreadMessages: 8 },
  { id: 9, name: 'Longmao eBay Shop', platform: 'ebay', platformShopId: 'EB987654321', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-09-20', todayOrders: 23, todaySales: '$1,890', unreadMessages: 4 },
  { id: 10, name: 'Longmao AliExpress', platform: 'aliexpress', platformShopId: 'AE11223344', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-04-30', todayOrders: 56, todaySales: '$2,780', unreadMessages: 7 },
  { id: 11, name: 'Longmao Shopee', platform: 'shopee', platformShopId: 'SH55667788', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-05-25', todayOrders: 78, todaySales: '$1,560', unreadMessages: 11 },
  { id: 12, name: 'Longmao Lazada', platform: 'lazada', platformShopId: 'LA99887766', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-06-10', todayOrders: 42, todaySales: '$980', unreadMessages: 5 },
  { id: 13, name: 'Longmao Temu', platform: 'temu', platformShopId: 'TM22334455', logo: '', status: 'active', authStatus: 'pending', authExpireTime: '', todayOrders: 0, todaySales: '¥0', unreadMessages: 0 },
  { id: 14, name: 'Longmao TikTok Shop', platform: 'tiktokshop', platformShopId: 'TT66778899', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-07-20', todayOrders: 89, todaySales: '$2,340', unreadMessages: 13 },
  { id: 15, name: 'Longmao SHEIN', platform: 'shein', platformShopId: 'SN33445566', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-08-01', todayOrders: 67, todaySales: '$1,890', unreadMessages: 9 },
  { id: 16, name: 'Longmao Mercado', platform: 'mercadolibre', platformShopId: 'ML44556677', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-09-15', todayOrders: 34, todaySales: '$890', unreadMessages: 4 },
  { id: 17, name: 'Longmao Rakuten', platform: 'rakuten', platformShopId: 'RA55667788', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-10-20', todayOrders: 12, todaySales: '¥45,000', unreadMessages: 2 },
  { id: 18, name: 'Longmao Coupang', platform: 'coupang', platformShopId: 'CP66778899', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-11-01', todayOrders: 28, todaySales: '₩890,000', unreadMessages: 3 },
  { id: 19, name: 'Longmao Ozon', platform: 'ozon', platformShopId: 'OZ77889900', logo: '', status: 'active', authStatus: 'expired', authExpireTime: '2024-11-15', todayOrders: 0, todaySales: '₽0', unreadMessages: 0 },
  { id: 20, name: 'Longmao Allegro', platform: 'allegro', platformShopId: 'AL88990011', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-12-10', todayOrders: 15, todaySales: 'zł450', unreadMessages: 2 },
  { id: 21, name: 'Longmao Joom', platform: 'joom', platformShopId: 'JO99001122', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-08-25', todayOrders: 8, todaySales: '€120', unreadMessages: 1 },
  { id: 22, name: 'Longmao Wish', platform: 'wish', platformShopId: 'WI00112233', logo: '', status: 'inactive', authStatus: 'active', authExpireTime: '2025-07-30', todayOrders: 0, todaySales: '$0', unreadMessages: 0 },
  { id: 23, name: '龙猫Made-in-China', platform: 'madeinchina', platformShopId: 'MIC223344', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-09-01', todayOrders: 5, todaySales: '$15,000', unreadMessages: 2 },
  { id: 24, name: '龙猫环球资源', platform: 'globalsources', platformShopId: 'GS334455', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-10-15', todayOrders: 3, todaySales: '$8,500', unreadMessages: 1 },
  { id: 25, name: '龙猫敦煌网', platform: 'dhgate', platformShopId: 'DH445566', logo: '', status: 'active', authStatus: 'pending', authExpireTime: '', todayOrders: 0, todaySales: '$0', unreadMessages: 0 },
  { id: 26, name: 'Longmao Shopify', platform: 'shopify', platformShopId: 'SHOP5566', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-11-20', todayOrders: 32, todaySales: '$2,100', unreadMessages: 5 },
  { id: 27, name: 'Longmao WooCommerce', platform: 'woocommerce', platformShopId: 'WC6677', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-12-01', todayOrders: 18, todaySales: '$980', unreadMessages: 3 },
  { id: 28, name: 'Longmao BigCommerce', platform: 'bigcommerce', platformShopId: 'BC7788', logo: '', status: 'active', authStatus: 'active', authExpireTime: '2025-10-10', todayOrders: 12, todaySales: '$650', unreadMessages: 2 },
  { id: 29, name: 'Longmao Magento', platform: 'magento', platformShopId: 'MG8899', logo: '', status: 'inactive', authStatus: 'active', authExpireTime: '2025-09-30', todayOrders: 0, todaySales: '$0', unreadMessages: 0 },
])

const activeShops = computed(() => shops.value.filter(s => s.status === 'active'))
const authExpiredShops = computed(() => shops.value.filter(s => s.authStatus === 'expired'))
const totalUnread = computed(() => shops.value.reduce((sum, s) => sum + s.unreadMessages, 0))

const filteredShops = computed(() => {
  if (filterPlatform.value === 'all') return shops.value
  return shops.value.filter(s => s.platform === filterPlatform.value)
})

const getAuthStatusType = (status: string) => {
  const types: Record<string, string> = { active: 'success', expired: 'danger', pending: 'warning' }
  return types[status] || 'info'
}

const getAuthStatusText = (status: string) => {
  const texts: Record<string, string> = { active: '已授权', expired: '已过期', pending: '待授权' }
  return texts[status] || status
}

const enterInbox = (shop: any) => {
  router.push({ path: '/inbox', query: { shopId: shop.id } })
}

const viewOrders = (shop: any) => {
  router.push({ path: '/orders', query: { shopId: shop.id } })
}
</script>

<style scoped>
.shop-management {
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.header-left h2 {
  margin: 0 0 8px 0;
}
.subtitle {
  color: #909399;
  margin: 0;
}
.stats-row {
  margin-bottom: 24px;
}
.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 12px;
}
.stat-info {
  flex: 1;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}
.stat-label {
  font-size: 14px;
  color: #909399;
}
.platform-filter {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.filter-label {
  font-weight: 500;
  color: #606266;
}
.shop-list {
  margin-top: 20px;
}
.shop-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}
.shop-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.shop-card.inactive {
  opacity: 0.6;
}
.shop-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.shop-platform {
  display: flex;
  align-items: center;
  gap: 8px;
}
.platform-icon {
  font-size: 20px;
}
.shop-info {
  text-align: center;
  margin-bottom: 16px;
}
.shop-logo {
  margin-bottom: 12px;
  background: #409eff;
  color: white;
  font-size: 24px;
}
.shop-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}
.shop-id {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #909399;
}
.auth-status {
  margin-top: 8px;
}
.shop-stats {
  display: flex;
  justify-content: space-around;
  padding: 16px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 16px;
}
.stat-item {
  text-align: center;
}
.stat-num {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}
.stat-item .stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
.shop-actions {
  display: flex;
  gap: 8px;
}
.shop-actions .el-button {
  flex: 1;
}
</style>
