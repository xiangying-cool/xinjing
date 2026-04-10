<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-8 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- 标题 -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">面部表情识别</h1>
        <p class="text-gray-600">上传照片、拍照或开启实时视频，AI 将分析您的情绪状态</p>
      </div>

      <!-- 主要内容区 -->
      <div class="bg-white rounded-2xl shadow-xl p-6 mb-6">
        <!-- 输入方式切换 -->
        <div class="flex justify-center gap-3 mb-6 flex-wrap">
          <button
            @click="switchMode('upload')"
            :class="['px-5 py-2 rounded-full font-medium transition-all text-sm', inputMode === 'upload' ? 'bg-blue-500 text-white shadow-md' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']"
          >📤 上传图片</button>
          <button
            @click="switchMode('camera')"
            :class="['px-5 py-2 rounded-full font-medium transition-all text-sm', inputMode === 'camera' ? 'bg-blue-500 text-white shadow-md' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']"
          >📷 拍照识别</button>
          <button
            @click="switchMode('live')"
            :class="['px-5 py-2 rounded-full font-medium transition-all text-sm', inputMode === 'live' ? 'bg-purple-500 text-white shadow-md' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']"
          >🎥 实时识别</button>
        </div>

        <!-- 上传图片 -->
        <div v-if="inputMode === 'upload'">
          <div
            @click="$refs.fileInput.click()"
            @drop.prevent="handleDrop"
            @dragover.prevent
            class="border-2 border-dashed border-blue-300 rounded-xl p-12 cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all text-center"
          >
            <div class="text-6xl mb-4">📸</div>
            <p class="text-gray-600 mb-2">点击或拖拽图片到此处</p>
            <p class="text-sm text-gray-400">支持 JPG、PNG 格式</p>
          </div>
          <input ref="fileInput" type="file" accept="image/*" @change="handleFileChange" class="hidden" />

          <!-- 预览 -->
          <div v-if="previewImage" class="mt-6 text-center">
            <img :src="previewImage" class="max-w-sm mx-auto rounded-xl shadow-lg" />
            <button
              @click="analyzeEmotion"
              :disabled="loading"
              class="mt-4 px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full font-medium hover:opacity-90 transition-all disabled:opacity-50"
            >
              <span v-if="loading">⏳ 分析中...</span>
              <span v-else>🔍 开始识别</span>
            </button>
          </div>
        </div>

        <!-- 拍照识别 -->
        <div v-else-if="inputMode === 'camera'" class="text-center">
          <div v-if="!cameraActive" class="space-y-4 py-8">
            <button @click="startCamera('photo')" class="px-8 py-4 bg-blue-500 text-white rounded-xl font-medium hover:bg-blue-600 transition-all">
              🎥 开启摄像头
            </button>
            <p class="text-gray-500 text-sm">需要摄像头权限</p>
          </div>
          <div v-else>
            <video ref="videoRef" autoplay playsinline class="w-full max-w-md mx-auto rounded-xl shadow"></video>
            <div class="flex justify-center gap-4 mt-4">
              <button @click="capturePhoto" class="px-6 py-2 bg-green-500 text-white rounded-full font-medium hover:bg-green-600 transition-all">
                📷 拍照
              </button>
              <button @click="stopCamera" class="px-6 py-2 bg-red-500 text-white rounded-full font-medium hover:bg-red-600 transition-all">
                ❌ 关闭
              </button>
            </div>
          </div>
          <!-- 拍照后预览 -->
          <div v-if="previewImage && !cameraActive" class="mt-6 text-center">
            <img :src="previewImage" class="max-w-sm mx-auto rounded-xl shadow-lg" />
            <button
              @click="analyzeEmotion"
              :disabled="loading"
              class="mt-4 px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full font-medium hover:opacity-90 transition-all disabled:opacity-50"
            >
              <span v-if="loading">⏳ 分析中...</span>
              <span v-else>🔍 开始识别</span>
            </button>
          </div>
        </div>

        <!-- 实时视频识别 (WebSocket) -->
        <div v-else-if="inputMode === 'live'">
          <!-- 未开启 -->
          <div v-if="!liveActive" class="text-center space-y-4 py-8">
            <div class="text-5xl mb-2">🎭</div>
            <p class="text-gray-600 mb-4">开启后将实时检测摄像头画面中的面部表情</p>
            <button @click="startLive" class="px-8 py-4 bg-purple-500 text-white rounded-xl font-medium hover:bg-purple-600 transition-all shadow-lg">
              🚀 开启实时识别
            </button>
          </div>

          <!-- 识别中 -->
          <div v-else>
            <!-- 隐藏摄像头，用于捕帧 -->
            <video ref="liveVideoRef" autoplay playsinline muted class="hidden"></video>

            <!-- 主体：视频 + 情绪面板 -->
            <div class="flex flex-col lg:flex-row gap-4 items-start">

              <!-- 左：标注视频流 -->
              <div class="relative flex-1 min-w-0">
                <img v-if="liveFrameSrc" :src="liveFrameSrc" class="w-full rounded-xl shadow-lg" alt="实时识别画面" />
                <div v-else class="w-full h-64 bg-gray-100 rounded-xl flex flex-col items-center justify-center text-gray-400 gap-2">
                  <div class="text-4xl">⏳</div>
                  <div class="text-sm">等待画面...</div>
                </div>
                <!-- 连接状态 -->
                <div class="absolute top-3 left-3 flex items-center gap-1.5 bg-black/60 text-white text-xs px-3 py-1.5 rounded-full backdrop-blur-sm">
                  <span class="w-2 h-2 rounded-full animate-pulse" :class="wsConnected ? 'bg-green-400' : 'bg-yellow-400'"></span>
                  {{ wsConnected ? '实时识别中' : '连接中...' }}
                </div>
                <!-- 人脸状态徽标 -->
                <div v-if="liveEmotions" class="absolute top-3 right-3 text-xs px-3 py-1.5 rounded-full backdrop-blur-sm font-medium"
                     :class="liveEmotions.face_detected ? 'bg-green-500/80 text-white' : 'bg-black/50 text-gray-200'">
                  {{ liveEmotions.face_detected ? '已检测到人脸' : '未检测到人脸' }}
                </div>
              </div>

              <!-- 右：情绪分析面板 -->
              <div class="w-full lg:w-60 flex-shrink-0 space-y-3">
                <!-- 等待人脸 -->
                <div v-if="!liveEmotions || !liveEmotions.face_detected"
                     class="h-48 bg-gray-50 rounded-xl flex flex-col items-center justify-center text-gray-400 border-2 border-dashed border-gray-200">
                  <div class="text-4xl mb-2">😶</div>
                  <div class="text-sm">等待检测人脸...</div>
                </div>

                <template v-else>
                  <!-- 主情绪 -->
                  <div class="p-4 bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl text-center border border-purple-100">
                    <div class="text-5xl mb-1 leading-none">{{ liveTopEmotion.emoji }}</div>
                    <div class="text-base font-bold text-gray-800 mt-1">{{ liveTopEmotion.name }}</div>
                    <div class="text-sm text-gray-500">{{ (liveTopEmotion.confidence * 100).toFixed(1) }}%</div>
                  </div>

                  <!-- 情绪条形图 -->
                  <div class="bg-white rounded-xl p-3 space-y-2 shadow-sm border border-gray-100">
                    <div v-for="(item, index) in liveSortedEmotions" :key="index">
                      <div class="flex justify-between items-center text-xs mb-0.5">
                        <span :style="{ color: index === 0 ? item.color : '#9CA3AF' }" class="font-medium">
                          {{ item.emoji }} {{ item.name }}
                        </span>
                        <span class="text-gray-400">{{ (item.confidence * 100).toFixed(1) }}%</span>
                      </div>
                      <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div class="h-full rounded-full transition-all duration-200"
                             :style="{ width: item.confidence * 100 + '%', backgroundColor: item.color, opacity: index === 0 ? 1 : 0.45 }"></div>
                      </div>
                    </div>
                  </div>

                  <!-- 情绪建议 -->
                  <div class="p-3 bg-amber-50 rounded-xl border border-amber-100">
                    <div class="flex items-start gap-2">
                      <span class="text-lg flex-shrink-0">💡</span>
                      <p class="text-gray-600 text-sm leading-relaxed">{{ liveTopEmotion.advice }}</p>
                    </div>
                  </div>
                </template>
              </div>
            </div>

            <!-- 停止按钮 -->
            <div class="text-center mt-4">
              <button @click="stopLive" class="px-6 py-2 bg-red-500 text-white rounded-full font-medium hover:bg-red-600 transition-all shadow">
                ⏹️ 停止识别
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 识别结果（上传/拍照模式） -->
      <div v-if="result && inputMode !== 'live'" class="bg-white rounded-2xl shadow-xl p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-4 text-center">识别结果</h2>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div
            v-for="(item, index) in sortedResults"
            :key="index"
            :class="['p-4 rounded-xl text-center transition-all', index === 0 ? 'bg-blue-100 border-2 border-blue-500 scale-105' : 'bg-gray-50']"
          >
            <div class="text-4xl mb-1">{{ item.emoji }}</div>
            <div class="font-bold text-gray-800 text-sm">{{ item.name }}</div>
            <div class="text-xs text-gray-500">{{ (item.confidence * 100).toFixed(1) }}%</div>
            <div class="mt-2 h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-500" :style="{ width: item.confidence * 100 + '%', backgroundColor: item.color }"></div>
            </div>
          </div>
        </div>

        <!-- 主要情绪 -->
        <div class="p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl text-center">
          <div class="text-6xl mb-2">{{ topEmotion.emoji }}</div>
          <div class="text-2xl font-bold text-gray-800">检测到情绪：{{ topEmotion.name }}</div>
          <div class="text-gray-600 mt-1">置信度：{{ (topEmotion.confidence * 100).toFixed(1) }}%</div>
        </div>

        <!-- 建议 -->
        <div class="mt-4 p-4 bg-yellow-50 rounded-xl border border-yellow-200 flex items-start gap-3">
          <span class="text-2xl">💡</span>
          <div>
            <div class="font-bold text-gray-800 mb-1">情绪建议</div>
            <p class="text-gray-600 text-sm">{{ topEmotion.advice }}</p>
          </div>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="mt-4 p-4 bg-red-50 text-red-600 rounded-xl text-center">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, nextTick } from 'vue'

