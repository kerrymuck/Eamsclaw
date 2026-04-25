<template>
  <div class="shop-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>🏪 店铺管理</h2>
        <p class="subtitle">管理您的多平台店铺，一个界面统一管理</p>
      </div>
      <el-button type="primary" size="large" @click="openAddDialog">
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
                  <el-dropdown-item @click="editShop(shop)">编辑</el-dropdown-item>
                  <el-dropdown-item v-if="shop.authStatus === 'expired'" @click="reauthShop(shop)">重新授权</el-dropdown-item>
                  <el-dropdown-item divided @click="toggleShopStatus(shop)">{{ shop.status === 'active' ? '暂停营业' : '恢复营业' }}</el-dropdown-item>
                  <el-dropdown-item type="danger" @click="deleteShop(shop)">删除</el-dropdown-item>
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

    <!-- 添加/编辑店铺弹窗 -->
    <el-dialog
      v-model="showAddDialog"
      :title="isEdit ? '编辑店铺' : '添加店铺'"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="选择平台" prop="platform">
          <el-select v-model="form.platform" placeholder="请选择电商平台" style="width: 100%">
            <el-option
              v-for="p in platformOptions"
              :key="p.id"
              :label="`${p.icon} ${p.name}`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="店铺名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入店铺名称" maxlength="50" show-word-limit />
        </el-form-item>

        <el-form-item label="平台店铺ID" prop="platformShopId">
          <el-input v-model="form.platformShopId" placeholder="请输入平台分配的店铺ID" />
          <div class="form-tip">在平台后台可以查看店铺ID</div>
        </el-form-item>

        <el-form-item label="店铺Logo">
          <el-upload
            class="avatar-uploader"
            action="#"
            :show-file-list="false"
            :auto-upload="false"
            :on-change="handleLogoChange"
          >
            <el-avatar v-if="form.logo" :size="80" :src="form.logo" />
            <div v-else class="upload-placeholder">
              <el-icon :size="28"><Plus /></el-icon>
              <span>点击上传</span>
            </div>
          </el-upload>
        </el-form-item>

        <el-form-item label="店铺状态">
          <el-switch
            v-model="form.status"
            active-value="active"
            inactive-value="inactive"
            active-text="营业中"
            inactive-text="已暂停"
          />
        </el-form-item>

        <el-form-item label="授权码" prop="licenseCode" required>
          <el-input v-model="form.licenseCode" placeholder="请输入授权码（一个店铺对应一个授权码）">
            <template #append>
              <el-button @click="verifyLicense">验证</el-button>
            </template>
          </el-input>
          <div class="form-tip">
            <el-link type="primary" @click="showLicenseHelp = true">如何获取授权码？</el-link>
          </div>
        </el-form-item>

        <!-- 授权码验证结果显示 -->
        <el-form-item v-if="licenseInfo.show">
          <el-alert
            :title="licenseInfo.valid ? '授权码有效' : '授权码无效'"
            :type="licenseInfo.valid ? 'success' : 'error'"
            :description="licenseInfo.message"
            :closable="false"
            show-icon
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveShop" :loading="saving">
          {{ isEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 版本更新提示弹窗 -->
    <el-dialog
      v-model="showUpdateDialog"
      title="发现新版本"
      width="500px"
      :close-on-click-modal="!updateInfo?.forceUpdate"
      :close-on-press-escape="!updateInfo?.forceUpdate"
      :show-close="!updateInfo?.forceUpdate"
    >
      <div class="update-content" v-if="updateInfo">
        <div class="update-version">
          <span class="version-label">最新版本</span>
          <span class="version-num">v{{ updateInfo.version }}</span>
        </div>
        <div class="update-current">当前版本: v{{ currentVersion }}</div>
        
        <div class="update-desc">
          <h4>更新内容:</h4>
          <p>{{ updateInfo.description }}</p>
        </div>

        <div class="update-info">
          <div class="info-item">
            <span class="label">文件大小:</span>
            <span class="value">{{ updateInfo.fileSize }}</span>
          </div>
          <div class="info-item">
            <span class="label">发布时间:</span>
            <span class="value">{{ updateInfo.publishTime }}</span>
          </div>
        </div>

        <el-alert
          v-if="updateInfo.forceUpdate"
          title="此版本为强制更新，必须更新后才能继续使用"
          type="warning"
          :closable="false"
          show-icon
        />
      </div>

      <template #footer>
        <el-button v-if="!updateInfo?.forceUpdate" @click="showUpdateDialog = false">
          稍后更新
        </el-button>
        <el-button type="primary" @click="downloadUpdate" :loading="downloading">
          {{ downloading ? '下载中...' : '立即更新' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 授权码帮助弹窗 -->
    <el-dialog v-model="showLicenseHelp" title="如何获取授权码" width="500px">
      <div class="license-help">
        <h4>授权码获取方式：</h4>
        <ol>
          <li>联系您的服务商获取授权码</li>
          <li>每个店铺需要一个独立的授权码</li>
          <li>授权码格式：EAMS-XXX-XXXX-XXXXXXXX</li>
          <li>授权码与店铺绑定后不可重复使用</li>
        </ol>
        <el-alert
          title="温馨提示"
          description="如果您还没有授权码，请联系您的服务商购买套餐获取。"
          type="info"
          :closable="false"
          style="margin-top: 16px;"
        />
      </div>
      <template #footer>
        <el-button @click="showLicenseHelp = false">我知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, More, ChatDotRound, Document } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'
import { getAllPlatforms, getPlatformIcon, getPlatformName, getPlatformTagType } from '@/config/platforms'

const router = useRouter()
const platformOptions = getAllPlatforms()
const filterPlatform = ref('all')
const showAddDialog = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()

// 更新相关
const showUpdateDialog = ref(false)
const downloading = ref(false)
const updateInfo = ref<any>(null)
const currentVersion = ref('1.2.2')

// 表单数据
const form = reactive({
  id: null as number | null,
  platform: '',
  name: '',
  platformShopId: '',
  logo: '',
  status: 'active',
  authStatus: 'pending',
  licenseCode: ''
})

// 授权码信息
const licenseInfo = reactive({
  show: false,
  valid: false,
  message: ''
})

// 授权码帮助弹窗
const showLicenseHelp = ref(false)

// 表单验证规则
const formRules: FormRules = {
  platform: [
    { required: true, message: '请选择电商平台', trigger: 'change' }
  ],
  name: [
    { required: true, message: '请输入店铺名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  platformShopId: [
    { required: true, message: '请输入平台店铺ID', trigger: 'blur' }
  ],
  licenseCode: [
    { required: true, message: '请输入授权码', trigger: 'blur' },
    { pattern: /^EAMS-[A-Z]{3}-\d{4}-[A-Z0-9]{8}$/, message: '授权码格式不正确', trigger: 'blur' }
  ]
}

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

// 打开添加弹窗
const openAddDialog = () => {
  isEdit.value = false
  form.id = null
  form.platform = ''
  form.name = ''
  form.platformShopId = ''
  form.logo = ''
  form.status = 'active'
  form.authStatus = 'pending'
  form.licenseCode = ''
  licenseInfo.show = false
  licenseInfo.valid = false
  licenseInfo.message = ''
  showAddDialog.value = true
}

// 编辑店铺
const editShop = (shop: any) => {
  isEdit.value = true
  form.id = shop.id
  form.platform = shop.platform
  form.name = shop.name
  form.platformShopId = shop.platformShopId
  form.logo = shop.logo
  form.status = shop.status
  form.authStatus = shop.authStatus
  form.licenseCode = shop.licenseCode || ''
  licenseInfo.show = false
  showAddDialog.value = true
}

// 验证授权码
const verifyLicense = () => {
  if (!form.licenseCode) {
    ElMessage.warning('请输入授权码')
    return
  }
  
  // 模拟验证
  licenseInfo.show = true
  
  // 模拟验证成功
  if (form.licenseCode.startsWith('EAMS-')) {
    licenseInfo.valid = true
    licenseInfo.message = '授权码有效，可用于绑定此店铺。授权到期时间：2027-04-10'
    form.authStatus = 'active'
  } else {
    licenseInfo.valid = false
    licenseInfo.message = '授权码无效或已被使用，请联系服务商获取有效授权码。'
  }
}

// 保存店铺
const saveShop = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (!valid) return
    
    saving.value = true
    
    setTimeout(() => {
      if (isEdit.value && form.id) {
        // 编辑模式
        const index = shops.value.findIndex(s => s.id === form.id)
        if (index > -1) {
          shops.value[index] = {
            ...shops.value[index],
            platform: form.platform,
            name: form.name,
            platformShopId: form.platformShopId,
            logo: form.logo,
            status: form.status,
            authStatus: form.authStatus
          }
        }
        ElMessage.success('店铺信息已更新')
      } else {
        // 添加模式
        const newShop = {
          id: Date.now(),
          platform: form.platform,
          name: form.name,
          platformShopId: form.platformShopId,
          logo: form.logo,
          status: form.status,
          authStatus: form.authStatus,
          authExpireTime: '',
          todayOrders: 0,
          todaySales: '¥0',
          unreadMessages: 0
        }
        shops.value.push(newShop)
        ElMessage.success('新店铺添加成功')
      }
      
      saving.value = false
      showAddDialog.value = false
    }, 500)
  })
}

// 删除店铺
const deleteShop = (shop: any) => {
  ElMessageBox.confirm(
    `确定要删除店铺「${shop.name}」吗？此操作不可恢复！`,
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = shops.value.findIndex(s => s.id === shop.id)
    if (index > -1) {
      shops.value.splice(index, 1)
      ElMessage.success('店铺已删除')
    }
  })
}

