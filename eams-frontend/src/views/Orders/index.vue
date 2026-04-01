<template>
  <div class="order-center">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>📦 订单管理中心</h2>
        <p class="subtitle">多平台订单聚合，一站式处理售后问题</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshOrders">
          <el-icon><Refresh /></el-icon>
          同步订单
        </el-button>
        <el-button @click="exportOrders">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6" :md="4">
        <el-card class="stat-card" @click="filterStatus = 'all'">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">全部订单</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="4">
        <el-card class="stat-card pending" @click="filterStatus = 'pending'">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待处理</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="4">
        <el-card class="stat-card" @click="filterStatus = 'shipped'">
          <div class="stat-value">{{ stats.shipped }}</div>
          <div class="stat-label">已发货</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="4">
        <el-card class="stat-card warning" @click="filterStatus = 'refunding'">
          <div class="stat-value">{{ stats.refunding }}</div>
          <div class="stat-label">退款/售后</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="4">
        <el-card class="stat-card danger" @click="filterStatus = 'exception'">
          <div class="stat-value">{{ stats.exception }}</div>
          <div class="stat-label">异常订单</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="4">
        <el-card class="stat-card success" @click="filterStatus = 'completed'">
          <div class="stat-value">{{ stats.completed }}</div>
          <div class="stat-label">已完成</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-row :gutter="16" align="middle">
        <el-col :xs="24" :sm="8" :md="6">
          <el-input
            v-model="searchKeyword"
            placeholder="订单号/商品/买家"
            :prefix-icon="Search"
            clearable
          />
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-select v-model="filterPlatform" placeholder="全部平台" clearable>
            <el-option label="全部平台" value="" />
            <el-option v-for="p in platforms" :key="p.id" :label="p.name" :value="p.id">
              <span>{{ p.icon }}</span> {{ p.name }}
            </el-option>
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-select v-model="filterStatus" placeholder="订单状态" clearable>
            <el-option label="全部状态" value="all" />
            <el-option label="待付款" value="unpaid" />
            <el-option label="待发货" value="paid" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已签收" value="received" />
            <el-option label="退款中" value="refunding" />
            <el-option label="已退款" value="refunded" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="8" :md="6">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%"
          />
        </el-col>
        <el-col :xs="24" :sm="4" :md="4">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 订单列表 -->
    <el-card class="order-list-card">
      <el-table
        :data="filteredOrders"
        v-loading="loading"
        stripe
        @row-click="handleRowClick"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="order-detail">
              <el-row :gutter="20">
                <el-col :span="12">
                  <h4>商品信息</h4>
                  <div v-for="item in row.items" :key="item.id" class="product-item">
                    <el-image :src="item.image" :alt="item.name" style="width: 60px; height: 60px" />
                    <div class="product-info">
                      <div class="product-name">{{ item.name }}</div>
                      <div class="product-sku">{{ item.sku }}</div>
                      <div class="product-price">
                        ¥{{ item.price }} × {{ item.quantity }}
                      </div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <h4>物流信息</h4>
                  <div v-if="row.logistics" class="logistics-info">
                    <p><strong>快递公司：</strong>{{ row.logistics.company }}</p>
                    <p><strong>运单号：</strong>{{ row.logistics.trackingNo }}</p>
                    <p><strong>发货时间：</strong>{{ row.logistics.shipTime }}</p>
                    <el-button type="primary" link @click="trackLogistics(row)">查看物流</el-button>
                  </div>
                  <div v-else class="no-logistics">暂无物流信息</div>
                </el-col>
              </el-row>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="订单号" min-width="180">
          <template #default="{ row }">
            <div class="order-no">
              <span class="platform-icon">{{ getPlatformIcon(row.platform) }}</span>
              <span class="no-text">{{ row.orderNo }}</span>
              <el-tag size="small" :type="getPlatformType(row.platform)">
                {{ getPlatformName(row.platform) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="商品" min-width="200">
          <template #default="{ row }">
            <div class="product-preview">
              <el-image :src="row.items[0]?.image" style="width: 40px; height: 40px" />
              <div class="product-text">
                <div class="name">{{ row.items[0]?.name }}</div>
                <div v-if="row.items.length > 1" class="more">+{{ row.items.length - 1 }}件商品</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="买家" width="150">
          <template #default="{ row }">
            <div class="buyer-info">
              <div class="name">{{ row.buyer.name }}</div>
              <div class="phone">{{ row.buyer.phone }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">
            <div class="amount">
              <div class="total">¥{{ row.totalAmount }}</div>
              <div class="freight">含运费¥{{ row.freight }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="时间" width="160">
          <template #default="{ row }">
            <div class="time-info">
              <div>下单：{{ formatTime(row.createTime) }}</div>
              <div v-if="row.payTime">付款：{{ formatTime(row.payTime) }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'paid'" 
              type="primary" 
              size="small"
              @click.stop="handleShip(row)"
            >
              发货
            </el-button>
            <el-button 
              v-if="row.status === 'refunding'" 
              type="warning" 
              size="small"
              @click.stop="handleRefund(row)"
            >
              处理退款
            </el-button>
            <el-button 
              type="primary" 
              link 
              size="small"
              @click.stop="viewDetail(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 发货对话框 -->
    <el-dialog v-model="shipDialogVisible" title="订单发货" width="500px">
      <el-form :model="shipForm" label-width="100px">
        <el-form-item label="物流公司">
          <el-select v-model="shipForm.company" placeholder="选择物流公司">
            <el-option label="顺丰速运" value="sf" />
            <el-option label="中通快递" value="zt" />
            <el-option label="圆通速递" value="yt" />
            <el-option label="申通快递" value="st" />
            <el-option label="韵达速递" value="yd" />
            <el-option label="EMS" value="ems" />
          </el-select>
        </el-form-item>
        <el-form-item label="运单号">
          <el-input v-model="shipForm.trackingNo" placeholder="请输入运单号" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="shipForm.remark" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shipDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmShip">确认发货</el-button>
      </template>
    </el-dialog>

    <!-- 退款处理对话框 -->
    <el-dialog v-model="refundDialogVisible" title="退款处理" width="500px">
      <div v-if="currentOrder" class="refund-info">
        <p><strong>订单号：</strong>{{ currentOrder.orderNo }}</p>
        <p><strong>退款金额：</strong>¥{{ currentOrder.refundAmount }}</p>
        <p><strong>退款原因：</strong>{{ currentOrder.refundReason }}</p>
      </div>
      <el-form :model="refundForm" label-width="100px" style="margin-top: 20px">
        <el-form-item label="处理结果">
          <el-radio-group v-model="refundForm.result">
            <el-radio label="agree">同意退款</el-radio>
            <el-radio label="reject">拒绝退款</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="处理说明">
          <el-input v-model="refundForm.remark" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="refundDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRefund">确认处理</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download, Search } from '@element-plus/icons-vue'
import { getPlatformIcon, getPlatformName, getPlatformTagType } from '@/config/platforms'

// 平台列表
const platforms = [
  { id: 'taobao', name: '淘宝', icon: '🍑' },
  { id: 'tmall', name: '天猫', icon: '🐱' },
  { id: 'jd', name: '京东', icon: '🐕' },
  { id: 'pdd', name: '拼多多', icon: '🟥' },
  { id: 'douyin', name: '抖店', icon: '🎵' }
]

// 统计数据
const stats = ref({
  total: 1256,
  pending: 23,
  shipped: 156,
  refunding: 8,
  exception: 3,
  completed: 1066
})

// 筛选条件
const searchKeyword = ref('')
const filterPlatform = ref('')
const filterStatus = ref('all')
const dateRange = ref([])
const loading = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(1256)

// 对话框
const shipDialogVisible = ref(false)
const refundDialogVisible = ref(false)
const currentOrder = ref<any>(null)

const shipForm = ref({
  company: '',
  trackingNo: '',
  remark: ''
})

const refundForm = ref({
  result: 'agree',
  remark: ''
})

// 模拟订单数据
const orders = ref([
  {
    id: '1',
    orderNo: 'TB202403230001',
    platform: 'taobao',
    buyer: { name: '张三', phone: '138****8888' },
    items: [
      { id: '1', name: 'iPhone 15 Pro Max 256GB', sku: '颜色:黑色', price: 9999, quantity: 1, image: '' }
    ],
    totalAmount: 9999,
    freight: 0,
    status: 'paid',
    createTime: '2024-03-23 10:30:00',
    payTime: '2024-03-23 10:35:00',
    logistics: null
  },
  {
    id: '2',
    orderNo: 'JD202403230002',
    platform: 'jd',
    buyer: { name: '李四', phone: '139****6666' },
    items: [
      { id: '2', name: '小米14 Pro 12+256GB', sku: '颜色:白色', price: 4999, quantity: 1, image: '' },
      { id: '3', name: '小米无线充电器', sku: '标配', price: 199, quantity: 1, image: '' }
    ],
    totalAmount: 5198,
    freight: 0,
    status: 'shipped',
    createTime: '2024-03-23 09:15:00',
    payTime: '2024-03-23 09:20:00',
    logistics: { company: '顺丰速运', trackingNo: 'SF1234567890', shipTime: '2024-03-23 14:00:00' }
  },
  {
    id: '3',
    orderNo: 'PDD202403230003',
    platform: 'pdd',
    buyer: { name: '王五', phone: '137****9999' },
    items: [
      { id: '4', name: '蓝牙耳机', sku: '颜色:蓝色', price: 99, quantity: 2, image: '' }
    ],
    totalAmount: 198,
    freight: 10,
    status: 'refunding',
    refundAmount: 198,
    refundReason: '商品质量问题',
    createTime: '2024-03-22 15:20:00',
    payTime: '2024-03-22 15:25:00',
    logistics: null
  }
])

// 过滤后的订单
const filteredOrders = computed(() => {
  let result = orders.value
  
  if (filterStatus.value && filterStatus.value !== 'all') {
    result = result.filter(o => o.status === filterStatus.value)
  }
  
  if (filterPlatform.value) {
    result = result.filter(o => o.platform === filterPlatform.value)
  }
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(o => 
      o.orderNo.toLowerCase().includes(keyword) ||
      o.buyer.name.includes(keyword) ||
      o.items.some((i: any) => i.name.includes(keyword))
    )
  }
  
  return result
})

// 方法
const getPlatformType = getPlatformTagType

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    unpaid: 'info',
    paid: 'warning',
    shipped: 'primary',
    received: 'success',
    refunding: 'danger',
    refunded: 'info',
    completed: 'success'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    unpaid: '待付款',
    paid: '待发货',
    shipped: '已发货',
    received: '已签收',
    refunding: '退款中',
    refunded: '已退款',
    completed: '已完成'
  }
  return map[status] || status
}

const formatTime = (time: string) => {
  return time.split(' ')[0]
}

const handleSearch = () => {
  ElMessage.success('查询成功')
}

const resetFilter = () => {
  searchKeyword.value = ''
  filterPlatform.value = ''
  filterStatus.value = 'all'
  dateRange.value = []
}

const refreshOrders = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('订单同步成功')
  }, 1000)
}