const inputMode = ref('upload')
const previewImage = ref(null)
const selectedFile = ref(null)
const loading = ref(false)
const result = ref(null)
const error = ref(null)
const cameraActive = ref(false)
const videoRef = ref(null)

// 实时识别
const liveActive = ref(false)
const liveVideoRef = ref(null)
const liveFrameSrc = ref(null)
const wsConnected = ref(false)
const liveEmotions = ref(null)   // { face_detected, emotions[] }
let ws = null
let frameTimer = null

const emotionLabels = {
  0: { name: '愤怒', emoji: '😠', color: '#FF4444', advice: '深呼吸，试着放松，愤怒会伤害自己。' },
  1: { name: '厌恶', emoji: '😧', color: '#8B4513', advice: '转移注意力，做一些让自己开心的事情。' },
  2: { name: '恐惧', emoji: '😨', color: '#800080', advice: '恐惧是正常的，试着面对它，你比自己想象的更勇敢。' },
  3: { name: '开心', emoji: '😃', color: '#FFD700', advice: '保持这份好心情，分享给身边的人吧！' },
  4: { name: '悲伤', emoji: '😞', color: '#4169E1', advice: '允许自己悲伤，但也要记得照顾好自己。' },
  5: { name: '惊讶', emoji: '😮', color: '#FF8C00', advice: '生活中的惊喜让每一天都充满期待！' },
  6: { name: '中立', emoji: '😐', color: '#808080', advice: '平静也是一种美好，享受当下的宁静。' }
}

