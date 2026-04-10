<script setup>
import { ref, onMounted, onUnmounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import XjLogo from '../components/XjLogo.vue'
import { useAuth } from '../composables/useAuth.js'

const route  = useRoute()
const router = useRouter()
const { isLoggedIn, currentUser, logout } = useAuth()

const scrolled   = ref(false)
const menuOpen   = ref(false)
const sosOpen    = ref(false)
const userMenuOpen = ref(false)

function handleLogout() {
  userMenuOpen.value = false
  logout()
  router.push('/')
}

// 点击外部关闭用户菜单
function onOutsideClick(e) {
  if (!e.target.closest('#user-menu-anchor')) userMenuOpen.value = false
}
onMounted(() => document.addEventListener('click', onOutsideClick))
onBeforeUnmount(() => document.removeEventListener('click', onOutsideClick))

const navItems = [
  { label: '首页', to: '/' },
  { label: '辅助筛查', to: '/screening' },
  { label: '情绪陪伴', to: '/companion' },
  { label: '表情识别', to: '/emotion' },
  { label: '情绪日历', to: '/mood-calendar' },
  { label: '数据分析', to: '/analytics' },
  { label: '关于我们', to: '/about' },
]

const handleScroll = () => { scrolled.value = window.scrollY > 20 }
onMounted(() => window.addEventListener('scroll', handleScroll))
onUnmounted(() => window.removeEventListener('scroll', handleScroll))
</script>

<template>
  <!-- ===== Navbar ===== -->
  <header
    class="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
    :class="scrolled
      ? 'bg-white/95 backdrop-blur-md shadow-[0_2px_20px_rgba(59,158,232,0.08)]'
      : 'bg-white/70 backdrop-blur-sm'"
  >
    <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
      <!-- Logo -->
      <RouterLink to="/" class="flex items-center gap-2.5 no-underline group">
        <XjLogo :size="36" />
        <span class="text-xl font-black tracking-tight bg-blue-green bg-clip-text text-transparent">心镜</span>
      </RouterLink>

      <!-- Desktop Nav -->
      <nav class="hidden md:flex items-center gap-1">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="relative px-4 py-2 text-sm font-medium rounded-xl transition-all duration-200 no-underline"
          :class="route.path === item.to
            ? 'text-primary bg-primary/8'
            : 'text-gray-500 hover:text-primary hover:bg-primary/5'"
        >
          {{ item.label }}
          <span
            v-if="route.path === item.to"
            class="absolute bottom-1 left-1/2 -translate-x-1/2 w-4 h-0.5 bg-primary rounded-full"
          ></span>
        </RouterLink>
      </nav>

      <!-- CTA + 用户区 -->
      <div class="hidden md:flex items-center gap-2">
        <RouterLink to="/screening" class="btn-primary text-sm no-underline flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
          开始筛测
        </RouterLink>

        <!-- 未登录：登录按钮 -->
        <RouterLink v-if="!isLoggedIn" to="/login"
          class="px-4 py-2 text-sm font-medium text-primary border border-primary/30 rounded-xl
                 hover:bg-primary/5 transition-all no-underline">
          登录
        </RouterLink>

        <!-- 已登录：用户头像下拉 -->
        <div v-else id="user-menu-anchor" class="relative">
          <button @click.stop="userMenuOpen = !userMenuOpen"
            class="flex items-center gap-2 px-3 py-1.5 rounded-xl hover:bg-gray-100 transition-all">
            <!-- 头像圆 -->
            <div class="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                 style="background:linear-gradient(135deg,#3B9EE8,#2EC4B6)">
              {{ (currentUser?.nickname || currentUser?.username || '?')[0].toUpperCase() }}
            </div>
            <span class="text-sm font-medium text-gray-700 max-w-[80px] truncate">
              {{ currentUser?.nickname || currentUser?.username }}
            </span>
            <svg class="w-3.5 h-3.5 text-gray-400 transition-transform" :class="userMenuOpen ? 'rotate-180' : ''"
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>

          <!-- 下拉菜单 -->
          <Transition name="dropdown">
            <div v-if="userMenuOpen"
              class="absolute right-0 top-full mt-2 w-44 bg-white rounded-2xl shadow-xl border border-gray-100 py-1.5 z-50">
              <div class="px-4 py-2.5 border-b border-gray-50">
                <p class="text-xs text-gray-400">当前账号</p>
                <p class="text-sm font-semibold text-gray-800 truncate">{{ currentUser?.nickname || currentUser?.username }}</p>
              </div>
              <RouterLink to="/analytics" @click="userMenuOpen = false"
                class="flex items-center gap-2.5 px-4 py-2.5 text-sm text-gray-600 hover:text-primary hover:bg-primary/5 no-underline transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
                我的数据
              </RouterLink>
              <RouterLink to="/mood-calendar" @click="userMenuOpen = false"
                class="flex items-center gap-2.5 px-4 py-2.5 text-sm text-gray-600 hover:text-primary hover:bg-primary/5 no-underline transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                情绪日历
              </RouterLink>
              <RouterLink to="/profile" @click="userMenuOpen = false"
                class="flex items-center gap-2.5 px-4 py-2.5 text-sm text-gray-600 hover:text-primary hover:bg-primary/5 no-underline transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
                个人资料
              </RouterLink>
              <div class="border-t border-gray-50 mt-1 pt-1">
                <button @click="handleLogout"
                  class="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-500 hover:bg-red-50 transition-colors">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                  </svg>
                  退出登录
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <!-- Mobile toggle -->
      <button class="md:hidden p-2 rounded-xl text-gray-500 hover:bg-gray-100" @click="menuOpen = !menuOpen">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path v-if="!menuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Mobile menu -->
    <Transition name="slide-down">
      <div v-if="menuOpen" class="md:hidden bg-white border-t border-gray-100 shadow-lg px-5 py-4 space-y-1">
        <RouterLink
          v-for="item in navItems" :key="item.to" :to="item.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-700 hover:text-primary hover:bg-primary/5 font-medium no-underline"
          @click="menuOpen = false"
        >{{ item.label }}</RouterLink>
        <RouterLink to="/screening" class="btn-primary block text-center mt-3 no-underline" @click="menuOpen = false">
          开始筛测
        </RouterLink>
      </div>
    </Transition>
  </header>

  <!-- Page content -->
  <main class="pt-16 min-h-screen">
    <RouterView />
  </main>

  <!-- ===== SOS 浮动按钮 ===== -->
  <div class="fixed bottom-6 right-6 z-50">
    <Transition name="sos-pop">
      <div v-if="sosOpen" class="absolute bottom-16 right-0 w-64 bg-white rounded-2xl shadow-2xl border border-red-100 overflow-hidden">
        <div class="bg-red-50 px-4 py-3 border-b border-red-100">
          <div class="flex items-center justify-between">
            <span class="font-bold text-red-700 flex items-center gap-2">🆘 紧急求助热线</span>
            <button class="text-gray-400 hover:text-gray-600 text-xl leading-none" @click="sosOpen = false">×</button>
          </div>
          <p class="text-xs text-red-500 mt-1">专业人员 · 免费保密 · 24小时</p>
        </div>
        <div class="p-4 space-y-3">
          <div class="flex items-center gap-3 p-3 bg-rose-50 rounded-xl">
            <span class="text-xl">📞</span>
            <div>
              <div class="text-xs text-gray-500">全国心理援助热线</div>
              <div class="font-mono font-bold text-primary text-lg">400-161-9995</div>
            </div>
          </div>
          <div class="flex items-center gap-3 p-3 bg-rose-50 rounded-xl">
            <span class="text-xl">📞</span>
            <div>
              <div class="text-xs text-gray-500">北京心理危机热线</div>
              <div class="font-mono font-bold text-primary text-lg">010-82951332</div>
            </div>
          </div>
          <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
            <span class="text-xl">🚑</span>
            <div>
              <div class="text-xs text-gray-500">紧急医疗救援</div>
              <div class="font-mono font-bold text-red-600 text-lg">120</div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
    <button
      class="w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all duration-200 relative"
      :class="sosOpen ? 'bg-red-600 scale-110' : 'bg-red-500 hover:bg-red-600 hover:scale-105'"
      @click="sosOpen = !sosOpen"
    >
      <span v-if="!sosOpen" class="absolute inset-0 rounded-full bg-red-400 animate-ping opacity-40"></span>
      <span class="relative text-white font-black text-sm">SOS</span>
    </button>
  </div>

  <!-- ===== Footer ===== -->
  <footer class="bg-gray-900 text-gray-400">
    <!-- Top wave -->
    <div class="-mt-1">
      <svg viewBox="0 0 1440 40" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full">
        <path d="M0 40L60 33C120 27 240 13 360 10C480 7 600 13 720 17C840 20 960 20 1080 17C1200 13 1320 7 1380 3L1440 0V40H0Z" fill="#111827"/>
      </svg>
    </div>
    <div class="max-w-7xl mx-auto px-6 pt-2 pb-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-10">
        <!-- Brand -->
        <div class="md:col-span-2">
          <div class="flex items-center gap-2.5 mb-4">
            <XjLogo :size="32" />
            <span class="text-xl font-black text-white">心镜</span>
          </div>
          <p class="text-sm leading-relaxed mb-5 max-w-sm text-gray-400">
            融合面部表情、语音信号与心理量表，构建智能化抑郁风险评估与心理健康支持平台。
          </p>
          <div class="flex flex-wrap gap-2">
            <span class="text-xs bg-white/10 text-gray-300 px-3 py-1.5 rounded-full border border-white/10">PC端稳定实验</span>
            <span class="text-xs bg-white/10 text-gray-300 px-3 py-1.5 rounded-full border border-white/10">多模态智能评估</span>
            <span class="text-xs bg-white/10 text-gray-300 px-3 py-1.5 rounded-full border border-white/10">数字人陪伴</span>
          </div>
        </div>
        <!-- Links -->
        <div>
          <h4 class="text-white font-semibold mb-4 text-sm">功能模块</h4>
          <ul class="space-y-2.5 text-sm">
            <li v-for="item in [['辅助筛查','/screening'],['情绪陪伴','/companion'],['情绪日历','/mood-calendar'],['数据分析','/analytics']]" :key="item[0]">
              <RouterLink :to="item[1]" class="hover:text-white transition-colors no-underline flex items-center gap-2">
                <span class="w-1 h-1 rounded-full bg-primary/60 inline-block"></span>{{ item[0] }}
              </RouterLink>
            </li>
          </ul>
        </div>
        <div>
          <h4 class="text-white font-semibold mb-4 text-sm">其他</h4>
          <ul class="space-y-2.5 text-sm">
            <li v-for="item in [['关于我们','/about'],['隐私政策','#'],['使用条款','#']]" :key="item[0]">
              <RouterLink :to="item[1]" class="hover:text-white transition-colors no-underline flex items-center gap-2">
                <span class="w-1 h-1 rounded-full bg-teal-brand/60 inline-block"></span>{{ item[0] }}
              </RouterLink>
            </li>
          </ul>
        </div>
      </div>

      <div class="border-t border-white/10 mt-10 pt-6 flex flex-col sm:flex-row justify-between items-center gap-2 text-xs text-gray-500">
        <p>© 2025 心镜 · 第十九届中国大学生计算机设计大赛</p>
        <p>本平台仅供辅助参考，不构成正式医学诊断</p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.no-underline { text-decoration: none; }
.bg-primary\/8 { background-color: rgb(59 158 232 / 0.08); }
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.25s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }
.sos-pop-enter-active, .sos-pop-leave-active { transition: all 0.2s ease; }
.sos-pop-enter-from, .sos-pop-leave-to { opacity: 0; transform: translateY(8px) scale(0.95); }
.dropdown-enter-active, .dropdown-leave-active { transition: all 0.18s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-6px) scale(0.97); }
</style>