const exportOrders = () => {
  ElMessage.success('订单导出成功')
}

const handleRowClick = (row: any) => {
  console.log('Row clicked:', row)
}

const handleShip = (row: any) => {
  currentOrder.value = row
  shipDialogVisible.value = true
}

const confirmShip = () => {
  ElMessage.success('发货成功')
  shipDialogVisible.value = false
}

const handleRefund = (row: any) => {
  currentOrder.value = row
  refundDialogVisible.value = true
}

const confirmRefund = () => {
  ElMessage.success('退款处理成功')
  refundDialogVisible.value = false
}

const viewDetail = (row: any) => {
  ElMessage.info('查看订单详情：' + row.orderNo)
}

const trackLogistics = (row: any) => {
  ElMessage.info('查看物流：' + row.logistics?.trackingNo)
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}
</script>

<style scoped>
.order-center {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h2 {
  margin: 0 0 8px 0;
}

.subtitle {
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stat-card.pending {
  border-top: 3px solid #e6a23c;
}

.stat-card.warning {
  border-top: 3px solid #f56c6c;
}

.stat-card.danger {
  border-top: 3px solid #ff4d4f;
}

.stat-card.success {
  border-top: 3px solid #67c23a;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.filter-card {
  margin-bottom: 20px;
}

.order-list-card {
  margin-bottom: 20px;
}

.order-no {
  display: flex;
  align-items: center;
  gap: 8px;
}

.platform-icon {
  font-size: 16px;
}

.no-text {
  font-family: monospace;
  color: #606266;
}

.product-preview {
  display: flex;
  align-items: center;
  gap: 10px;
}

.product-text {
  flex: 1;
}

.product-text .name {
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-text .more {
  font-size: 12px;
  color: #909399;
}

.buyer-info .name {
  font-size: 14px;
  color: #303133;
}

.buyer-info .phone {
  font-size: 12px;
  color: #909399;
}

.amount {
  text-align: right;
}

.amount .total {
  font-size: 16px;
  font-weight: bold;
  color: #f56c6c;
}

.amount .freight {
  font-size: 12px;
  color: #909399;
}

.time-info {
  font-size: 12px;
  color: #909399;
}

.order-detail {
  padding: 20px;
  background: #f5f7fa;
}

.order-detail h4 {
  margin-bottom: 12px;
  color: #303133;
}

.product-item {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.product-info {
  flex: 1;
}

.product-info .product-name {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
}

.product-info .product-sku {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.product-info .product-price {
  font-size: 14px;
  color: #f56c6c;
}

.logistics-info p {
  margin-bottom: 8px;
  font-size: 14px;
}

.no-logistics {
  color: #909399;
  font-size: 14px;
}

.refund-info p {
  margin-bottom: 12px;
  font-size: 14px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
