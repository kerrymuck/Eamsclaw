<template>
  <div class="knowledge">
    <!-- 1. 知识库平台管理 -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>📚 知识库平台管理</span>
          <span style="color: #909399; font-size: 14px">支持32个全球电商平台</span>
        </div>
      </template>
      <div class="platform-filter">
        <el-radio-group v-model="selectedPlatform" size="small">
          <el-radio-button label="all">全部平台</el-radio-button>
        </el-radio-group>
        
        <!-- 国内电商平台 -->
        <div class="platform-category">
          <span class="category-label">国内电商：</span>
          <el-radio-group v-model="selectedPlatform" size="small">
            <el-radio-button v-for="platform in domesticPlatforms" :key="platform.id" :label="platform.id">
              {{ platform.icon }} {{ platform.name }}
            </el-radio-button>
          </el-radio-group>
        </div>
        
        <!-- 跨境电商平台 -->
        <div class="platform-category">
          <span class="category-label">跨境电商：</span>
          <el-radio-group v-model="selectedPlatform" size="small">
            <el-radio-button v-for="platform in crossborderPlatforms" :key="platform.id" :label="platform.id">
              {{ platform.icon }} {{ platform.name }}
            </el-radio-button>
          </el-radio-group>
        </div>
        
        <!-- B2B平台 -->
        <div class="platform-category">
          <span class="category-label">B2B平台：</span>
          <el-radio-group v-model="selectedPlatform" size="small">
            <el-radio-button v-for="platform in b2bPlatforms" :key="platform.id" :label="platform.id">
              {{ platform.icon }} {{ platform.name }}
            </el-radio-button>
          </el-radio-group>
        </div>
        
        <!-- 独立站平台 -->
        <div class="platform-category">
          <span class="category-label">独立站：</span>
          <el-radio-group v-model="selectedPlatform" size="small">
            <el-radio-button v-for="platform in independentPlatforms" :key="platform.id" :label="platform.id">
              {{ platform.icon }} {{ platform.name }}
            </el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </el-card>

    <!-- 2. 通用知识库设置 -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>📖 通用知识库设置</span>
          <span style="color: #909399; font-size: 14px">配置通用知识分类和条目</span>
        </div>
      </template>
      <el-row :gutter="20">
        <!-- 左侧分类 -->
        <el-col :span="6">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>知识分类</span>
                <el-button type="primary" size="small" @click="showAddCategory = true">
                  <el-icon><Plus /></el-icon> 新增
                </el-button>
              </div>
            </template>
            
            <el-tree
              :data="mockStore.categories"
              :props="{ label: 'name', children: 'children' }"
              @node-click="handleCategoryClick"
              highlight-current
              default-expand-all
            >
              <template #default="{ node, data }">
                <span class="tree-node">
                  <span>{{ node.label }}</span>
                  <span class="actions">
                    <el-button type="primary" link size="small" @click.stop="editCategory(data)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button type="danger" link size="small" @click.stop="deleteCategory(data)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </span>
                </span>
              </template>
            </el-tree>
          </el-card>
        </el-col>
        
        <!-- 右侧条目列表 -->
        <el-col :span="18">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>
                  知识条目
                  <el-tag v-if="currentCategory" type="info" style="margin-left: 10px">
                    {{ currentCategory.name }}
                  </el-tag>
                </span>
                <div>
                  <el-input
                    v-model="searchQuery"
                    placeholder="搜索知识"
                    :prefix-icon="Search"
                    style="width: 200px; margin-right: 10px"
                    clearable
                  />
                  <el-button type="primary" @click="showAddEntry = true">
                    <el-icon><Plus /></el-icon> 新增条目
                  </el-button>
                </div>
              </div>
            </template>
            
            <el-table :data="filteredEntries" v-loading="loading" stripe>
              <el-table-column type="index" width="50" />
              <el-table-column prop="question" label="问题" min-width="200" show-overflow-tooltip />
              <el-table-column prop="answer" label="答案" min-width="300" show-overflow-tooltip>
                <template #default="{ row }">
                  <el-text line-clamp="2">{{ row.answer }}</el-text>
                </template>
              </el-table-column>
              <el-table-column prop="category_name" label="分类" width="120">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.category_name }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="关键词" width="150">
                <template #default="{ row }">
                  <el-tag 
                    v-for="kw in row.keywords" 
                    :key="kw" 
                    size="small" 
                    effect="plain"
                    style="margin-right: 5px; margin-bottom: 3px"
                  >
                    {{ kw }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link @click="editEntry(row)">
                    <el-icon><Edit /></el-icon> 编辑
                  </el-button>
                  <el-button type="danger" link @click="deleteEntry(row)">
                    <el-icon><Delete /></el-icon> 删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              :total="mockStore.entries.length"
              layout="total, prev, pager, next"
              style="margin-top: 20px; justify-content: flex-end"
            />
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 3. 行业知识库设置 -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>🏭 行业知识库设置</span>
          <el-button type="primary" size="small" @click="showIndustryDialog = true">
            <el-icon><Plus /></el-icon> 选择行业模板
          </el-button>
        </div>
      </template>
      <div class="industry-section">
        <div class="current-industry" v-if="currentIndustry">
          <el-tag type="success" size="large" effect="dark">
            {{ currentIndustry.icon }} {{ currentIndustry.name }}
          </el-tag>
          <span class="industry-desc">{{ currentIndustry.description }}</span>
          <el-button type="primary" link @click="viewIndustryTemplates">查看模板详情</el-button>
        </div>
        <div class="no-industry" v-else>
          <el-empty description="暂未设置行业属性" :image-size="60">
            <el-button type="primary" @click="showIndustryDialog = true">选择行业</el-button>
          </el-empty>
        </div>
      </div>
    </el-card>
    
    <!-- 添加/编辑分类对话框 -->
    <el-dialog v-model="showAddCategory" title="新增分类" width="500px">
      <el-form :model="categoryForm" label-width="100px">
        <el-form-item label="所属平台">
          <el-select v-model="categoryForm.platform_id" clearable placeholder="通用（所有平台）" style="width: 100%">
            <el-option label="通用（所有平台）" value="" />
            <el-option
              v-for="platform in platforms"
              :key="platform.id"
              :label="platform.icon + ' ' + platform.name"
              :value="platform.id"
            />
          </el-select>
          <div class="form-tip">选择平台后，该分类下的知识仅对该平台生效</div>
        </el-form-item>
        <el-form-item label="分类名称">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="上级分类">
          <el-select v-model="categoryForm.parent_id" clearable placeholder="无（一级分类）" style="width: 100%">
            <el-option
              v-for="cat in flatCategories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddCategory = false">取消</el-button>
        <el-button type="primary" @click="saveCategory">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 行业选择对话框 -->
    <el-dialog v-model="showIndustryDialog" title="选择行业知识库模板" width="800px">
      <div class="industry-grid">
        <el-card 
          v-for="industry in industryTemplates" 
          :key="industry.id"
          class="industry-card"
          :body-style="{ padding: '20px' }"
          shadow="hover"
          @click="selectIndustry(industry)"
        >
          <div class="industry-icon">{{ industry.icon }}</div>
          <div class="industry-name">{{ industry.name }}</div>
          <div class="industry-desc">{{ industry.description }}</div>
          <div class="industry-templates">
            <el-tag 
              v-for="tpl in industry.templates" 
              :key="tpl"
              size="small"
              type="info"
              effect="plain"
              style="margin-right: 6px; margin-bottom: 4px;"
            >
              {{ tpl }}
            </el-tag>
          </div>
        </el-card>
      </div>
      <template #footer>
        <el-button @click="showIndustryDialog = false">取消</el-button>
      </template>
    </el-dialog>

    <!-- 行业模板详情对话框 -->
    <el-dialog v-model="showIndustryDetailDialog" :title="currentIndustry?.name + ' - 知识库模板'" width="900px">
      <div v-if="industryDetailData" class="industry-detail">
        <el-alert
          :title="'以下是' + industryDetailData.name + '的常用知识库内容，您可以参考使用或一键导入'"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
        />
        <el-collapse v-model="activeCollapse">
          <el-collapse-item 
            v-for="(category, index) in industryDetailData.categories" 
            :key="index"
            :title="category.name + ' (' + category.items.length + '条)'"
            :name="index"
          >
            <el-table :data="category.items" style="width: 100%" size="small">
              <el-table-column prop="question" label="问题" min-width="200" show-overflow-tooltip />
              <el-table-column prop="answer" label="答案" min-width="300" show-overflow-tooltip>
                <template #default="{ row }">
                  <el-text line-clamp="2">{{ row.answer }}</el-text>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="useTemplateItem(row)">使用</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </div>
      <template #footer>
        <el-button @click="showIndustryDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="importAllTemplates">一键导入全部</el-button>
      </template>
    </el-dialog>

    <!-- 添加/编辑条目对话框 -->
    <el-dialog v-model="showAddEntry" title="新增知识条目" width="700px">
      <el-form :model="entryForm" label-width="100px">
        <el-form-item label="所属平台">
          <el-select v-model="entryForm.platform_id" clearable placeholder="通用（所有平台）" style="width: 100%">
            <el-option label="通用（所有平台）" value="" />
            <el-option
              v-for="platform in platforms"
              :key="platform.id"
              :label="platform.icon + ' ' + platform.name"
              :value="platform.id"
            />
          </el-select>
          <div class="form-tip">选择平台后，该知识仅对该平台生效</div>
        </el-form-item>
        <el-form-item label="所属分类">
          <el-select v-model="entryForm.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="cat in flatCategories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="问题">
          <el-input 
            v-model="entryForm.question" 
            type="textarea" 
            :rows="2" 
            placeholder="请输入问题"
          />
        </el-form-item>
        <el-form-item label="答案">
          <el-input 
            v-model="entryForm.answer" 
            type="textarea" 
            :rows="6" 
            placeholder="请输入答案"
          />
        </el-form-item>
        <el-form-item label="关键词">
          <el-select
            v-model="entryForm.keywords"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入关键词后按回车"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddEntry = false">取消</el-button>
        <el-button type="primary" @click="saveEntry">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Search, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMockStore } from '@/stores/mock'
