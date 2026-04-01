<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
    <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index">
      {{ item }}
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const breadcrumbs = computed(() => {
  const titles: string[] = []
  const matched = route.matched
  
  for (const record of matched) {
    if (record.meta?.title && record.path !== '/') {
      titles.push(record.meta.title as string)
    }
  }
  
  return titles
})
</script>
