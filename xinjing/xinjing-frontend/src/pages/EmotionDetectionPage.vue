<template>
  <MainLayout>
    <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-8 px-4">
      <div class="max-w-4xl mx-auto">
        <!-- 标题 -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-800 mb-2">面部表情识别</h1>
          <p class="text-gray-600">上传照片或拍照，AI 将分析您的情绪状态</p>
        </div>

        <!-- 主要内容区 -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <!-- 输入方式切换 -->
          <div class="flex justify-center gap-4 mb-6">
            <button
              @click="inputMode = 'upload'"
              :class="['px-6 py-2 rounded-full font-medium transition-all', inputMode === 'upload' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']"
            >
              📤 上传图片
            </button>
            <button
              @click="inputMode = 'camera'"
              :class="['px-6 py-2 rounded-full font-medium transition-all', inputMode === 'camera' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']"
            >
              📷 拍照识别
            </button>
          </div>

          <!-- 上传图片 -->
          <div v-if="inputMode === 'upload'" class="text-center">
            <div
              @click="$refs.fileInput.click()"
              @drop.prevent="handleDrop"
              @dragover.prevent
              class="border-2 border-dashed border-blue-300 rounded-xl p-12 cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all"
            >
              <div class="text-6xl mb-4">📸</div>
              <p class="text-gray-600 mb-2">点击或拖拽图片到此处</p>
              <p class="text-sm text-gray-400">支持 JPG、PNG 格式</p>
            </div>
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              @change="handleFileChange"
              class="hidden"
            />
          </div>

          <!-- 拍照 -->
          <div v-else class="text-center">
            <div v-if="!cameraActive" class="space-y-4">
              <button
                @click="startCamera"
                class="px-8 py-4 bg-blue-500 text-white rounded-xl font-medium hover:bg-blue-600 transition-all"
              >
                🎥 开启摄像头
              </button>
              <p class="text-gray-500 text-sm">需要摄像头权限</p>
            </div>
            <div v-else class="relative">
              <video
                ref="videoRef"
                autoplay
                playsinline
                class="w-full max-w-md mx-auto rounded-xl"
              ></video>
              <div class="flex justify-center gap-4 mt-4">
                <button
                  @click="capturePhoto"
                  class="px-6 py-2 bg-green-500 text-white rounded-full font-medium hover:bg-green-600 transition-all"
                >
                  📷 拍照
                </button>
                <button
                  @click="stopCamera"
                  class="px-6 py-2 bg-red-500 text-white rounded-full font-medium hover:bg-red-600 transition-all"
                >
                  ❌ 关闭
                </button>
              </div>
            </div>
          </div>

          <!-- 预览图片 -->
          <div v-if="previewImage" class="mt-6 text-center">
            <img
              :src="previewImage"
              class="max-w-md mx-auto rounded-xl shadow-lg"
            />
            <button
              @click="analyzeEmotion"
              :disabled="loading"
              class="mt-4 px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full font-medium hover:from-blue-600 hover:to-purple-600 transition-all disabled:opacity-50"
            >
              <span v-if="loading" class="animate-spin inline-block mr-2">⏳</span>
              {{ loading ? '分析中...' : '🔍 开始识别' }}
            </button>
          </div>
        </div>

        <!-- 识别结果 -->
        <div v-if="result" class="bg-white rounded-2xl shadow-xl p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4 text-center">识别结果</h2>
          
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div
              v-for="(item, index) in sortedResults"
              :key="index"
              :class="['p-4 rounded-xl text-center transition-all', index === 0 ? 'bg-blue-100 border-2 border-blue-500 scale-105' : 'bg-gray-50']"
            >
              <div class="text-4xl mb-2">{{ item.emoji }}</div>
              <div class="font-bold text-gray-800">{{ item.name }}</div>
              <div class="text-sm text-gray-600">{{ (item.confidence * 100).toFixed(1) }}%</div>
              <div class="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :style="{ width: item.confidence * 100 + '%', backgroundColor: item.color }"
                ></div>
              </div>
            </div>
          </div>

          <!-- 主要情绪 -->
          <div class="mt-6 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl text-center">
            <div class="text-6xl mb-2">{{ topEmotion.emoji }}</div>
            <div class="text-2xl font-bold text-gray-800">
              检测到情绪：{{ topEmotion.name }}
            </div>
            <div class="text-gray-600 mt-2">
              置信度：{{ (topEmotion.confidence * 100).toFixed(1) }}%
            </div>
          </div>

          <!-- 建议 -->
          <div class="mt-6 p-4 bg-yellow-50 rounded-xl border border-yellow-200">
            <div class="flex items-start gap-3">
              <span class="text-2xl">💡</span>
              <div>
                <div class="font-bold text-gray-800 mb-1">情绪建议</div>
                <p class="text-gray-600 text-sm">{{ emotionAdvice }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="mt-4 p-4 bg-red-50 text-red-600 rounded-xl text-center">
          {{ error }}
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import MainLayout from '../layouts/MainLayout.vue'
import api from '../services/api'

const inputMode = ref('upload')
const previewImage = ref(null)
const selectedFile = ref(null)
const loading = ref(false)
const result = ref(null)
const error = ref(null)
const cameraActive = ref(false)
const videoRef = ref(null)

// 情绪标签映射
const emotionLabels = {
  0: { name: '愤怒', emoji: '😠', color: '#FF4444', advice: '深呼吸，试着放松，愤怒会伤害自己。' },
  1: { name: '厌恶', emoji: '😧', color: '#8B4513', advice: '转移注意力，做一些让自己开心的事情。' },
  2: { name: '恐惧', emoji: '😨', color: '#800080', advice: '恐惧是正常的，试着面对它，你比自己想象的更勇敢。' },
  3: { name: '开心', emoji: '😃', color: '#FFD700', advice: '保持这份好心情，分享给身边的人吧！' },
  4: { name: '悲伤', emoji: '😞', color: '#4169E1', advice: '允许自己悲伤，但也要记得照顾好自己。' },
  5: { name: '惊讶', emoji: '😮', color: '#FF8C00', advice: '生活中的惊喜让每一天都充满期待！' },
  6: { name: '中立', emoji: '😐', color: '#808080', advice: '平静也是一种美好，享受当下的宁静。' }
}

// 排序后的结果
const sortedResults = computed(() => {
  if (!result.value || !result.value.emotions) return []
  return result.value.emotions
    .map((confidence, idx) => ({
      ...emotionLabels[idx],
      confidence
    }))
    .sort((a, b) => b.confidence - a.confidence)
})

// 主要情绪
const topEmotion = computed(() => {
  return sortedResults.value[0] || { name: '', emoji: '', confidence: 0 }
})

// 情绪建议
const emotionAdvice = computed(() => {
  return topEmotion.value.advice || ''
})

// 处理文件上传
function handleFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    processFile(file)
  }
}

