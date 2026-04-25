<template>
  <div class="agent-settings">
    <el-page-header title="智能体设置" @back="goBack">
      <template #content>
        <span class="page-title">智能体设置</span>
        <el-tag type="info" size="small" style="margin-left: 12px;">配置智能体角色、职务及店铺权限</el-tag>
      </template>
    </el-page-header>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 角色设置 -->
          <el-tab-pane label="角色设置" name="role">
            <div class="tab-header">
              <el-button type="primary" @click="showAddRole = true">
                <el-icon><Plus /></el-icon> 新增角色
              </el-button>
            </div>
            
            <el-table :data="roles" style="margin-top: 16px;" border>
              <el-table-column prop="name" label="角色名称" min-width="150" />
              <el-table-column prop="description" label="角色描述" min-width="200" />
              <el-table-column prop="permissions" label="权限范围" min-width="300">
                <template #default="{ row }">
                  <el-tag 
                    v-for="perm in row.permissions" 
                    :key="perm"
                    size="small"
                    style="margin-right: 6px; margin-bottom: 4px;"
                  >
                    {{ perm }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="agentCount" label="智能体数量" width="120" align="center" />
              <el-table-column label="操作" width="180" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link @click="editRole(row)">编辑</el-button>
                  <el-button type="primary" link @click="configRolePermissions(row)">权限配置</el-button>
                  <el-button type="danger" link @click="deleteRole(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          
          <!-- 职务设置 -->
          <el-tab-pane label="职务设置" name="position">
            <div class="tab-header">
              <el-button type="primary" @click="showAddPosition = true">
                <el-icon><Plus /></el-icon> 新增职务
              </el-button>
            </div>
            
            <el-table :data="positions" style="margin-top: 16px;" border>
              <el-table-column prop="name" label="职务名称" min-width="150" />
              <el-table-column prop="level" label="职务等级" width="120">
                <template #default="{ row }">
                  <el-tag :type="getLevelType(row.level)">{{ row.level }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="职务描述" min-width="200" />
              <el-table-column prop="responsibilities" label="职责范围" min-width="250">
                <template #default="{ row }">
                  <el-tag 
                    v-for="resp in row.responsibilities" 
                    :key="resp"
                    type="info"
                    size="small"
                    style="margin-right: 6px; margin-bottom: 4px;"
                  >
                    {{ resp }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="agentCount" label="智能体数量" width="120" align="center" />
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link @click="editPosition(row)">编辑</el-button>
                  <el-button type="danger" link @click="deletePosition(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          
          <!-- 店铺权限设置 -->
          <el-tab-pane label="店铺权限设置" name="shop-permissions">
            <div class="permission-notice" style="margin-bottom: 16px;">
              <el-alert
                title="店铺权限说明"
                type="info"
                :closable="false"
                show-icon
              >
                <template #default>
                  <div>
                    <p>1. 店铺权限决定智能体可以访问和操作哪些店铺的订单、商品、客户数据</p>
                    <p>2. 权限属性需要与各电商平台API的店铺权限相匹配（部分平台需要API授权）</p>
                    <p>3. 每个店铺可独立配置智能体的操作权限范围</p>
                  </div>
                </template>
              </el-alert>
            </div>
            
            <div class="tab-header">
              <el-button type="primary" @click="syncPlatformPermissions">
                <el-icon><Refresh /></el-icon> 同步平台权限
              </el-button>
              <el-button @click="showBatchConfig = true">
                批量配置
              </el-button>
            </div>
            
            <el-table :data="shopPermissions" style="margin-top: 16px;" border>
              <el-table-column prop="shopName" label="店铺名称" min-width="180" />
              <el-table-column prop="platform" label="所属平台" width="120">
                <template #default="{ row }">
                  <el-tag :type="getPlatformType(row.platform)" size="small">{{ row.platform }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="shopId" label="店铺ID" width="150" />
              <el-table-column prop="permissions" label="智能体权限" min-width="300">
                <template #default="{ row }">
                  <el-checkbox-group v-model="row.permissions" @change="updateShopPermissions(row)">
                    <el-checkbox label="view_orders">查看订单</el-checkbox>
                    <el-checkbox label="modify_orders">修改订单</el-checkbox>
                    <el-checkbox label="view_products">查看商品</el-checkbox>
                    <el-checkbox label="modify_products">修改商品</el-checkbox>
                    <el-checkbox label="reply_messages">回复消息</el-checkbox>
                    <el-checkbox label="view_customers">查看客户</el-checkbox>
                  </el-checkbox-group>
                </template>
              </el-table-column>
              <el-table-column prop="syncStatus" label="同步状态" width="120">
                <template #default="{ row }">
                  <el-tag :type="row.syncStatus === 'synced' ? 'success' : 'warning'" size="small">
                    {{ row.syncStatus === 'synced' ? '已同步' : '未同步' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link @click="editShopPermissions(row)">编辑</el-button>
                  <el-button type="primary" link @click="syncSingleShop(row)">同步</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          
          <!-- 智能体列表 -->
          <el-tab-pane label="智能体管理" name="agents">
            <div class="tab-header">
              <el-button type="primary" @click="showAddAgent = true">
                <el-icon><Plus /></el-icon> 新增智能体
              </el-button>
            </div>
            
            <el-table :data="agents" style="margin-top: 16px;" border>
              <el-table-column prop="name" label="智能体名称" min-width="150" />
              <el-table-column prop="role" label="所属角色" width="120">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.role }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="position" label="职务" width="120" />
              <el-table-column prop="assignedShops" label="分配店铺" min-width="200">
                <template #default="{ row }">
                  <el-tag 
                    v-for="shop in row.assignedShops.slice(0, 3)" 
                    :key="shop"
                    type="info"
                    size="small"
                    style="margin-right: 6px; margin-bottom: 4px;"
                  >
                    {{ shop }}
                  </el-tag>
                  <el-tag v-if="row.assignedShops.length > 3" type="info" size="small">
                    +{{ row.assignedShops.length - 3 }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-switch
                    v-model="row.status"
                    active-value="active"
                    inactive-value="inactive"
                    @change="toggleAgentStatus(row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link @click="editAgent(row)">编辑</el-button>
                  <el-button type="primary" link @click="configAgentShops(row)">店铺配置</el-button>
                  <el-button type="danger" link @click="deleteAgent(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>
    
    <!-- 新增角色对话框 -->
    <el-dialog v-model="showAddRole" title="新增角色" width="500px">
      <el-form :model="roleForm" label-width="100px">
        <el-form-item label="角色名称" required>
          <el-input v-model="roleForm.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色描述">
          <el-input v-model="roleForm.description" type="textarea" :rows="3" placeholder="请输入角色描述" />
        </el-form-item>
        <el-form-item label="权限范围">
          <el-checkbox-group v-model="roleForm.permissions">
            <el-checkbox label="view_all">查看全部</el-checkbox>
            <el-checkbox label="manage_orders">订单管理</el-checkbox>
            <el-checkbox label="manage_products">商品管理</el-checkbox>
            <el-checkbox label="manage_customers">客户管理</el-checkbox>
            <el-checkbox label="reply_messages">消息回复</el-checkbox>
            <el-checkbox label="view_reports">查看报表</el-checkbox>
            <el-checkbox label="system_config">系统配置</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddRole = false">取消</el-button>
        <el-button type="primary" @click="saveRole">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 新增职务对话框 -->
    <el-dialog v-model="showAddPosition" title="新增职务" width="500px">
      <el-form :model="positionForm" label-width="100px">
        <el-form-item label="职务名称" required>
          <el-input v-model="positionForm.name" placeholder="请输入职务名称" />
        </el-form-item>
        <el-form-item label="职务等级">
          <el-select v-model="positionForm.level" style="width: 100%">
            <el-option label="初级" value="初级" />
            <el-option label="中级" value="中级" />
            <el-option label="高级" value="高级" />
            <el-option label="专家" value="专家" />
          </el-select>
        </el-form-item>
        <el-form-item label="职务描述">
          <el-input v-model="positionForm.description" type="textarea" :rows="3" placeholder="请输入职务描述" />
        </el-form-item>
        <el-form-item label="职责范围">
          <el-checkbox-group v-model="positionForm.responsibilities">
            <el-checkbox label="售前咨询">售前咨询</el-checkbox>
            <el-checkbox label="售后处理">售后处理</el-checkbox>
            <el-checkbox label="投诉处理">投诉处理</el-checkbox>
            <el-checkbox label="订单跟进">订单跟进</el-checkbox>
            <el-checkbox label="客户维护">客户维护</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddPosition = false">取消</el-button>
        <el-button type="primary" @click="savePosition">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 新增智能体对话框 -->
    <el-dialog v-model="showAddAgent" title="新增智能体" width="500px">
      <el-form :model="agentForm" label-width="100px">
        <el-form-item label="智能体名称" required>
          <el-input v-model="agentForm.name" placeholder="请输入智能体名称" />
        </el-form-item>
        <el-form-item label="所属角色">
          <el-select v-model="agentForm.role" style="width: 100%">
            <el-option v-for="role in roles" :key="role.name" :label="role.name" :value="role.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="职务">
          <el-select v-model="agentForm.position" style="width: 100%">
            <el-option v-for="pos in positions" :key="pos.name" :label="pos.name" :value="pos.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="分配店铺">
          <el-select v-model="agentForm.assignedShops" multiple style="width: 100%">
            <el-option 
              v-for="shop in allShops" 
              :key="shop.shopId" 
              :label="shop.shopName" 
              :value="shop.shopName" 
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddAgent = false">取消</el-button>
        <el-button type="primary" @click="saveAgent">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'

const router = useRouter()

const goBack = () => {
  router.push('/dashboard')
}

// 当前标签页
const activeTab = ref('role')

// 角色数据
const roles = ref([
  { 
    name: '超级管理员', 
    description: '拥有系统所有权限', 
    permissions: ['查看全部', '订单管理', '商品管理', '客户管理', '消息回复', '查看报表', '系统配置'],
    agentCount: 1
  },
  { 
    name: '客服主管', 
    description: '负责客服团队管理和质量监控', 
    permissions: ['查看全部', '订单管理', '客户管理', '消息回复', '查看报表'],
    agentCount: 2
  },
  { 
    name: '售前客服', 
    description: '负责售前咨询和商品推荐', 
    permissions: ['查看商品', '消息回复', '查看客户'],
    agentCount: 5
  },
  { 
    name: '售后客服', 
    description: '负责售后处理和投诉解决', 
    permissions: ['订单管理', '消息回复', '查看客户'],
    agentCount: 3
  }
])

// 职务数据
const positions = ref([
  { name: '客服专员', level: '初级', description: '处理日常客户咨询', responsibilities: ['售前咨询', '售后处理'], agentCount: 6 },
  { name: '高级客服', level: '中级', description: '处理复杂问题和投诉', responsibilities: ['售前咨询', '售后处理', '投诉处理'], agentCount: 3 },
  { name: '客服主管', level: '高级', description: '团队管理和质量监控', responsibilities: ['投诉处理', '订单跟进', '客户维护'], agentCount: 2 },
  { name: '客服经理', level: '专家', description: '整体运营和策略制定', responsibilities: ['投诉处理', '客户维护'], agentCount: 1 }
])

// 店铺权限数据
const shopPermissions = ref([
  { shopName: '科技云旗舰店', platform: '淘宝', shopId: 'TB123456', permissions: ['view_orders', 'modify_orders', 'reply_messages', 'view_customers'], syncStatus: 'synced' },
  { shopName: '科技云数码店', platform: '京东', shopId: 'JD789012', permissions: ['view_orders', 'reply_messages'], syncStatus: 'synced' },
  { shopName: '科技云生活馆', platform: '拼多多', shopId: 'PDD345678', permissions: ['view_orders', 'view_products', 'reply_messages'], syncStatus: 'unsynced' },
  { shopName: '科技云海外店', platform: '天猫国际', shopId: 'TMG901234', permissions: ['view_orders', 'modify_orders', 'view_products', 'reply_messages'], syncStatus: 'synced' }
])

// 所有店铺
const allShops = ref([
  { shopName: '科技云旗舰店', shopId: 'TB123456' },
  { shopName: '科技云数码店', shopId: 'JD789012' },
  { shopName: '科技云生活馆', shopId: 'PDD345678' },
  { shopName: '科技云海外店', shopId: 'TMG901234' }
])

// 智能体数据
const agents = ref([
  { name: '小云助手', role: '售前客服', position: '客服专员', assignedShops: ['科技云旗舰店', '科技云数码店'], status: 'active' },
  { name: '小智助手', role: '售后客服', position: '高级客服', assignedShops: ['科技云旗舰店', '科技云生活馆'], status: 'active' },
  { name: '小慧助手', role: '客服主管', position: '客服主管', assignedShops: ['科技云旗舰店', '科技云数码店', '科技云生活馆', '科技云海外店'], status: 'active' }
])

// 对话框显示状态
const showAddRole = ref(false)
const showAddPosition = ref(false)
const showAddAgent = ref(false)
const showBatchConfig = ref(false)

// 表单数据
const roleForm = ref({ name: '', description: '', permissions: [] })
const positionForm = ref({ name: '', level: '初级', description: '', responsibilities: [] })
const agentForm = ref({ name: '', role: '', position: '', assignedShops: [] })

// 获取平台标签类型
const getPlatformType = (platform: string) => {
  const typeMap: Record<string, string> = {
    '淘宝': 'danger',
    '天猫': 'danger',
    '天猫国际': 'danger',
    '京东': 'primary',
    '拼多多': 'success',
    '抖音': 'warning',
    '快手': 'warning'
  }
  return typeMap[platform] || 'info'
}

// 获取等级标签类型
const getLevelType = (level: string) => {
  const typeMap: Record<string, string> = {
    '初级': 'info',
    '中级': 'success',
    '高级': 'warning',
    '专家': 'danger'
  }
  return typeMap[level] || 'info'
}

// 保存角色
const saveRole = () => {
  ElMessage.success('角色保存成功')
  showAddRole.value = false
  roleForm.value = { name: '', description: '', permissions: [] }
}

// 编辑角色
const editRole = (row: any) => {
  ElMessage.info('编辑角色: ' + row.name)
}

// 配置角色权限
const configRolePermissions = (row: any) => {
  ElMessage.info('配置角色权限: ' + row.name)
}

// 删除角色
const deleteRole = (row: any) => {
  ElMessageBox.confirm('确定要删除该角色吗？', '提示', { type: 'warning' })
    .then(() => {
      ElMessage.success('角色删除成功')
    })
}

// 保存职务
const savePosition = () => {
  ElMessage.success('职务保存成功')
  showAddPosition.value = false
  positionForm.value = { name: '', level: '初级', description: '', responsibilities: [] }
}

// 编辑职务
const editPosition = (row: any) => {
  ElMessage.info('编辑职务: ' + row.name)
}

// 删除职务
const deletePosition = (row: any) => {
  ElMessageBox.confirm('确定要删除该职务吗？', '提示', { type: 'warning' })
    .then(() => {
      ElMessage.success('职务删除成功')
    })
}

// 同步平台权限
const syncPlatformPermissions = () => {
  ElMessage.info('正在同步平台权限...')
  setTimeout(() => {
    ElMessage.success('平台权限同步完成')
  }, 2000)
}

// 同步单个店铺
const syncSingleShop = (row: any) => {
  ElMessage.info('正在同步店铺: ' + row.shopName)
  setTimeout(() => {
    row.syncStatus = 'synced'
    ElMessage.success('店铺权限同步完成')
  }, 1500)
}

// 更新店铺权限
const updateShopPermissions = (row: any) => {
  row.syncStatus = 'unsynced'
  ElMessage.success('权限已更新，请同步到平台')
}

// 编辑店铺权限
const editShopPermissions = (row: any) => {
  ElMessage.info('编辑店铺权限: ' + row.shopName)
}

// 保存智能体
const saveAgent = () => {
  ElMessage.success('智能体保存成功')
  showAddAgent.value = false
  agentForm.value = { name: '', role: '', position: '', assignedShops: [] }
}

// 编辑智能体
const editAgent = (row: any) => {
  ElMessage.info('编辑智能体: ' + row.name)
}

// 配置智能体店铺
const configAgentShops = (row: any) => {
  ElMessage.info('配置智能体店铺: ' + row.name)
}

// 删除智能体
const deleteAgent = (row: any) => {
  ElMessageBox.confirm('确定要删除该智能体吗？', '提示', { type: 'warning' })
    .then(() => {
      ElMessage.success('智能体删除成功')
    })
}

// 切换智能体状态
const toggleAgentStatus = (row: any) => {
  ElMessage.success(`智能体已${row.status === 'active' ? '启用' : '禁用'}`)
}
</script>

<style scoped>
.agent-settings {
  padding: 20px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.tab-header {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.permission-notice {
  margin-bottom: 16px;
}

.permission-notice p {
  margin: 4px 0;
  font-size: 13px;
}
</style>
