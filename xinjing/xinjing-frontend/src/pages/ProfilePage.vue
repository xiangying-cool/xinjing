<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import { api } from '../services/api.js'

const router = useRouter()
const { userId, currentUser, updateProfile } = useAuth()

// 页面加载动画
const visible = ref(false)
onMounted(() => {
  setTimeout(() => { visible.value = true }, 100)
  loadProfile()
})

// 用户资料表单
const profile = ref({
  nickname: '',
  email: '',
  phone: '',
  bio: '',
  emergency_contact: '',
  emergency_phone: ''
})

const loading = ref(false)
const saving = ref(false)
const message = ref('')
const messageType = ref('success')

// 加载用户资料
async function loadProfile() {
  loading.value = true
  try {
    const data = await api.get(`/users/${userId.value}/profile`)
    if (data) {
      profile.value = {
        nickname: data.nickname || '',
        email: data.email || '',
        phone: data.phone || '',
        bio: data.bio || '',
        emergency_contact: data.emergency_contact || '',
        emergency_phone: data.emergency_phone || ''
      }
    }
  } catch (e) {
    console.error('加载资料失败:', e)
    showMessage('加载资料失败', 'error')
  } finally {
    loading.value = false
  }
}

// 保存资料
async function saveProfile() {
  saving.value = true
  try {
    await updateProfile(profile.value)
    showMessage('资料保存成功', 'success')
  } catch (e) {
    console.error('保存失败:', e)
    showMessage('保存失败，请重试', 'error')
  } finally {
    saving.value = false
  }
}

// 显示消息
function showMessage(msg, type = 'success') {
  message.value = msg
  messageType.value = type
  setTimeout(() => { message.value = '' }, 3000)
}

// 返回上一页
function goBack() {
  router.back()
}
</script>

<template>
  <div class="min-h-screen bg-hero-gradient">
    <div class="max-w-2xl mx-auto px-6 py-12">
      <!-- 返回按钮 -->
      <button 
        @click="goBack"
        class="mb-6 flex items-center gap-2 text-gray-500 hover:text-primary transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        返回
      </button>

      <!-- 页面标题 -->
      <div 
        class="text-center mb-10 transition-all duration-500"
        :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'"
      >
        <h1 class="text-3xl font-bold text-gray-800 mb-2">个人资料</h1>
        <p class="text-gray-500">管理您的个人信息和紧急联系人</p>
      </div>

      <!-- 消息提示 -->
      <Transition name="fade">
        <div 
          v-if="message" 
          class="mb-6 p-4 rounded-xl text-center"
          :class="messageType === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'"
        >
          {{ message }}
        </div>
      </Transition>

      <!-- 资料表单 -->
      <div 
        class="bg-white rounded-2xl shadow-card border border-gray-100 p-8 transition-all duration-500 delay-100"
        :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'"
      >
        <div v-if="loading" class="text-center py-12">
          <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto"></div>
          <p class="text-gray-400 mt-3">加载中...</p>
        </div>

        <form v-else @submit.prevent="saveProfile" class="space-y-6">
          <!-- 基本信息 -->
          <div class="space-y-4">
            <h3 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <span class="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">👤</span>
              基本信息
            </h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">昵称</label>
                <input 
                  v-model="profile.nickname"
                  type="text"
                  placeholder="设置一个昵称"
                  class="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">邮箱</label>
                <input 
                  v-model="profile.email"
                  type="email"
                  placeholder="your@email.com"
                  class="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">手机号</label>
              <input 
                v-model="profile.phone"
                type="tel"
                placeholder="138xxxx"
                class="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">个人简介</label>
              <textarea 
                v-model="profile.bio"
                rows="3"
                placeholder="简单介绍一下自己..."
                class="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all resize-none"
              ></textarea>
            </div>
          </div>

          <!-- 紧急联系人 -->
          <div class="space-y-4 pt-6 border-t border-gray-100">
            <h3 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <span class="w-8 h-8 rounded-lg bg-red-50 text-red-500 flex items-center justify-center">🆘</span>
              紧急联系人
            </h3>
            <p class="text-sm text-gray-500">在遇到紧急情况时，我们会联系您设置的紧急联系人</p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">联系人姓名</label>
                <input 
                  v-model="profile.emergency_contact"
                  type="text"
                  placeholder="紧急联系人姓名"
                  class="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">联系人电话</label>
                <input 
                  v-model="profile.emergency_phone"
                  type="tel"
                  placeholder="紧急联系人电话"
                  class="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                />
              </div>
            </div>
          </div>

          <!-- 保存按钮 -->
          <div class="pt-6">
            <button 
              type="submit"
              :disabled="saving"
              class="w-full btn-primary py-3 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <svg v-if="saving" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ saving ? '保存中...' : '保存资料' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