import { getAllPlatforms, PLATFORM_CATEGORIES } from '@/config/platforms'

const mockStore = useMockStore()
const allPlatforms = getAllPlatforms()
const selectedPlatform = ref('all')

// 按分类获取平台
const domesticPlatforms = allPlatforms.filter(p => PLATFORM_CATEGORIES.domestic.platforms.includes(p.id))
const crossborderPlatforms = allPlatforms.filter(p => PLATFORM_CATEGORIES.crossborder.platforms.includes(p.id))
const b2bPlatforms = allPlatforms.filter(p => PLATFORM_CATEGORIES.b2b.platforms.includes(p.id))
const independentPlatforms = allPlatforms.filter(p => PLATFORM_CATEGORIES.independent.platforms.includes(p.id))

// 当前行业
const currentIndustry = ref<any>(null)

// 行业模板列表
const industryTemplates = ref([
  { 
    id: 'shoes', 
    name: '鞋服行业', 
    icon: '👟',
    description: '适用于鞋类、服装、配饰等零售店铺',
    templates: ['尺码对照', '面料说明', '退换货政策', '搭配建议']
  },
  { 
    id: 'food', 
    name: '食品行业', 
    icon: '🍔',
    description: '适用于食品、饮料、生鲜等店铺',
    templates: ['保质期说明', '储存条件', '食品安全', '物流冷链']
  },
  { 
    id: 'beauty', 
    name: '美妆护肤', 
    icon: '💄',
    description: '适用于化妆品、护肤品、个护等店铺',
    templates: ['肤质匹配', '成分说明', '使用方法', '过敏测试']
  },
  { 
    id: 'digital', 
    name: '3C数码', 
    icon: '📱',
    description: '适用于手机、电脑、数码配件等店铺',
    templates: ['规格参数', '保修政策', '故障排查', '正品验证']
  },
  { 
    id: 'home', 
    name: '家居日用', 
    icon: '🏠',
    description: '适用于家具、家纺、日用品等店铺',
    templates: ['尺寸规格', '安装说明', '材质说明', '配送服务']
  },
  { 
    id: 'maternal', 
    name: '母婴用品', 
    icon: '👶',
    description: '适用于母婴用品、童装、玩具等店铺',
    templates: ['适用年龄', '安全认证', '材质安全', '使用指导']
  },
  { 
    id: 'sports', 
    name: '运动户外', 
    icon: '⚽',
    description: '适用于运动装备、户外用品等店铺',
    templates: ['尺码推荐', '功能说明', '保养维护', '适用场景']
  },
  { 
    id: 'books', 
    name: '图书文具', 
    icon: '📚',
    description: '适用于图书、文具、办公用品等店铺',
    templates: ['版本信息', '内容摘要', '适用人群', '发货说明']
  }
])