// 切换店铺状态
const toggleShopStatus = (shop: any) => {
  const newStatus = shop.status === 'active' ? 'inactive' : 'active'
  const actionText = newStatus === 'active' ? '恢复营业' : '暂停营业'
  
  ElMessageBox.confirm(
    `确定要${actionText}「${shop.name}」吗？`,
    '确认操作',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    shop.status = newStatus
    ElMessage.success(`店铺已${actionText}`)
  })
}

// 重新授权
const reauthShop = (shop: any) => {
  ElMessage.info(`正在重新授权「${shop.name}」，请稍候...`)
  setTimeout(() => {
    shop.authStatus = 'active'
    shop.authExpireTime = '2025-12-31'
    ElMessage.success('授权成功')
  }, 1500)
}

// 处理Logo上传
const handleLogoChange = (file: UploadFile) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    form.logo = e.target?.result as string
  }
  if (file.raw) {
    reader.readAsDataURL(file.raw)
  }
}

// 检查版本更新
const checkUpdate = async () => {
  // 模拟API调用
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  // 模拟有新版本
  updateInfo.value = {
    version: '1.2.3',
    description: '修复已知问题，优化性能，新增店铺管理功能',
    fileSize: '45.2 MB',
    forceUpdate: false,
    publishTime: '2026-04-10 10:00:00',
    downloadUrl: 'https://your-domain.com/downloads/v1.2.3.zip'
  }
  
  showUpdateDialog.value = true
}

