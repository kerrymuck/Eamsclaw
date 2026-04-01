import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('super_admin_token') || '')
  const username = ref(localStorage.getItem('super_admin_username') || '')
  const role = ref(localStorage.getItem('super_admin_role') || '')

  const isLoggedIn = computed(() => !!token.value)

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('super_admin_token', newToken)
  }

  const setUserInfo = (name: string, userRole: string) => {
    username.value = name
    role.value = userRole
    localStorage.setItem('super_admin_username', name)
    localStorage.setItem('super_admin_role', userRole)
  }

  const logout = () => {
    token.value = ''
    username.value = ''
    role.value = ''
    localStorage.removeItem('super_admin_token')
    localStorage.removeItem('super_admin_username')
    localStorage.removeItem('super_admin_role')
  }

  return {
    token,
    username,
    role,
    isLoggedIn,
    setToken,
    setUserInfo,
    logout
  }
})