// 显示行业选择对话框
const showIndustryDialog = ref(false)

// 选择行业模板
const selectIndustry = (industry: any) => {
  currentIndustry.value = industry
  showIndustryDialog.value = false
  ElMessage.success(`已选择「${industry.name}」行业模板`)
}

// 查看行业模板详情
const viewIndustryTemplates = () => {
  showIndustryDetailDialog.value = true
}

// 行业模板详情数据
const industryDetailData = ref<any>(null)
const showIndustryDetailDialog = ref(false)

// 加载行业模板详情
const loadIndustryDetail = (industryId: string) => {
  const details: Record<string, any> = {
    'shoes': {
      name: '鞋服行业',
      icon: '👟',
      categories: [
        {
          name: '商品信息',
          items: [
            { question: '这款鞋的尺码偏大还是偏小？', answer: '我们的鞋子为标准尺码，建议按照平时穿着尺码选择。如果您脚宽或脚背高，建议选择大一码。' },
            { question: '衣服的面料是什么材质？', answer: '本款衣服采用100%纯棉面料，柔软舒适，透气性好，适合四季穿着。' },
            { question: '这款包包能装下A4纸吗？', answer: '可以的，这款包包尺寸为30*25*10cm，可以轻松装下A4纸和日常用品。' }
          ]
        },
        {
          name: '售前咨询',
          items: [
            { question: '这件衣服适合什么场合穿？', answer: '这款衣服设计简约大方，适合日常通勤、休闲聚会等多种场合。' },
            { question: '这双鞋透气吗？', answer: '鞋面采用透气网布设计，内里使用吸汗材质，长时间穿着也不会闷脚。' },
            { question: '有搭配建议吗？', answer: '这款上衣可以搭配牛仔裤或休闲裤，鞋子推荐搭配小白鞋或乐福鞋，整体风格简约时尚。' }
          ]
        },
        {
          name: '售后处理',
          items: [
            { question: '鞋子磨脚可以退换吗？', answer: '新鞋可能会有轻微磨脚情况，建议先穿厚袜子适应。如果严重磨脚且未穿过外出，支持7天无理由退换。' },
            { question: '衣服掉色怎么办？', answer: '深色衣物初次洗涤可能会有轻微浮色，属于正常现象。建议反面洗涤，避免暴晒。如严重掉色可联系客服处理。' },
            { question: '尺码不合适可以换吗？', answer: '可以的，我们支持7天无理由换货。请保持商品完好，吊牌齐全，联系客服申请换货即可。' }
          ]
        },
        {
          name: '物流相关',
          items: [
            { question: '什么时候发货？', answer: '下午4点前下单的订单，当天发货；4点后下单的订单，次日发货。' },
            { question: '支持哪些快递？', answer: '默认发中通快递，如需指定其他快递请联系客服。顺丰需补差价。' },
            { question: '偏远地区包邮吗？', answer: '新疆、西藏、青海、内蒙古等地区需补运费差价，具体金额以结算页面为准。' }
          ]
        }
      ]
    },
    'food': {
      name: '食品行业',
      icon: '🍔',
      categories: [
        {
          name: '商品信息',
          items: [
            { question: '这个产品的保质期多久？', answer: '本产品保质期为12个月，生产日期见包装喷码。开封后建议尽快食用完毕。' },
            { question: '需要冷藏保存吗？', answer: '未开封常温保存即可，开封后建议冷藏保存并在7天内食用完毕。' },
            { question: '配料表里有什么？', answer: '主要配料：小麦粉、白砂糖、鸡蛋、黄油。不含防腐剂和人工色素。' }
          ]
        },
        {
          name: '售前咨询',
          items: [
            { question: '这个辣吗？', answer: '这款是微辣口味，辣度适中。如果您不太能吃辣，建议选择原味。' },
            { question: '适合孕妇/小孩吃吗？', answer: '本产品配料天然，无添加剂，孕妇和3岁以上儿童均可食用。但如有特殊体质建议咨询医生。' },
            { question: '一箱有多少个？', answer: '一箱共24包，每包净重30g，整箱净重720g。' }
          ]
        },
        {
          name: '售后处理',
          items: [
            { question: '收到包装破损怎么办？', answer: '如收到商品包装破损，请拍照联系客服，我们会为您补发或退款。' },
            { question: '食品可以退换吗？', answer: '食品类商品因安全考虑，非质量问题不支持退换。如有质量问题，请24小时内联系客服处理。' },
            { question: '发现异物怎么办？', answer: '非常抱歉！如发现有异物，请立即停止食用并拍照联系客服，我们会严肃处理并给您满意答复。' }
          ]
        },
        {
          name: '物流相关',
          items: [
            { question: '生鲜怎么保证新鲜？', answer: '我们采用冷链配送，使用保温箱+冰袋包装，确保商品新鲜送达。' },
            { question: '多久能到货？', answer: '同城次日达，省内1-2天，跨省2-3天。生鲜商品仅限部分地区配送。' },
            { question: '可以指定送货时间吗？', answer: '可以在订单备注中注明，我们会尽量安排。具体以物流实际配送为准。' }
          ]
        }
      ]
    }
  }
  return details[industryId] || null
}