const sortedResults = computed(() => {
  if (!result.value?.emotions) return []
  return result.value.emotions
    .map((confidence, idx) => ({ ...emotionLabels[idx], confidence }))
    .sort((a, b) => b.confidence - a.confidence)
})

const topEmotion = computed(() => sortedResults.value[0] || { name: '', emoji: '', confidence: 0, advice: '' })

const liveSortedEmotions = computed(() => {
  if (!liveEmotions.value?.emotions) return []
  return liveEmotions.value.emotions
    .map((confidence, idx) => ({ ...emotionLabels[idx], confidence }))
    .sort((a, b) => b.confidence - a.confidence)
})

const liveTopEmotion = computed(() => liveSortedEmotions.value[0] || { name: '', emoji: '', confidence: 0, advice: '' })

// 切换模式时清理
function switchMode(mode) {
  stopCamera()
  stopLive()
  previewImage.value = null
  selectedFile.value = null
  result.value = null
  error.value = null
  inputMode.value = mode
}

function handleFileChange(event) {
  const file = event.target.files[0]
  if (file) processFile(file)
}

function handleDrop(event) {
  const file = event.dataTransfer.files[0]
  if (file?.type.startsWith('image/')) processFile(file)
}

function processFile(file) {
  selectedFile.value = file
  result.value = null
  error.value = null
  const reader = new FileReader()
  reader.onload = (e) => { previewImage.value = e.target.result }
  reader.readAsDataURL(file)
}

