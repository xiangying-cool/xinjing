<!-- 背景装饰气泡 - 可复用 -->
<script setup>
defineProps({
  variant: { type: String, default: 'default' } // default | warm | cool
})
</script>

<template>
  <div class="absolute inset-0 overflow-hidden pointer-events-none -z-0" aria-hidden="true">
    <!-- Blob 1 -->
    <div
      class="absolute rounded-full blur-3xl opacity-30 animate-float"
      :class="variant === 'warm'
        ? 'w-96 h-96 -top-20 -left-20 bg-orange-200'
        : 'w-96 h-96 -top-20 -left-20 bg-primary/20'"
    ></div>
    <!-- Blob 2 -->
    <div
      class="absolute rounded-full blur-3xl opacity-20 animate-float"
      style="animation-delay:1.5s"
      :class="variant === 'warm'
        ? 'w-80 h-80 top-1/3 right-0 bg-yellow-200'
        : 'w-80 h-80 top-1/3 right-0 bg-teal-brand/20'"
    ></div>
    <!-- Blob 3 -->
    <div
      class="absolute rounded-full blur-2xl opacity-20 animate-float"
      style="animation-delay:3s"
      :class="'w-64 h-64 bottom-0 left-1/3 bg-primary/10'"
    ></div>
    <!-- Dot grid pattern -->
    <svg class="absolute inset-0 w-full h-full opacity-[0.03]" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="dots" x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse">
          <circle cx="2" cy="2" r="1.5" fill="#3B9EE8"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#dots)"/>
    </svg>
  </div>
</template>
