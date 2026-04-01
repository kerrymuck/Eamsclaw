<template>
  <div class="knowledge">
    <!-- 平台筛选 -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>📚 知识库管理</span>
          <span style="color: #909399; font-size: 14px">按平台配置不同的知识库内容</span>
        </div>
      </template>
      <div class="platform-filter">
        <span class="filter-label">选择平台：</span>
        <el-radio-group v-model="selectedPlatform" size="small">
          <el-radio-button label="all">全部平台</el-radio-button>
          <el-radio-button v-for="platform in platforms" :key="platform.id" :label="platform.id">
            {{ platform.icon }} {{ platform.name }}
          </el-radio-button>
        </el-radio-group>
      </div>
    </el-card>
    
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
import { ref, computed } from 'vue'
import { Search, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMockStore } from '@/stores/mock'
import { getAllPlatforms } from '@/config/platforms'

const mockStore = useMockStore()
const platforms = getAllPlatforms().slice(0, 8) // 取前8个平台展示
const selectedPlatform = ref('all')

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
</style>
