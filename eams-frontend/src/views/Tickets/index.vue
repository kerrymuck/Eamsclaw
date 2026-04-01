<template>
  <div class="ticket-center">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>🎫 工单流转中心</h2>
        <p class="subtitle">复杂问题升级处理，团队协作高效解决</p>
      </div>
      <el-button type="primary" size="large" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建工单
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6" :md="4">
        <el-card class="stat-card" @click="filterStatus = 'all'">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">全部工单</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="4">
        <el-card class="stat-card pending" @click="filterStatus = 'pending'">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待处理</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="4">
        <el-card class="stat-card processing" @click="filterStatus = 'processing'">
          <div class="stat-value">{{ stats.processing }}</div>
          <div class="stat-label">处理中</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="4">
        <el-card class="stat-card waiting" @click="filterStatus = 'waiting'">
          <div class="stat-value">{{ stats.waiting }}</div>
          <div class="stat-label">待回复</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="4">
        <el-card class="stat-card escalated" @click="filterStatus = 'escalated'">
          <div class="stat-value">{{ stats.escalated }}</div>
          <div class="stat-label">已升级</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="4">
        <el-card class="stat-card resolved" @click="filterStatus = 'resolved'">
          <div class="stat-value">{{ stats.resolved }}</div>
          <div class="stat-label">已解决</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-row :gutter="16" align="middle">
        <el-col :xs="24" :sm="8" :md="6">
          <el-input
            v-model="searchKeyword"
            placeholder="工单号/客户/问题描述"
            :prefix-icon="Search"
            clearable
          />
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-select v-model="filterPriority" placeholder="优先级" clearable>
            <el-option label="全部优先级" value="" />
            <el-option label="🔴 紧急" value="urgent" />
            <el-option label="🟠 高" value="high" />
            <el-option label="🟡 中" value="medium" />
            <el-option label="🟢 低" value="low" />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-select v-model="filterType" placeholder="工单类型" clearable>
            <el-option label="全部类型" value="" />
            <el-option label="售后问题" value="aftersales" />
            <el-option label="投诉建议" value="complaint" />
            <el-option label="技术问题" value="technical" />
            <el-option label="物流问题" value="logistics" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="6" :md="4">
          <el-select v-model="filterAssignee" placeholder="处理人" clearable>
            <el-option label="全部" value="" />
            <el-option label="待分配" value="unassigned" />
            <el-option label="我的工单" value="me" />
            <el-option v-for="agent in agents" :key="agent.id" :label="agent.name" :value="agent.id" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="6" :md="6">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 工单列表 -->
    <el-card class="ticket-list-card">
      <el-table :data="filteredTickets" v-loading="loading" stripe @row-click="handleRowClick">
        <el-table-column label="工单信息" min-width="280">
          <template #default="{ row }">
            <div class="ticket-info">
              <div class="ticket-header">
                <span class="ticket-no">{{ row.ticketNo }}</span>
                <el-tag :type="getPriorityType(row.priority)" size="small">
                  {{ getPriorityText(row.priority) }}
                </el-tag>
                <el-tag :type="getStatusType(row.status)" size="small" effect="plain">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </div>
              <div class="ticket-title">{{ row.title }}</div>
              <div class="ticket-meta">
                <span class="type">{{ getTypeText(row.type) }}</span>
                <span class="divider">|</span>
                <span class="customer">{{ row.customerName }}</span>
                <span class="divider">|</span>
                <span class="time">{{ formatTime(row.createTime) }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="关联订单" width="180">
          <template #default="{ row }">
            <div v-if="row.orderNo" class="order-link">
              <span class="platform-icon">{{ getPlatformIcon(row.platform) }}</span>
              <span class="order-no">{{ row.orderNo }}</span>
            </div>
            <span v-else class="no-order">-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="处理人" width="120">
          <template #default="{ row }">
            <div class="assignee">
              <el-avatar :size="24" :src="row.assigneeAvatar">
                {{ row.assigneeName?.charAt(0) }}
              </el-avatar>
              <span>{{ row.assigneeName || '待分配' }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="时效" width="120">
          <template #default="{ row }">
            <div class="sla" :class="getSlaClass(row)">
              <el-icon><Timer /></el-icon>
              <span>{{ getSlaText(row) }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending' && !row.assigneeId" type="primary" size="small" @click.stop="handleClaim(row)">认领</el-button>
            <el-button v-if="canTransfer(row)" type="warning" link size="small" @click.stop="handleTransfer(row)">转交</el-button>
            <el-button v-if="canEscalate(row)" type="danger" link size="small" @click.stop="handleEscalate(row)">升级</el-button>
            <el-button type="primary" link size="small" @click.stop="handleProcess(row)">{{ row.status === 'resolved' ? '查看' : '处理' }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50]" :total="total" layout="total, sizes, prev, pager, next" />
      </div>
    </el-card>

    <!-- 创建工单对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建工单" width="600px">
      <el-form :model="createForm" label-width="100px" :rules="createRules">
        <el-form-item label="关联客户" prop="customerId">
          <el-select v-model="createForm.customerId" filterable placeholder="搜索客户">
            <el-option v-for="c in customers" :key="c.id" :label="c.name + ' (' + c.phone + ')'" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="工单类型" prop="type">
          <el-radio-group v-model="createForm.type">
            <el-radio-button label="aftersales">售后问题</el-radio-button>
            <el-radio-button label="complaint">投诉建议</el-radio-button>
            <el-radio-button label="technical">技术问题</el-radio-button>
            <el-radio-button label="logistics">物流问题</el-radio-button>
            <el-radio-button label="other">其他</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="createForm.priority">
            <el-radio-button label="urgent">🔴 紧急</el-radio-button>
            <el-radio-button label="high">🟠 高</el-radio-button>
            <el-radio-button label="medium">🟡 中</el-radio-button>
            <el-radio-button label="low">🟢 低</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="问题描述" prop="description">
          <el-input v-model="createForm.description" type="textarea" rows="4" placeholder="请详细描述问题..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- 处理工单对话框 -->
    <el-dialog v-model="showProcessDialog" title="处理工单" width="700px">
      <div v-if="currentTicket" class="ticket-detail">
        <div class="detail-header">
          <div class="detail-title">
            <span class="ticket-no">{{ currentTicket.ticketNo }}</span>
            <el-tag :type="getPriorityType(currentTicket.priority)">{{ getPriorityText(currentTicket.priority) }}</el-tag>
          </div>
          <div class="detail-meta">
            <span>客户：{{ currentTicket.customerName }}</span>
            <span>创建：{{ currentTicket.createTime }}</span>
          </div>
        </div>
        <el-card class="description-card">
          <template #header><span>问题描述</span></template>
          <p>{{ currentTicket.description }}</p>
        </el-card>
        <div class="reply-box" v-if="currentTicket.status !== 'resolved'">
          <el-input v-model="replyContent" type="textarea" rows="4" placeholder="输入处理回复..." />
          <div class="reply-actions">
            <el-checkbox v-model="replyForm.notifyCustomer">通知客户</el-checkbox>
            <el-button type="primary" @click="submitReply">提交回复</el-button>
            <el-button type="success" @click="resolveTicket">标记解决</el-button>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 转交对话框 -->
    <el-dialog v-model="showTransferDialog" title="转交工单" width="400px">
      <el-form :model="transferForm" label-width="80px">
        <el-form-item label="转交给">
          <el-select v-model="transferForm.assigneeId" placeholder="选择处理人">
            <el-option v-for="agent in agents.filter(a => a.id !== currentTicket?.assigneeId)" :key="agent.id" :label="agent.name" :value="agent.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="转交说明">
          <el-input v-model="transferForm.remark" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTransferDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmTransfer">确认转交</el-button>
      </template>
    </el-dialog>

    <!-- 升级对话框 -->
    <el-dialog v-model="showEscalateDialog" title="升级工单" width="400px">
      <el-alert title="升级说明" description="升级后工单将转交至主管处理，并标记为高优先级" type="warning" :closable="false" style="margin-bottom: 20px" />
      <el-form :model="escalateForm" label-width="80px">
        <el-form-item label="升级原因">
          <el-input v-model="escalateForm.reason" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEscalateDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmEscalate">确认升级</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search, Timer } from '@element-plus/icons-vue'
import { getPlatformIcon } from '@/config/platforms'

const stats = ref({ total: 156, pending: 23, processing: 45, waiting: 18, escalated: 12, resolved: 58 })
const searchKeyword = ref('')
const filterPriority = ref('')
const filterType = ref('')
const filterAssignee = ref('')
const filterStatus = ref('all')
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(156)

const showCreateDialog = ref(false)
const showProcessDialog = ref(false)
const showTransferDialog = ref(false)
const showEscalateDialog = ref(false)
const currentTicket = ref<any>(null)

const createForm = ref({ customerId: '', orderId: '', type: 'aftersales', priority: 'medium', description: '' })
const createRules = {
  customerId: [{ required: true, message: '请选择客户', trigger: 'change' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
  description: [{ required: true, message: '请描述问题', trigger: 'blur' }]
}

const replyContent = ref('')
const replyForm = ref({ notifyCustomer: true })
const transferForm = ref({ assigneeId: '', remark: '' })
const escalateForm = ref({ reason: '' })

const agents = ref([{ id: '1', name: '张三', avatar: '' }, { id: '2', name: '李四', avatar: '' }, { id: '3', name: '王五', avatar: '' }])
const customers = ref([{ id: '1', name: '客户A', phone: '138****8888' }, { id: '2', name: '客户B', phone: '139****6666' }])

const tickets = ref([
  { id: '1', ticketNo: 'TK20240323001', title: '商品质量问题，要求退货退款', type: 'aftersales', priority: 'high', status: 'pending', customerId: '1', customerName: '客户A', orderNo: 'TB202403230001', platform: 'taobao', assigneeId: '', assigneeName: '', assigneeAvatar: '', createTime: '2024-03-23 10:30:00', slaDeadline: '2024-03-23 14:30:00', description: '收到的商品有破损，包装完好，应该是发货前就有的问题。要求退货退款。' },
  { id: '2', ticketNo: 'TK20240323002', title: '物流显示已签收但未收到', type: 'logistics', priority: 'urgent', status: 'processing', customerId: '2', customerName: '客户B', orderNo: 'JD202403230002', platform: 'jd', assigneeId: '1', assigneeName: '张三', assigneeAvatar: '', createTime: '2024-03-23 09:15:00', slaDeadline: '2024-03-23 11:15:00', description: '物流信息显示已签收，但我没有收到包裹，请帮忙查询。' },
  { id: '3', ticketNo: 'TK20240323003', title: '对客服态度不满意，要求投诉', type: 'complaint', priority: 'medium', status: 'escalated', customerId: '1', customerName: '客户A', orderNo: '', platform: '', assigneeId: '2', assigneeName: '李四', assigneeAvatar: '', createTime: '2024-03-22 16:00:00', slaDeadline: '2024-03-23 16:00:00', description: '之前的客服回复太慢，态度也不好，我要投诉。' }
])

const filteredTickets = computed(() => {
  let result = tickets.value
  if (filterStatus.value && filterStatus.value !== 'all') result = result.filter(t => t.status === filterStatus.value)
  if (filterPriority.value) result = result.filter(t => t.priority === filterPriority.value)
  if (filterType.value) result = result.filter(t => t.type === filterType.value)
  if (filterAssignee.value) {
    if (filterAssignee.value === 'unassigned') result = result.filter(t => !t.assigneeId)
    else if (filterAssignee.value === 'me') result = result.filter(t => t.assigneeId === '1')
    else result = result.filter(t => t.assigneeId === filterAssignee.value)
  }
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(t => t.ticketNo.toLowerCase().includes(keyword) || t.title.includes(keyword) || t.customerName.includes(keyword))
  }
  return result
})

const getPriorityType = (p: string) => ({ urgent: 'danger', high: 'warning', medium: 'primary', low: 'info' }[p] || 'info')
const getPriorityText = (p: string) => ({ urgent: '紧急', high: '高', medium: '中', low: '低' }[p] || p)
const getStatusType = (s: string) => ({ pending: 'info', processing: 'primary', waiting: 'warning', escalated: 'danger', resolved: 'success' }[s] || 'info')
const getStatusText = (s: string) => ({ pending: '待处理', processing: '处理中', waiting: '待回复', escalated: '已升级', resolved: '已解决' }[s] || s)
const getTypeText = (t: string) => ({ aftersales: '售后问题', complaint: '投诉建议', technical: '技术问题', logistics: '物流问题', other: '其他' }[t] || t)
const formatTime = (time: string) => time.split(' ')[0].slice(5)

const getSlaClass = (ticket: any) => {
  const diff = new Date(ticket.slaDeadline).getTime() - new Date().getTime()
  if (diff < 0) return 'overdue'
  if (diff < 3600000) return 'urgent'
  return 'normal'
}

const getSlaText = (ticket: any) => {
  const diff = new Date(ticket.slaDeadline).getTime() - new Date().getTime()
  if (diff < 0) return `已超时${Math.abs(Math.floor(diff / 3600000))}h`
  return `${Math.floor(diff / 3600000)}h${Math.floor((diff % 3600000) / 60000)}m`
}

const canTransfer = (t: any) => ['pending', 'processing', 'waiting'].includes(t.status) && t.assigneeId
const canEscalate = (t: any) => ['pending', 'processing', 'waiting'].includes(t.status) && t.priority !== 'urgent'

const handleSearch = () => ElMessage.success('查询成功')
const resetFilter = () => { searchKeyword.value = ''; filterPriority.value = ''; filterType.value = ''; filterAssignee.value = ''; filterStatus.value = 'all' }
const handleRowClick = (row: any) => { currentTicket.value = row; showProcessDialog.value = true }
const handleClaim = (row: any) => { row.assigneeId = '1'; row.assigneeName = '当前用户'; row.status = 'processing'; ElMessage.success('认领成功') }
const handleTransfer = (row: any) => { currentTicket.value = row; showTransferDialog.value = true }
const confirmTransfer = () => { ElMessage.success('转交成功'); showTransferDialog.value = false }
const handleEscalate = (row: any) => { currentTicket.value = row; showEscalateDialog.value = true }
const confirmEscalate = () => { currentTicket.value.status = 'escalated'; currentTicket.value.priority = 'urgent'; ElMessage.success('升级成功'); showEscalateDialog.value = false }
const handleProcess = (row: any) => { currentTicket.value = row; showProcessDialog.value = true }
const submitCreate = () => { ElMessage.success('工单创建成功'); showCreateDialog.value = false }
const submitReply = () => { ElMessage.success('回复已提交'); replyContent.value = '' }
const resolveTicket = () => { currentTicket.value.status = 'resolved'; ElMessage.success('工单已解决'); showProcessDialog.value = false }
</script>

<style scoped>
.ticket-center { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left h2 { margin: 0 0 8px 0; }
.subtitle { color: #909399; margin: 0; }
.stats-row { margin-bottom: 20px; }
.stat-card { text-align: center; cursor: pointer; transition: all 0.3s; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.stat-card.pending { border-top: 3px solid #909399; }
.stat-card.processing { border-top: 3px solid #409eff; }
.stat-card.waiting { border-top: 3px solid #e6a23c; }
.stat-card.escalated { border-top: 3px solid #f56c6c; }
.stat-card.resolved { border-top: 3px solid #67c23a; }
.stat-value { font-size: 24px; font-weight: bold; color: #303133; margin-bottom: 4px; }
.stat-label { font-size: 14px; color: #909399; }
.filter-card { margin-bottom: 20px; }
.ticket-list-card { margin-bottom: 20px; }
.ticket-info { display: flex; flex-direction: column; gap: 8px; }
.ticket-header { display: flex; align-items: center; gap: 8px; }
.ticket-no { font-family: monospace; font-weight: 500; color: #606266; }
.ticket-title { font-size: 14px; color: #303133; font-weight: 500; }
.ticket-meta { font-size: 12px; color: #909399; display: flex; align-items: center; gap: 8px; }
.ticket-meta .divider { color: #dcdfe6; }
.order-link { display: flex; align-items: center; gap: 6px; }
.order-link .platform-icon { font-size: 14px; }
.order-link .order-no { font-family: monospace; font-size: 13px; color: #606266; }
.no-order { color: #909399; }
.assignee { display: flex; align-items: center; gap: 6px; }
.sla { display: flex; align-items: center; gap: 4px; font-size: 13px; }
.sla.normal { color: #67c23a; }
.sla.urgent { color: #e6a23c; }
.sla.overdue { color: #f56c6c; font-weight: bold; }
.pagination { display: flex; justify-content: flex-end; margin-top: 20px; }
.ticket-detail { padding: 20px; }
.detail-header { margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #ebeef5; }
.detail-title { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.detail-title .ticket-no { font-size: 18px; font-weight: bold; }
.detail-meta { display: flex; gap: 20px; color: #909399; font-size: 13px; }
.description-card { margin-bottom: 20px; }
.description-card p { line-height: 1.8; color: #606266; }
.reply-box { margin-top: 20px; padding-top: 20px; border-top: 1px solid #ebeef5; }
.reply-actions { display: flex; justify-content: space-between; margin-top: 10px; }
</style>