// 下载更新
const downloadUpdate = () => {
  downloading.value = true
  
  // 模拟下载
  setTimeout(() => {
    downloading.value = false
    showUpdateDialog.value = false
    
    ElMessageBox.alert(
      '更新包已下载完成，应用将在重启后更新到最新版本。',
      '下载完成',
      {
        confirmButtonText: '立即重启',
        callback: () => {
          window.location.reload()
        }
      }
    )
  }, 2000)
}

// 初始化
onMounted(() => {
  // 启动时检查更新
  checkUpdate()
})
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

/* 表单样式 */
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
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
  overflow: hidden;
}

.avatar-uploader:hover {
  border-color: #1677ff;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #999;
  font-size: 12px;
}

/* 更新弹窗样式 */
.update-content {
  padding: 10px 0;
}

.update-version {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.version-label {
  font-size: 14px;
  color: #909399;
}

.version-num {
  font-size: 24px;
  font-weight: bold;
  color: #1677ff;
}

.update-current {
  font-size: 13px;
  color: #909399;
  margin-bottom: 16px;
}

.update-desc {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.update-desc h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #333;
}

.update-desc p {
  margin: 0;
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}

.update-info {
  margin-bottom: 16px;
}

.update-info .info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.update-info .info-item:last-child {
  border-bottom: none;
}

.update-info .label {
  color: #909399;
  font-size: 13px;
}

.update-info .value {
  color: #333;
  font-size: 13px;
}

/* 授权码帮助弹窗样式 */
.license-help {
  padding: 10px 0;
}

.license-help h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
}

.license-help ol {
  margin: 0;
  padding-left: 20px;
  color: #606266;
  line-height: 2;
}

.license-help li {
  margin: 4px 0;
}
</style>