// 处理拖拽
function handleDrop(event) {
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  }
}

// 处理文件
function processFile(file) {
  selectedFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    previewImage.value = e.target.result
  }
  reader.readAsDataURL(file)
  result.value = null
  error.value = null
}

// 开启摄像头
async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    videoRef.value.srcObject = stream
    cameraActive.value = true
  } catch (err) {
    error.value = '无法访问摄像头，请检查权限设置'
  }
}

// 关闭摄像头
function stopCamera() {
  if (videoRef.value && videoRef.value.srcObject) {
    videoRef.value.srcObject.getTracks().forEach(track => track.stop())
    videoRef.value.srcObject = null
  }
  cameraActive.value = false
}

// 拍照
function capturePhoto() {
  if (!videoRef.value) return
  
  const canvas = document.createElement('canvas')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight
  canvas.getContext('2d').drawImage(videoRef.value, 0, 0)
  
  canvas.toBlob((blob) => {
    const file = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' })
    processFile(file)
    stopCamera()
  }, 'image/jpeg')
}

// 分析情绪
async function analyzeEmotion() {
  if (!selectedFile.value) return
  
  loading.value = true
  error.value = null
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const response = await api.post('/emotion/detect', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    result.value = response
  } catch (err) {
    error.value = err.response?.data?.detail || '识别失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