// 监听行业变化，加载详情
watch(() => currentIndustry.value, (newVal) => {
  if (newVal) {
    industryDetailData.value = loadIndustryDetail(newVal.id)
  }
}, { immediate: true })

const loading = ref(false)
const searchQuery = ref('')
const page = ref(1)
const pageSize = ref(10)
const currentCategory = ref<any>(null)

const showAddCategory = ref(false)
const showAddEntry = ref(false)
const categoryForm = ref({ name: '', parent_id: '', platform_id: '' })
const entryForm = ref({
  platform_id: '',
  category_id: '',
  question: '',
  answer: '',
  keywords: []
})

// 扁平化分类列表
const flatCategories = computed(() => {
  const result: any[] = []
  const flatten = (list: any[]) => {
    list.forEach(item => {
      result.push(item)
      if (item.children) {
        flatten(item.children)
      }
    })
  }
  flatten(mockStore.categories)
  return result
})

const filteredEntries = computed(() => {
  let result = mockStore.entries
  
  // 按分类筛选
  if (currentCategory.value) {
    result = result.filter(e => e.category_name === currentCategory.value.name)
  }
  
  // 按关键词搜索
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(e => 
      e.question.toLowerCase().includes(query) ||
      e.answer.toLowerCase().includes(query) ||
      e.keywords.some((k: string) => k.toLowerCase().includes(query))
    )
  }
  
  return result
})

