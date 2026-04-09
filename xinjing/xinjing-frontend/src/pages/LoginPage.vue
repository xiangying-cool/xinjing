<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import XjLogo from '../components/XjLogo.vue'

const router = useRouter()
const route  = useRoute()
const { login, register } = useAuth()

const tab      = ref('login')   // 'login' | 'register'
const username = ref('')
const password = ref('')
const confirm  = ref('')
const nickname = ref('')
const email    = ref('')
const phone    = ref('')
const gender   = ref('')
const ageRange = ref('')
const error    = ref('')
const loading  = ref(false)
const showPwd  = ref(false)

const redirect = route.query.redirect || '/'

const AGE_RANGES  = ['< 18', '18-24', '25-34', '35-44', '45-54', '≥ 55']
const GENDER_OPTS = [{ value: 'male', label: '男' }, { value: 'female', label: '女' }, { value: 'other', label: '其他' }]

async function submit() {
  error.value   = ''
  loading.value = true

  if (!username.value.trim()) { error.value = '请输入用户名'; loading.value = false; return }
  if (!password.value)        { error.value = '请输入密码';   loading.value = false; return }
  if (tab.value === 'register' && password.value !== confirm.value) {
    error.value = '两次密码不一致'; loading.value = false; return
  }

  const result = tab.value === 'login'
    ? await login(username.value.trim(), password.value)
    : await register({
        username: username.value.trim(),
        password: password.value,
        nickname: nickname.value.trim(),
        email:    email.value.trim(),
        phone:    phone.value.trim(),
        gender:   gender.value,
        age_range: ageRange.value,
      })

  loading.value = false
  if (result.ok) {
    router.replace(redirect)
  } else {
    error.value = result.message
  }
}

function switchTab(t) {
  tab.value   = t
  error.value = ''
  password.value = ''
  confirm.value  = ''
}
</script>

