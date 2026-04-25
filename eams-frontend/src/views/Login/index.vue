<template>
  <div class="login-container">
    <div class="login-wrapper">
      <!-- 左侧品牌区域 -->
      <div class="brand-section">
        <div class="brand-content">
          <div class="logo">
            <span class="logo-icon">🐱</span>
            <h1>EAMSCLAW</h1>
          </div>
          <p class="slogan">企业级AI电商客服中控台</p>
          <p class="description">一站式多平台智能客服解决方案<br>AI驱动，让客服工作更高效、更智能</p>
          <div class="features">
            <div class="feature-item">
              <el-icon><MessageBox /></el-icon>
              <span>多平台统一管理</span>
            </div>
            <div class="feature-item">
              <el-icon><Cpu /></el-icon>
              <span>AI智能回复</span>
            </div>
            <div class="feature-item">
              <el-icon><DataLine /></el-icon>
              <span>数据智能分析</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录区域 -->
      <div class="login-section">
        <div class="login-box">
          <h2 class="welcome-title">欢迎登录</h2>
          <p class="welcome-subtitle">请选择您的身份类型</p>

          <!-- 登录类型切换 -->
          <div class="login-type-tabs">
            <div 
              class="type-tab" 
              :class="{ active: loginType === 'merchant' }"
              @click="loginType = 'merchant'"
            >
              <div class="tab-icon">
                <el-icon><Shop /></el-icon>
              </div>
              <div class="tab-content">
                <h3>商家登录</h3>
                <p>店铺管理、客服工作台</p>
              </div>
            </div>
            <div 
              class="type-tab" 
              :class="{ active: loginType === 'provider' }"
              @click="loginType = 'provider'"
            >
              <div class="tab-icon provider">
                <el-icon><OfficeBuilding /></el-icon>
              </div>
              <div class="tab-content">
                <h3>服务商登录</h3>
                <p>代理商管理、商户管理</p>
              </div>
            </div>
          </div>

          <!-- 登录表单 -->
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            class="login-form"
            @keyup.enter="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                :prefix-icon="User"
                size="large"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                show-password
                size="large"
              />
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住密码</el-checkbox>
              <el-link type="primary" :underline="false">忘记密码?</el-link>
            </div>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                @click="handleLogin"
                size="large"
                class="login-btn"
              >
                {{ loginType === 'merchant' ? '商家登录' : '服务商登录' }}
              </el-button>
            </el-form-item>
          </el-form>

          <div class="register-link">
            <span>还没有账号?</span>
            <el-link type="primary" :underline="false">立即注册</el-link>
          </div>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="login-footer">
      <p>© 2026 EAMSCLAW 企业级AI电商客服中控台. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Shop, OfficeBuilding, MessageBox, Cpu, DataLine } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const loginType = ref<'merchant' | 'provider'>('merchant')
const rememberMe = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    
    // 根据登录类型跳转到不同的后台
    if (loginType.value === 'provider') {
      // 服务商登录跳转到服务商工作台
      router.push('/provider-dashboard')
    } else {
      // 商家登录跳转到商家管理后台
      router.push('/')
    }
  } catch (error) {
    ElMessage.error('登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

.login-wrapper {
  flex: 1;
  display: flex;
  min-height: 0;
}

/* 左侧品牌区域 */
.brand-section {
  flex: 1;
  background: linear-gradient(135deg, #1677ff 0%, #0056b3 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #fff;
}

.brand-content {
  max-width: 480px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.logo-icon {
  font-size: 48px;
}

.logo h1 {
  font-size: 48px;
  font-weight: 700;
  margin: 0;
}

.slogan {
  font-size: 28px;
  font-weight: 500;
  margin: 0 0 16px 0;
}

.description {
  font-size: 16px;
  line-height: 1.8;
  margin: 0 0 48px 0;
  opacity: 0.9;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
}

.feature-item .el-icon {
  font-size: 24px;
}

/* 右侧登录区域 */
.login-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #fff;
}

.login-box {
  width: 100%;
  max-width: 420px;
}

.welcome-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
  text-align: center;
}

.welcome-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0 0 32px 0;
  text-align: center;
}

/* 登录类型切换 */
.login-type-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
}

.type-tab {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.type-tab:hover {
  border-color: #1677ff;
}

.type-tab.active {
  border-color: #1677ff;
  background: #f0f7ff;
}

.tab-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: #e6f7ff;
  color: #1677ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.tab-icon.provider {
  background: #f6ffed;
  color: #52c41a;
}

.tab-content h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 4px 0;
}

.tab-content p {
  font-size: 12px;
  color: #999;
  margin: 0;
}

/* 登录表单 */
.login-form {
  margin-bottom: 24px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  font-size: 16px;
}

.register-link {
  text-align: center;
  font-size: 14px;
  color: #666;
}

.register-link span {
  margin-right: 8px;
}

/* 页脚 */
.login-footer {
  padding: 24px;
  text-align: center;
  background: #fff;
  border-top: 1px solid #e4e7ed;
}

.login-footer p {
  margin: 0;
  font-size: 12px;
  color: #999;
}

/* 响应式适配 */
@media screen and (max-width: 992px) {
  .brand-section {
    display: none;
  }
  
  .login-section {
    padding: 24px;
  }
}

@media screen and (max-width: 576px) {
  .login-type-tabs {
    flex-direction: column;
  }
  
  .type-tab {
    padding: 12px;
  }
  
  .tab-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
}
</style>
