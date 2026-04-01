<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <el-icon :size="48" color="#1677ff"><Shop /></el-icon>
        <h1>商家登录</h1>
        <p>EAMS 智能客服管理系统</p>
      </div>

      <el-card class="login-card">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          @keyup.enter="handleLogin"
        >
          <el-form-item label="账号" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入商家账号"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              show-password
              size="large"
            />
          </el-form-item>

          <el-form-item>
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <a href="#" class="forgot-link">忘记密码？</a>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              @click="handleLogin"
              size="large"
              style="width: 100%"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">
          <p>还没有账号？<a href="#">立即注册</a></p>
        </div>
      </el-card>
    </div>

    <div class="login-bg">
      <div class="bg-content">
        <h2>智能客服，助力电商增长</h2>
        <ul>
          <li>🤖 AI智能回复，7×24小时在线</li>
          <li>📊 多维度数据分析，洞察客户需求</li>
          <li>🔗 多平台接入，一站式管理</li>
          <li>👥 人机协作，提升服务效率</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Shop } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const rememberMe = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error('登录失败，请检查账号密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  background: #f0f2f5;
}

.login-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 600;
  margin: 16px 0 8px;
  color: #333;
}

.login-header p {
  font-size: 14px;
  color: #666;
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
}

.forgot-link {
  float: right;
  font-size: 13px;
  color: #1677ff;
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e8e8e8;
}

.login-footer p {
  font-size: 14px;
  color: #666;
}

.login-footer a {
  color: #1677ff;
  text-decoration: none;
}

.login-bg {
  flex: 1;
  background: linear-gradient(135deg, #1677ff 0%, #0958d9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #fff;
}

.bg-content {
  max-width: 400px;
}

.bg-content h2 {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 32px;
}

.bg-content ul {
  list-style: none;
  padding: 0;
}

.bg-content li {
  font-size: 16px;
  margin-bottom: 16px;
  opacity: 0.9;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .login-page {
    flex-direction: column;
  }
  
  .login-bg {
    display: none;
  }
  
  .login-container {
    padding: 20px;
  }
  
  .login-header h1 {
    font-size: 24px;
  }
}
</style>
