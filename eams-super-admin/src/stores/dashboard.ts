import { defineStore } from 'pinia'
import { ref } from 'vue'

// 数据面板统计
export const useDashboardStore = defineStore('dashboard', () => {
  const stats = ref({
    totalLicenses: 0,
    activeLicenses: 0,
    todayNewLicenses: 0,
    expiredLicenses: 0,
    totalProviders: 0,
    activeProviders: 0,
    totalRevenue: 0,
    todayRevenue: 0,
    aiTokensUsed: 0,
    aiTokensRemaining: 0
  })

  const licenseTrend = ref([])
  const revenueTrend = ref([])
  const platformDistribution = ref([])

  return {
    stats,
    licenseTrend,
    revenueTrend,
    platformDistribution
  }
})