const handleCategoryClick = (data: any) => {
  currentCategory.value = data
}

const saveCategory = () => {
  if (!categoryForm.value.name) {
    ElMessage.warning('请输入分类名称')
    return
  }
  
  // 模拟添加分类
  const newCategory = {
    id: `cat-${Date.now()}`,
    name: categoryForm.value.name,
    children: []
  }
  
  if (categoryForm.value.parent_id) {
    // 添加到子分类
    const parent = flatCategories.value.find(c => c.id === categoryForm.value.parent_id)
    if (parent) {
      if (!parent.children) parent.children = []
      parent.children.push(newCategory)
    }
  } else {
    // 添加到一级分类
    mockStore.categories.push(newCategory)
  }
  
  ElMessage.success('添加成功')
  showAddCategory.value = false
  categoryForm.value = { name: '', parent_id: '', platform_id: '' }
}

const editCategory = (data: any) => {
  ElMessage.info('编辑功能演示')
}

const deleteCategory = async (data: any) => {
  try {
    await ElMessageBox.confirm(`确定删除分类 "${data.name}" 吗？`, '提示', { type: 'warning' })
    ElMessage.success('删除成功')
  } catch {
    // 取消
  }
}

const saveEntry = () => {
  if (!entryForm.value.question || !entryForm.value.answer) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  const category = flatCategories.value.find(c => c.id === entryForm.value.category_id)
  
  const newEntry = {
    id: `entry-${Date.now()}`,
    question: entryForm.value.question,
    answer: entryForm.value.answer,
    category_name: category?.name || '未分类',
    keywords: entryForm.value.keywords
  }
  
  mockStore.entries.push(newEntry)
  
  ElMessage.success('添加成功')
  showAddEntry.value = false
  entryForm.value = { platform_id: '', category_id: '', question: '', answer: '', keywords: [] }
}