<template>
  <div class="min-h-screen flex" style="background: linear-gradient(135deg,#EBF5FF 0%,#F0F8FF 40%,#F5F0FF 100%)">

    <!-- ─── 左侧装饰区 ───────────────────────────── -->
    <div class="hidden lg:flex flex-1 relative overflow-hidden items-center justify-center"
         style="background: linear-gradient(145deg,#3B9EE8 0%,#2EC4B6 60%,#6C63FF 100%)">

      <!-- 几何装饰 -->
      <div class="absolute top-[-80px] left-[-80px] w-[360px] h-[360px] rounded-full bg-white/10"></div>
      <div class="absolute bottom-[-60px] right-[-60px] w-[280px] h-[280px] rounded-full bg-white/8"></div>
      <div class="absolute top-1/3 right-12 w-[120px] h-[120px] rounded-full border-2 border-white/20"></div>
      <div class="absolute bottom-1/3 left-16 w-[80px] h-[80px] rounded-full border border-white/15"></div>

      <!-- 中心内容 -->
      <div class="relative z-10 text-center px-12">
        <div class="flex justify-center mb-8">
          <div class="w-24 h-24 rounded-3xl bg-white/20 backdrop-blur-sm flex items-center justify-center shadow-2xl">
            <XjLogo :size="56" />
          </div>
        </div>
        <h1 class="text-4xl font-black text-white mb-4 leading-tight">心镜</h1>
        <p class="text-white/80 text-lg mb-10 leading-relaxed">
          智能心理健康管理平台<br/>多模态评估 · 情绪陪伴 · 数据分析
        </p>

        <!-- 特性列表 -->
        <div class="space-y-4 text-left max-w-xs mx-auto">
          <div v-for="feat in [
            { icon:'🧠', text:'多维度心理健康评估' },
            { icon:'📅', text:'情绪日历与趋势追踪' },
            { icon:'🤖', text:'AI 数字人情绪陪伴' },
            { icon:'📊', text:'可视化报告与分析' },
          ]" :key="feat.text"
            class="flex items-center gap-3 bg-white/10 backdrop-blur-sm rounded-2xl px-5 py-3.5">
            <span class="text-xl">{{ feat.icon }}</span>
            <span class="text-white/90 text-sm font-medium">{{ feat.text }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── 右侧表单区 ─────────────────────────── -->
    <div class="flex-1 lg:max-w-[480px] flex flex-col items-center justify-center px-8 py-12">

      <!-- 移动端 Logo -->
      <div class="lg:hidden flex items-center gap-2.5 mb-10">
        <XjLogo :size="36" />
        <span class="text-2xl font-black"
          style="background:linear-gradient(90deg,#3B9EE8,#2EC4B6);-webkit-background-clip:text;-webkit-text-fill-color:transparent">
          心镜
        </span>
      </div>

      <div class="w-full max-w-[380px]">
        <!-- 标题 -->
        <div class="mb-8">
          <h2 class="text-2xl font-black text-gray-800">{{ tab === 'login' ? '欢迎回来' : '创建账号' }}</h2>
          <p class="text-gray-400 text-sm mt-1">{{ tab === 'login' ? '登录以继续使用心镜' : '注册后开始心理健康之旅' }}</p>
        </div>

        <!-- Tab 切换 -->
        <div class="flex bg-gray-100 rounded-2xl p-1 mb-7">
          <button v-for="t in [['login','登录'],['register','注册']]" :key="t[0]"
            class="flex-1 py-2.5 text-sm font-semibold rounded-xl transition-all duration-200"
            :class="tab === t[0] ? 'bg-white text-primary shadow-sm' : 'text-gray-400 hover:text-gray-600'"
            @click="switchTab(t[0])">
            {{ t[1] }}
          </button>
        </div>

        <!-- 表单 -->
        <form @submit.prevent="submit" class="space-y-4">

          <!-- 注册专属字段 -->
          <Transition name="fade-slide">
            <div v-if="tab === 'register'" class="space-y-4">

              <!-- 昵称 -->
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1.5">昵称</label>
                <input v-model="nickname" type="text" placeholder="你的昵称（选填）"
                  class="w-full px-4 py-3 rounded-2xl border border-gray-200 bg-white text-gray-800 text-sm
                         outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition-all"/>
              </div>

              <!-- 邮箱 -->
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1.5">邮箱</label>
                <input v-model="email" type="email" placeholder="your@email.com（选填）"
                  class="w-full px-4 py-3 rounded-2xl border border-gray-200 bg-white text-gray-800 text-sm
                         outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition-all"/>
              </div>

              <!-- 手机号 -->
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1.5">手机号</label>
                <input v-model="phone" type="tel" placeholder="138xxxx（选填）"
                  class="w-full px-4 py-3 rounded-2xl border border-gray-200 bg-white text-gray-800 text-sm
                         outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition-all"/>
              </div>

              <!-- 性别 + 年龄段 -->
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1.5">性别</label>
                  <select v-model="gender"
                    class="w-full px-4 py-3 rounded-2xl border border-gray-200 bg-white text-gray-700 text-sm
                           outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition-all appearance-none">
                    <option value="">不填写</option>
                    <option v-for="g in GENDER_OPTS" :key="g.value" :value="g.value">{{ g.label }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1.5">年龄段</label>
                  <select v-model="ageRange"
                    class="w-full px-4 py-3 rounded-2xl border border-gray-200 bg-white text-gray-700 text-sm
                           outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition-all appearance-none">
                    <option value="">不填写</option>
                    <option v-for="a in AGE_RANGES" :key="a" :value="a">{{ a }}</option>
                  </select>
                </div>
              </div>

            </div>
          </Transition>

          <!-- 用户名 -->
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1.5">用户名</label>
            <input v-model="username" type="text" placeholder="输入用户名" autocomplete="username"
              class="w-full px-4 py-3 rounded-2xl border border-gray-200 bg-white text-gray-800 text-sm
                     outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition-all"
            />
          </div>

          <!-- 密码 -->
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1.5">密码</label>
            <div class="relative">
              <input v-model="password" :type="showPwd ? 'text' : 'password'" placeholder="输入密码"
                autocomplete="current-password"
                class="w-full px-4 py-3 pr-12 rounded-2xl border border-gray-200 bg-white text-gray-800 text-sm
                       outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition-all"
              />
              <button type="button" @click="showPwd = !showPwd"
                class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors">
                <svg v-if="!showPwd" class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- 确认密码（仅注册） -->
          <Transition name="fade-slide">
            <div v-if="tab === 'register'">
              <label class="block text-sm font-medium text-gray-600 mb-1.5">确认密码</label>
              <input v-model="confirm" type="password" placeholder="再次输入密码"
                class="w-full px-4 py-3 rounded-2xl border border-gray-200 bg-white text-gray-800 text-sm
                       outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition-all"
              />
            </div>
          </Transition>

          <!-- 错误提示 -->
          <Transition name="fade-slide">
            <div v-if="error"
              class="flex items-center gap-2 bg-red-50 border border-red-100 text-red-600 text-sm px-4 py-3 rounded-2xl">
              <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
              </svg>
              {{ error }}
            </div>
          </Transition>

          <!-- 提交按钮 -->
          <button type="submit" :disabled="loading"
            class="w-full py-3.5 rounded-2xl text-white font-semibold text-sm transition-all duration-200 mt-2
                   disabled:opacity-60 disabled:cursor-not-allowed"
            style="background: linear-gradient(135deg,#3B9EE8,#2EC4B6)">
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ tab === 'login' ? '登录中…' : '注册中…' }}
            </span>
            <span v-else>{{ tab === 'login' ? '登录' : '注册' }}</span>
          </button>
        </form>

        <!-- 演示账号提示 -->
        <div v-if="tab === 'login'"
          class="mt-5 p-4 bg-primary/5 rounded-2xl border border-primary/10 text-center">
          <p class="text-xs text-gray-500">演示账号：<span class="text-primary font-mono font-semibold">demo / 123456</span></p>
        </div>

        <!-- 回首页 -->
        <p class="text-center text-sm text-gray-400 mt-6">
          <RouterLink to="/" class="text-primary hover:underline no-underline font-medium">← 返回首页</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.no-underline { text-decoration: none; }
.w-4\.5 { width: 1.125rem; }
.h-4\.5 { height: 1.125rem; }
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.25s ease; }
.fade-slide-enter-from, .fade-slide-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
