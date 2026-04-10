<template>
  <div style="padding: 20px;">
    <h1>表情识别测试页面</h1>
    <p>这是一个简单的测试页面</p>
    <button @click="count++">点击我: {{ count }}</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const count = ref(0)
</script>