// 开启摄像头（拍照模式）
async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    cameraActive.value = true
    await nextTick()
    videoRef.value.srcObject = stream
    previewImage.value = null
    result.value = null
  } catch {
    error.value = '无法访问摄像头，请检查权限设置'
  }
}

function stopCamera() {
  if (videoRef.value?.srcObject) {
    videoRef.value.srcObject.getTracks().forEach(t => t.stop())
    videoRef.value.srcObject = null
  }
  cameraActive.value = false
}

function capturePhoto() {
  if (!videoRef.value) return
  const canvas = document.createElement('canvas')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight
  canvas.getContext('2d').drawImage(videoRef.value, 0, 0)
  canvas.toBlob((blob) => {
    const file = new File([blob], 'photo.jpg', { type: 'image/jpeg' })
    processFile(file)
    stopCamera()
  }, 'image/jpeg', 0.9)
}

// 分析情绪（上传/拍照）
async function analyzeEmotion() {
  if (!selectedFile.value) return
  loading.value = true
  error.value = null
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    const response = await fetch('/api/v1/emotion/detect', { method: 'POST', body: formData })
    if (!response.ok) throw new Error(await response.text())
    result.value = await response.json()
  } catch (err) {
    error.value = '识别失败：' + (err.message || '请重试')
  } finally {
    loading.value = false
  }
}

// 开启实时识别（WebSocket）
async function startLive() {
  error.value = null
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
    liveActive.value = true
    await nextTick()
    liveVideoRef.value.srcObject = stream

    // 连接 WebSocket
    ws = new WebSocket(`ws://${location.host}/fer/predict/ws`)
    ws.binaryType = 'arraybuffer'

    ws.onopen = () => {
      wsConnected.value = true
      startSendingFrames()
    }

    ws.onmessage = (event) => {
      if (typeof event.data === 'string') {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'emotions') liveEmotions.value = data
        } catch {}
      } else {
        const blob = new Blob([event.data], { type: 'image/jpeg' })
        const url = URL.createObjectURL(blob)
        if (liveFrameSrc.value) URL.revokeObjectURL(liveFrameSrc.value)
        liveFrameSrc.value = url
      }
    }

    ws.onclose = () => {
      wsConnected.value = false
    }

    ws.onerror = () => {
      error.value = 'WebSocket 连接失败，请确认 FER 服务已启动（端口 8002）'
      stopLive()
    }
  } catch {
    error.value = '无法访问摄像头，请检查权限设置'
  }
}

function startSendingFrames() {
  const canvas = document.createElement('canvas')
  canvas.width = 640
  canvas.height = 480
  const ctx = canvas.getContext('2d')

  // 每 100ms 发送一帧（约 10fps）
  frameTimer = setInterval(() => {
    if (!liveVideoRef.value || !ws || ws.readyState !== WebSocket.OPEN) return
    ctx.drawImage(liveVideoRef.value, 0, 0, 640, 480)
    canvas.toBlob((blob) => {
      if (blob && ws?.readyState === WebSocket.OPEN) {
        blob.arrayBuffer().then(buf => ws.send(buf))
      }
    }, 'image/jpeg', 0.7)
  }, 100)
}

function stopLive() {
  clearInterval(frameTimer)
  frameTimer = null
  if (ws) {
    ws.close()
    ws = null
  }
  if (liveVideoRef.value?.srcObject) {
    liveVideoRef.value.srcObject.getTracks().forEach(t => t.stop())
    liveVideoRef.value.srcObject = null
  }
  liveActive.value = false
  wsConnected.value = false
  liveFrameSrc.value = null
  liveEmotions.value = null
}

onUnmounted(() => {
  stopCamera()
  stopLive()
})
</script>
