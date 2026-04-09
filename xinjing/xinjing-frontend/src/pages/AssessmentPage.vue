<script setup>
import { useRoute, useRouter } from 'vue-router'
import { onMounted } from 'vue'

const route = useRoute()
const router = useRouter()
const type = route.params.type

// 将评估类型映射到筛查页面的类型
const typeMap = {
  'phq9': 'phq9',
  'sds': 'sds', 
  'ais': 'ais',
  'pss': 'pss',
  'depression': 'phq9',
  'sleep': 'ais',
  'stress': 'pss'
}

onMounted(() => {
  // 自动跳转到筛查页面，并传递评估类型
  const targetType = typeMap[type] || 'phq9'
  router.push({
    path: '/screening',
    query: { type: targetType }
  })
})
</script>

<template>
  <div class="min-h-screen bg-hero-gradient flex items-center justify-center">
    <div class="text-center">
      <div class="text-5xl mb-4">📋</div>
      <h2 class="text-2xl font-bold text-gray-800 mb-2">正在进入 {{ type?.toUpperCase() }} 评估...</h2>
      <p class="text-gray-500 mb-6">正在跳转到辅助筛查页面</p>
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto"></div>
    </div>
  </div>
</template>
