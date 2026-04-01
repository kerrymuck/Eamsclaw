import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const role = ref(localStorage.getItem('role') || '')
  const userInfo = ref<any>(null)

  // 模拟登录（用于前端预览，无需后端）
  const login = async (user: string, pass: string) => {
    // 模拟验证 - 任何用户名密码都可以登录
    const mockToken = 'mock_token_' + Date.now()
    const mockUser = {
      id: '1',
      username: user,
      email: user + '@example.com',
      role: 'admin',
      real_name: '管理员'
    }
    
    token.value = mockToken
    username.value = user
    role.value = 'admin'
    userInfo.value = mockUser
    
    localStorage.setItem('token', mockToken)
    localStorage.setItem('username', user)
    localStorage.setItem('role', 'admin')
    
    ElMessage.success('登录成功')
    return { code: 1, data: { token: mockToken, user: mockUser } }
  }

  // 真实API登录（需要后端服务）
  const loginReal = async (user: string, pass: string) => {
    try {
      const res: any = await authApi.login(user, pass)
      if (res.code === 1 || res.access_token) {
        const tokenValue = res.access_token || res.data?.token
        const userData = res.data?.user || res.user
        
        token.value = tokenValue
        username.value = userData.username
        role.value = userData.role
        userInfo.value = userData
        
        localStorage.setItem('token', tokenValue)
        localStorage.setItem('username', userData.username)
        localStorage.setItem('role', userData.role)
        
        ElMessage.success('登录成功')
        return res
      } else {
        throw new Error(res.message || '登录失败')
      }
    } catch (error: any) {
      ElMessage.error(error.message || '登录失败')
      throw error
    }
  }

  const getUserInfo = async () => {
    // 模拟获取用户信息
    if (!userInfo.value && username.value) {
      userInfo.value = {
        id: '1',
        username: username.value,
        role: role.value
      }
    }
  }

  const logout = () => {
    token.value = ''
    username.value = ''
    role.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('role')
    ElMessage.success('已退出登录')
  }

  return {
    token,
    username,
    role,
    userInfo,
    login,
    loginReal,
    logout,
    getUserInfo
  }
})