const editEntry = (row: any) => {
  ElMessage.info('编辑功能演示')
}

const deleteEntry = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定删除条目 "${row.question}" 吗？`, '提示', { type: 'warning' })
    const index = mockStore.entries.findIndex(e => e.id === row.id)
    if (index > -1) {
      mockStore.entries.splice(index, 1)
    }
    ElMessage.success('删除成功')
  } catch {
    // 取消
  }
}

// 使用模板条目
const useTemplateItem = (item: any) => {
  entryForm.value.question = item.question
  entryForm.value.answer = item.answer
  showIndustryDetailDialog.value = false
  showAddEntry.value = true
  ElMessage.success('已填充到新增条目表单')
}

// 一键导入全部模板
const importAllTemplates = async () => {
  try {
    await ElMessageBox.confirm('确定要导入该行业的全部知识库模板吗？', '提示', { type: 'info' })
    if (industryDetailData.value && industryDetailData.value.categories) {
      let count = 0
      industryDetailData.value.categories.forEach((category: any) => {
        category.items.forEach((item: any) => {
          mockStore.entries.push({
            id: `entry-${Date.now()}-${count}`,
            question: item.question,
            answer: item.answer,
            category_name: industryDetailData.value.name,
            keywords: [industryDetailData.value.name, category.name]
          })
          count++
        })
      })
      ElMessage.success(`成功导入 ${count} 条知识库条目`)
      showIndustryDetailDialog.value = false
    }
  } catch {
    // 取消
  }
}

// 当前展开的折叠面板
const activeCollapse = ref([0])
</script>

<style scoped>
.knowledge {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 10px;
}

.tree-node .actions {
  display: none;
}

.tree-node:hover .actions {
  display: block;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

/* 平台筛选样式 */
.platform-filter {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.platform-category {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.category-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  white-space: nowrap;
  min-width: 80px;
}

/* 行业知识库样式 */
.industry-section {
  padding: 10px 0;
}

.current-industry {
  display: flex;
  align-items: center;
  gap: 16px;
}

.industry-desc {
  color: #606266;
  font-size: 14px;
}

.no-industry {
  padding: 20px 0;
}

.industry-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.industry-card {
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}

.industry-card:hover {
  transform: translateY(-4px);
  border-color: #409eff;
}

.industry-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.industry-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.industry-desc {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
  line-height: 1.5;
  min-height: 36px;
}

.industry-templates {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

@media screen and (max-width: 1200px) {
  .industry-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media screen and (max-width: 768px) {
  .industry-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 行业模板详情样式 */
.industry-detail {
  max-height: 600px;
  overflow-y: auto;
}

.industry-detail .el-collapse {
  border: none;
}

.industry-detail .el-collapse-item__header {
  font-size: 14px;
  font-weight: 500;
}
</style>
