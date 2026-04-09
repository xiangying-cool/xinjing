<script setup>
import { ref, onMounted } from 'vue'
import BgBlobs from '../components/BgBlobs.vue'
import XjLogo from '../components/XjLogo.vue'
import { useAuth } from '../composables/useAuth.js'
import { api } from '../services/api.js'

const visible = ref(false)
const { isLoggedIn, displayName, userId } = useAuth()

// ── 个性化数据 ──────────────────────────────────────────
const lastReport  = ref(null)   // { level, color, scale, date, id }
const moodStreak  = ref(0)
const todayMood   = ref(null)   // mood_key or null
const alerts      = ref([])     // 未处理的紧急预警

const MOOD_ICON = { sunny: '☀️', partly: '⛅', cloudy: '☁️', rainy: '🌧️', stormy: '⛈️' }

function calcStreak(records) {
  const today = new Date(); today.setHours(0,0,0,0)
  const fmt = d => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
  const map = {}
  records.forEach(r => { map[r.record_date] = r.mood_key })
  let count = 0, d = new Date(today)
  while (map[fmt(d)]) { count++; d.setDate(d.getDate()-1) }
  return count
}

onMounted(async () => {
  setTimeout(() => { visible.value = true }, 100)
  if (!isLoggedIn.value || !userId.value) return
  try {
    const [reports, moodRecords, alertList] = await Promise.all([
      api.get('/reports?limit=1').catch(() => []),
      api.get(`/mood-calendar?user_id=${userId.value}`).catch(() => []),
      api.get('/reports/alerts').catch(() => []),
    ])
    if (alertList?.length) alerts.value = alertList.filter(a => !a.is_handled)
    if (reports?.length > 0) {
      const r = reports[0]
      lastReport.value = {
        id:    r.id,
        level: r.report_json?.level,
        color: r.report_json?.color || '#22c55e',
        scale: r.report_json?.scale || '评估',
        date:  (r.report_json?.date || r.created_at || '').slice(0, 10),
      }
    }
    if (moodRecords?.length > 0) {
      moodStreak.value = calcStreak(moodRecords)
      const todayKey = new Date().toISOString().slice(0, 10)
      const rec = moodRecords.find(r => r.record_date === todayKey)
      if (rec) todayMood.value = rec.mood_key
    }
  } catch (e) {
    console.error('首页个性化数据加载失败:', e)
  }
})

const features = [
  {
    title: '多模态辅助筛查',
    desc: '融合面部表情分析、语音情感识别和标准量表，综合多维度数据进行抑郁风险评估。',
    gradient: 'from-blue-50 to-sky-100',
    iconBg: 'from-primary to-blue-400',
    border: 'border-blue-100',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
      d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/>`,
  },
  {
    title: '快捷心理测评',
    desc: '涵盖 PHQ-9、情绪状态、压力与睡眠等测试，帮助用户快速完成初筛流程。',
    gradient: 'from-orange-50 to-amber-50',
    iconBg: 'from-orange-brand to-amber-400',
    border: 'border-orange-100',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
      d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V19.5a2.25 2.25 0 002.25 2.25h.75"/>`,
  },
  {
    title: '智能评估报告',
    desc: '自动生成可视化报告，包括风险等级、量表结果、面部分析和个性化建议。',
    gradient: 'from-teal-brand/5 to-green-50',
    iconBg: 'from-teal-brand to-green-400',
    border: 'border-green-100',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
      d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z"/>`,
  },
  {
    title: '数字人陪伴对话',
    desc: '搭载 Agent 数字人，与用户进行倾听、安抚、情绪疏导和日常陪伴对话。',
    gradient: 'from-purple-50 to-blue-50',
    iconBg: 'from-purple-400 to-primary',
    border: 'border-purple-100',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
      d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155"/>`,
  },
]

const steps = [
  { num: '01', title: '注册即时信息', desc: '快速注册，填写基本健康信息', icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>`, color: 'from-primary to-blue-400' },
  { num: '02', title: '模态数据采集', desc: '开启摄像头与麦克风进行采集', icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 00-1.134-.175 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.039l-.821 1.316z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M16.5 12.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zM18.75 10.5h.008v.008h-.008V10.5z"/>`, color: 'from-teal-brand to-green-400' },
  { num: '03', title: '生成评估报告', desc: 'AI 综合分析，生成个性化报告', icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/>`, color: 'from-orange-brand to-amber-400' },
  { num: '04', title: '数字人陪伴疏导', desc: '智能陪伴，提供持续心理支持', icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"/>`, color: 'from-purple-400 to-pink-400' },
]

const showcases = [
  {
    title: '多模态智能评估',
    desc: '通过摄像头分析面部微表情，结合语音情绪识别和 PHQ-9 量表，构建多维度的抑郁风险评估模型。',
    tags: ['面部表情 AU 编码分析', '语音声学特征提取', '主客观量表综合评分'],
    gradient: 'from-blue-50 via-sky-bg to-white',
    iconGrad: 'from-primary to-blue-400',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>`,
    imgType: 'assessment',
  },
  {
    title: '量表评估报告',
    desc: '基于临床标准 PHQ-9 量表，综合多维度评分，自动生成专业的心理健康可视化评估报告。',
    tags: ['临床级量表标准评估', '风险等级可视化展示', '支持报告导出与分享'],
    gradient: 'from-teal-brand/5 via-mint-bg to-white',
    iconGrad: 'from-teal-brand to-green-400',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z"/>`,
    imgType: 'report',
  },
  {
    title: '数字人陪伴心理伴',
    desc: '搭载 AI Agent 数字人，通过对话提供情感倾听、压力疏导，给予用户持续温暖的心理陪伴。',
    tags: ['情感识别与实时响应', '个性化情绪干预训练', '24小时智能陪伴在线'],
    gradient: 'from-purple-50 via-blue-50 to-white',
    iconGrad: 'from-purple-400 to-primary',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155"/>`,
    imgType: 'companion',
  },
]

const scenarios = [
  {
    title: '优秀心理疏解',
    desc: '大学生面对学业压力、人际关系、就业焦虑等问题时，使用心镜进行自我评估与情绪疏导。',
    tags: ['学业压力', '人际关系', '就业焦虑'],
    iconGrad: 'from-blue-400 to-primary',
    bgDecor: 'from-blue-50 to-sky-100',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5"/>`,
  },
  {
    title: '家庭情绪疗愈',
    desc: '家庭成员间情绪互动监测，识别潜在心理问题，促进家庭心理健康与和谐氛围。',
    tags: ['亲子互动', '情绪监测', '和谐关系'],
    iconGrad: 'from-orange-brand to-amber-400',
    bgDecor: 'from-orange-50 to-amber-50',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"/>`,
  },
  {
    title: '心理专科辅助',
    desc: '辅助心理健康专业人员，提供标准化评估工具、趋势追踪和数字化治疗辅助工具。',
    tags: ['标准化评估', '效果追踪', '辅助治疗'],
    iconGrad: 'from-teal-brand to-green-400',
    bgDecor: 'from-teal-brand/10 to-green-50',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"/>`,
  },
]
</script>

<template>
  <!-- ====== Hero ====== -->
  <section class="relative overflow-hidden bg-hero-gradient min-h-[90vh] flex items-center">
    <BgBlobs />

    <div class="relative z-10 max-w-7xl mx-auto px-6 py-20 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
      <!-- Left -->
      <div class="transition-all duration-700" :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 bg-white/80 backdrop-blur-sm border border-primary/20 text-primary text-xs font-semibold px-4 py-2 rounded-full mb-7 shadow-sm">
          <span class="w-1.5 h-1.5 bg-primary rounded-full animate-pulse"></span>
          基于多模态感知技术 · AI 心理健康平台
        </div>

        <h1 class="text-4xl lg:text-[2.8rem] font-black text-gray-900 leading-[1.2] mb-6">
          心镜：基于多模态感知的<br/>
          <span class="relative inline-block">
            <span class="bg-blue-green bg-clip-text text-transparent">抑郁症筛查</span>
            <!-- Underline decoration -->
            <svg class="absolute -bottom-1 left-0 w-full" viewBox="0 0 200 8" fill="none">
              <path d="M2 6 Q100 2 198 6" stroke="url(#uGrad)" stroke-width="2.5" stroke-linecap="round"/>
              <defs>
                <linearGradient id="uGrad" x1="0" y1="0" x2="200" y2="0">
                  <stop offset="0%" stop-color="#3B9EE8"/>
                  <stop offset="100%" stop-color="#2EC4B6"/>
                </linearGradient>
              </defs>
            </svg>
          </span>
          与数字陪伴平台
        </h1>

        <p class="text-gray-500 text-lg leading-relaxed mb-9 max-w-lg">
          融合面部表情、语音信号与心理量表，搭建智能化抑郁风险评估与心理健康支持平台。
        </p>

        <div class="flex flex-wrap gap-4 mb-10">
          <RouterLink to="/screening" class="btn-primary text-base no-underline flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            立即开始筛测
          </RouterLink>
          <RouterLink to="/about" class="btn-outline text-base no-underline flex items-center gap-2">
            了解更多
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </RouterLink>
        </div>

        <!-- Stat chips -->
        <div class="flex flex-wrap gap-3">
          <div v-for="chip in ['PC端稳定实验','多模态智能评估','数字人陪伴字幕']" :key="chip"
               class="flex items-center gap-2 bg-white/70 backdrop-blur-sm border border-gray-200 rounded-full px-4 py-2 text-sm text-gray-600 shadow-sm">
            <svg class="w-3.5 h-3.5 text-primary flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd"/>
            </svg>
            {{ chip }}
          </div>
        </div>
      </div>

      <!-- Right: UI Mockup -->
      <div class="relative transition-all duration-700 delay-300" :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'">
        <!-- Main card -->
        <div class="bg-white/90 backdrop-blur-md rounded-3xl shadow-[0_20px_60px_rgba(59,158,232,0.15)] p-6 border border-white">
          <!-- Window bar -->
          <div class="flex items-center gap-1.5 mb-5">
            <span class="w-3 h-3 rounded-full bg-red-400"></span>
            <span class="w-3 h-3 rounded-full bg-yellow-400"></span>
            <span class="w-3 h-3 rounded-full bg-green-400"></span>
            <span class="ml-3 text-xs text-gray-400 bg-gray-100 rounded-full px-3 py-0.5">心镜 · 多模态评估</span>
          </div>

          <!-- User row -->
          <div class="flex items-center gap-3 mb-5">
            <div class="w-10 h-10 rounded-full bg-blue-green flex items-center justify-center text-white text-sm font-bold">张</div>
            <div class="flex-1">
              <div class="text-sm font-semibold text-gray-800">张同学</div>
              <div class="text-xs text-gray-400">上次评估：3天前</div>
            </div>
            <span class="text-xs bg-green-100 text-green-600 px-2.5 py-1 rounded-full font-medium flex items-center gap-1">
              <span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>评估中
            </span>
          </div>

          <!-- PHQ-9 bars -->
          <div class="bg-gray-50 rounded-2xl p-4 mb-4">
            <div class="flex items-center justify-between mb-3">
              <span class="text-xs font-semibold text-gray-600">PHQ-9 各维度评分</span>
              <span class="text-xs text-primary font-bold">7 / 27</span>
            </div>
            <div class="flex items-end gap-1.5 h-14">
              <div v-for="(h, i) in [33,67,33,100,0,33,33,0,0]" :key="i"
                   class="flex-1 rounded-t-md transition-all duration-1000"
                   :class="i === 1 || i === 3 ? 'bg-orange-brand/70' : 'bg-primary/30'"
                   :style="{ height: visible ? h + '%' : '0%', transitionDelay: (i * 80) + 'ms' }">
              </div>
            </div>
            <div class="grid grid-cols-9 gap-1 mt-1 text-[8px] text-gray-400 text-center">
              <span v-for="l in ['兴趣','情绪','睡眠','精力','食欲','自评','注意','运动','念头']" :key="l">{{ l }}</span>
            </div>
          </div>

          <!-- Risk row -->
          <div class="flex items-center justify-between p-3 bg-blue-50 rounded-xl mb-3">
            <span class="text-sm font-medium text-gray-700">综合风险等级</span>
            <div class="flex items-center gap-2.5">
              <div class="flex gap-1">
                <span v-for="i in 5" :key="i" class="w-5 h-1.5 rounded-full" :class="i <= 2 ? 'bg-primary' : 'bg-gray-200'"></span>
              </div>
              <span class="text-sm text-primary font-bold">轻度</span>
            </div>
          </div>

          <!-- Action btn -->
          <div class="flex gap-2">
            <button class="flex-1 bg-blue-green text-white text-xs py-2 rounded-xl font-medium">查看完整报告</button>
            <button class="flex-1 border border-primary/30 text-primary text-xs py-2 rounded-xl font-medium">与数字人对话</button>
          </div>
        </div>

        <!-- Floating card: Voice -->
        <div class="absolute -left-10 top-1/4 bg-white rounded-2xl shadow-card-hover p-4 w-44 animate-float border border-gray-100">
          <div class="flex items-center gap-2 mb-3">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-teal-brand to-green-400 flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
              </svg>
            </div>
            <span class="text-xs font-semibold text-gray-700">语音分析</span>
          </div>
          <div class="flex items-end gap-0.5 h-8 mb-2">
            <div v-for="(h,i) in [40,70,55,90,45,75,60,80,50,65]" :key="i"
                 class="flex-1 rounded-sm bg-teal-brand/60"
                 :style="{ height: h + '%' }"></div>
          </div>
          <div class="flex gap-1 flex-wrap">
            <span class="text-[10px] bg-blue-100 text-primary px-1.5 py-0.5 rounded-full">平稳</span>
            <span class="text-[10px] bg-green-100 text-green-600 px-1.5 py-0.5 rounded-full">积极</span>
          </div>
        </div>

        <!-- Floating card: Face -->
        <div class="absolute -right-6 bottom-16 bg-white rounded-2xl shadow-card-hover p-4 w-44 animate-float border border-gray-100" style="animation-delay:1.2s">
          <div class="flex items-center gap-2 mb-3">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-orange-brand to-amber-400 flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.182 15.182a4.5 4.5 0 01-6.364 0M21 12a9 9 0 11-18 0 9 9 0 0118 0zM9.75 9.75c0 .414-.168.75-.375.75S9 10.164 9 9.75 9.168 9 9.375 9s.375.336.375.75zm-.375 0h.008v.015h-.008V9.75zm5.625 0c0 .414-.168.75-.375.75s-.375-.336-.375-.75.168-.75.375-.75.375.336.375.75zm-.375 0h.008v.015h-.008V9.75z"/>
              </svg>
            </div>
            <span class="text-xs font-semibold text-gray-700">面部分析</span>
          </div>
          <div class="space-y-1.5">
            <div v-for="(e,i) in [{l:'平静',w:45,c:'bg-primary'},{l:'沉思',w:30,c:'bg-purple-400'},{l:'轻松',w:25,c:'bg-green-400'}]" :key="i">
              <div class="flex justify-between text-[10px] text-gray-500 mb-0.5"><span>{{ e.l }}</span><span>{{ e.w }}%</span></div>
              <div class="h-1 bg-gray-100 rounded-full"><div class="h-1 rounded-full" :class="e.c" :style="{width: e.w+'%'}"></div></div>
            </div>
          </div>
        </div>

        <!-- Top right floating badge -->
        <div class="absolute -top-4 right-10 bg-white rounded-xl shadow-card px-3 py-2 flex items-center gap-2 border border-gray-100">
          <div class="w-6 h-6 rounded-full bg-blue-green flex items-center justify-center">
            <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd"/>
            </svg>
          </div>
          <span class="text-xs font-semibold text-gray-700">AI 分析完成</span>
        </div>
      </div>
    </div>

    <!-- Wave -->
    <div class="absolute bottom-0 left-0 right-0 z-10">
      <svg viewBox="0 0 1440 60" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M0 60L60 50C120 40 240 20 360 15C480 10 600 20 720 25C840 30 960 30 1080 25C1200 20 1320 10 1380 5L1440 0V60H0Z" fill="white"/>
      </svg>
    </div>
  </section>

  <!-- ====== 紧急预警横幅（有未处理警报时显示） ====== -->
  <section v-if="isLoggedIn && alerts.length > 0" class="bg-red-50 border-b border-red-100">
    <div class="max-w-7xl mx-auto px-6 py-4 space-y-3">
      <div
        v-for="alert in alerts"
        :key="alert.id"
        class="flex items-start gap-3 p-4 bg-white rounded-2xl border border-red-200 shadow-sm"
      >
        <div class="w-9 h-9 rounded-xl bg-red-100 flex items-center justify-center flex-shrink-0 mt-0.5">
          <span class="text-lg">⚠️</span>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-bold text-red-700">{{ alert.alert_title }}</p>
          <p class="text-xs text-red-600 mt-0.5 leading-relaxed">{{ alert.alert_content }}</p>
          <p class="text-[10px] text-red-400 mt-1">{{ alert.created_at?.slice(0, 10) }}</p>
        </div>
        <RouterLink
          to="/companion"
          class="text-xs font-medium text-red-600 border border-red-200 px-3 py-1.5 rounded-xl hover:bg-red-50 transition-colors no-underline flex-shrink-0 whitespace-nowrap"
        >
          寻求帮助
        </RouterLink>
      </div>
    </div>
  </section>

  <!-- ====== 个人概况（登录后显示） ====== -->
  <section v-if="isLoggedIn" class="bg-white border-b border-gray-100">
    <div class="max-w-7xl mx-auto px-6 py-5">
      <div class="flex flex-wrap items-center gap-4">
        <!-- 问候 -->
        <div class="flex items-center gap-2.5 mr-2">
          <div class="w-9 h-9 rounded-full bg-blue-green flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            {{ displayName?.slice(0,1) || '我' }}
          </div>
          <div>
            <p class="text-xs text-gray-400">欢迎回来</p>
            <p class="text-sm font-bold text-gray-800">{{ displayName }}</p>
          </div>
        </div>

        <div class="h-8 w-px bg-gray-200 hidden sm:block"></div>

        <!-- 最近报告 -->
        <RouterLink
          v-if="lastReport"
          :to="`/report/${lastReport.id}`"
          class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors no-underline"
        >
          <span class="text-xs text-gray-400">最近评估</span>
          <span class="text-xs font-bold px-2 py-0.5 rounded-full" :style="{ color: lastReport.color, backgroundColor: lastReport.color + '18' }">
            {{ lastReport.level }}
          </span>
          <span class="text-xs text-gray-400">{{ lastReport.scale }} · {{ lastReport.date }}</span>
          <svg class="w-3.5 h-3.5 text-gray-400 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </RouterLink>
        <span v-else class="text-xs text-gray-400 px-3">暂无评估记录</span>

        <div class="h-8 w-px bg-gray-200 hidden sm:block"></div>

        <!-- 打卡连续 -->
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-50">
          <span class="text-base">🔥</span>
          <span class="text-xs font-bold text-amber-700">连续打卡 {{ moodStreak }} 天</span>
        </div>

        <!-- 今日情绪 -->
        <div v-if="todayMood" class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-sky-50">
          <span class="text-base">{{ MOOD_ICON[todayMood] }}</span>
          <span class="text-xs font-medium text-sky-700">今天已打卡</span>
        </div>
        <RouterLink v-else to="/mood-calendar" class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-dashed border-gray-300 hover:border-primary/50 transition-colors no-underline">
          <span class="text-base">🌀</span>
          <span class="text-xs text-gray-500">记录今日心情</span>
        </RouterLink>

        <!-- 快捷操作 -->
        <div class="ml-auto flex gap-2">
          <RouterLink to="/screening" class="text-xs font-medium text-white bg-primary px-3 py-1.5 rounded-lg hover:bg-primary/90 transition-colors no-underline">
            开始筛测
          </RouterLink>
          <RouterLink to="/companion" class="text-xs font-medium text-primary border border-primary/30 px-3 py-1.5 rounded-lg hover:bg-primary/5 transition-colors no-underline">
            情绪陪伴
          </RouterLink>
        </div>
      </div>
    </div>
  </section>

  <!-- ====== Feature Cards ====== -->
  <section class="py-24 bg-white">
    <div class="max-w-7xl mx-auto px-6">
      <!-- Section header -->
      <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-14">
        <div>
          <div class="inline-flex items-center gap-2 bg-primary/8 text-primary text-xs font-semibold px-4 py-2 rounded-full mb-4">
            <span class="w-1.5 h-1.5 bg-primary rounded-full"></span>
            核心功能
          </div>
          <h2 class="text-3xl font-black text-gray-800 leading-tight">全面守护心理健康</h2>
          <p class="text-gray-400 mt-2 text-sm">四大能力模块，构建完整的心理健康管理闭环</p>
        </div>
        <RouterLink to="/screening" class="hidden md:inline-flex items-center gap-1.5 text-sm text-primary font-semibold hover:gap-3 transition-all no-underline">
          立即体验
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
          </svg>
        </RouterLink>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div v-for="(f, i) in features" :key="i"
             class="group relative bg-white rounded-3xl border border-gray-100 p-7 hover:border-primary/15 hover:shadow-[0_16px_48px_rgba(59,158,232,0.10)] transition-all duration-300 hover:-translate-y-2 overflow-hidden flex flex-col">
          <!-- Number watermark -->
          <span class="absolute -bottom-2 -right-1 text-[88px] font-black leading-none select-none text-gray-50/80 group-hover:text-primary/[0.04] transition-colors duration-300">{{ String(i+1).padStart(2,'0') }}</span>

          <!-- Icon -->
          <div class="relative w-13 h-13 w-[52px] h-[52px] rounded-2xl bg-gradient-to-br flex items-center justify-center shadow-sm mb-6 flex-shrink-0"
               :class="f.iconBg">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-html="f.icon"></svg>
          </div>

          <!-- Text -->
          <div class="relative flex-1">
            <h3 class="font-bold text-gray-800 text-[15px] mb-2.5 leading-snug">{{ f.title }}</h3>
            <p class="text-gray-400 text-sm leading-relaxed">{{ f.desc }}</p>
          </div>

          <!-- Bottom hover accent -->
          <div class="absolute bottom-0 left-7 right-7 h-[2px] rounded-full scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left bg-gradient-to-r" :class="f.iconBg"></div>
        </div>
      </div>
    </div>
  </section>

  <!-- ====== How It Works ====== -->
  <section class="py-24 relative overflow-hidden" style="background: linear-gradient(160deg,#F0F7FF 0%,#F8F0FF 50%,#F0FFF8 100%)">
    <BgBlobs variant="cool" />
    <div class="relative z-10 max-w-7xl mx-auto px-6">
      <div class="text-center mb-16">
        <div class="inline-flex items-center gap-2 bg-white/80 text-primary text-xs font-semibold px-4 py-2 rounded-full mb-5 border border-primary/15 shadow-sm">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
          </svg>
          使用流程
        </div>
        <h2 class="text-3xl font-black text-gray-800">四步完成评估</h2>
        <p class="text-gray-400 mt-2 text-sm">轻松了解心理状态，开启心理健康之旅</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 relative">
        <!-- Dashed connector line -->
        <div class="hidden lg:block absolute top-[52px] left-[calc(12.5%+44px)] right-[calc(12.5%+44px)] border-t-2 border-dashed border-primary/20 z-0"></div>

        <div v-for="(step, i) in steps" :key="i"
             class="group relative bg-white/80 backdrop-blur rounded-3xl border border-white shadow-sm hover:shadow-[0_12px_40px_rgba(59,158,232,0.12)] hover:border-primary/20 transition-all duration-300 hover:-translate-y-1.5 p-6 flex flex-col items-center text-center z-10">

          <!-- Step badge -->
          <div class="relative mb-5">
            <!-- Icon circle with step number badge -->
            <div class="w-[88px] h-[88px] rounded-full bg-gradient-to-br flex items-center justify-center shadow-md group-hover:scale-105 transition-transform duration-300"
                 :class="step.color">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-html="step.icon"></svg>
            </div>
            <!-- Step number chip -->
            <div class="absolute -top-1 -right-1 w-7 h-7 rounded-full bg-white border-2 flex items-center justify-center text-[11px] font-black shadow-sm"
                 :class="[step.color.split(' ')[1] === 'to-blue-400' ? 'text-primary border-primary/20' : step.color.split(' ')[1] === 'to-green-400' ? 'text-teal-brand border-teal-brand/20' : step.color.split(' ')[1] === 'to-amber-400' ? 'text-orange-brand border-orange-brand/20' : 'text-purple-500 border-purple-200']">
              {{ step.num }}
            </div>
          </div>

          <h3 class="font-bold text-gray-800 mb-1.5 text-[15px]">{{ step.title }}</h3>
          <p class="text-gray-400 text-xs leading-relaxed">{{ step.desc }}</p>

          <!-- Arrow (between cards) -->
          <div v-if="i < 3" class="hidden lg:flex absolute -right-3 top-[50px] z-20 w-6 h-6 rounded-full bg-white border border-gray-100 shadow-sm items-center justify-center text-gray-300">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ====== Feature Showcase ====== -->
  <section class="py-24 bg-white">
    <div class="max-w-7xl mx-auto px-6">
      <div class="text-center mb-14">
        <div class="inline-flex items-center gap-2 bg-teal-brand/10 text-teal-brand text-xs font-semibold px-4 py-2 rounded-full mb-5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
          </svg>
          三大核心模块
        </div>
        <h2 class="text-3xl font-black text-gray-800">核心功能展示</h2>
        <p class="text-gray-400 mt-2 text-sm">全方位覆盖心理健康管理的每个环节</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div v-for="(s, i) in showcases" :key="i"
             class="group rounded-3xl border border-gray-100 overflow-hidden hover:shadow-[0_20px_60px_rgba(59,158,232,0.10)] hover:border-primary/15 transition-all duration-300 hover:-translate-y-2 flex flex-col bg-white">

          <!-- Mockup area - redesigned with floating card style -->
          <div class="relative h-56 overflow-hidden flex items-center justify-center"
               :style="`background: linear-gradient(135deg, ${i===0?'#EFF6FF,#E0F2FE':i===1?'#F0FDF9,#DCFCE7':'#F5F3FF,#EDE9FE'})`">

            <!-- Decorative background circles -->
            <div class="absolute -top-8 -right-8 w-32 h-32 rounded-full opacity-20"
                 :style="`background: ${i===0?'#3B9EE8':i===1?'#2EC4B6':'#8B5CF6'}`"></div>
            <div class="absolute -bottom-6 -left-6 w-24 h-24 rounded-full opacity-10"
                 :style="`background: ${i===0?'#3B9EE8':i===1?'#2EC4B6':'#8B5CF6'}`"></div>
            <div class="absolute top-6 left-8 w-3 h-3 rounded-full opacity-40"
                 :style="`background: ${i===0?'#3B9EE8':i===1?'#2EC4B6':'#8B5CF6'}`"></div>
            <div class="absolute bottom-8 right-12 w-2 h-2 rounded-full opacity-30"
                 :style="`background: ${i===0?'#3B9EE8':i===1?'#2EC4B6':'#8B5CF6'}`"></div>

            <!-- Assessment mockup -->
            <template v-if="s.imgType === 'assessment'">
              <div class="bg-white/90 backdrop-blur rounded-2xl shadow-[0_8px_32px_rgba(59,158,232,0.15)] p-4 w-52 group-hover:shadow-[0_12px_40px_rgba(59,158,232,0.20)] transition-shadow duration-300">
                <div class="flex items-center gap-2 mb-3">
                  <div class="w-8 h-8 rounded-xl bg-blue-green flex items-center justify-center">
                    <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.182 15.182a4.5 4.5 0 01-6.364 0M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                  </div>
                  <div>
                    <div class="h-2 bg-gray-200 rounded w-20 mb-1"></div>
                    <div class="h-1.5 bg-primary/30 rounded w-14"></div>
                  </div>
                </div>
                <div class="flex items-end gap-1 h-12 mb-2">
                  <div v-for="(h,j) in [60,90,50,100,30,70,55,40,25]" :key="j"
                       class="flex-1 rounded-t transition-all duration-700"
                       :class="j===3||j===1?'bg-orange-brand/70':'bg-primary/30'"
                       :style="{height:h+'%'}"></div>
                </div>
                <div class="h-1.5 bg-gray-100 rounded-full">
                  <div class="h-1.5 bg-blue-green rounded-full w-2/5"></div>
                </div>
              </div>
            </template>

            <!-- Report mockup -->
            <template v-else-if="s.imgType === 'report'">
              <div class="bg-white/90 backdrop-blur rounded-2xl shadow-[0_8px_32px_rgba(46,196,182,0.15)] p-4 w-52">
                <div class="flex items-center gap-2 mb-3">
                  <div class="h-2 bg-gray-200 rounded flex-1"></div>
                  <span class="text-xs bg-yellow-100 text-yellow-600 px-2 py-0.5 rounded-full font-medium">轻度</span>
                </div>
                <div class="flex gap-3 mb-3">
                  <div class="relative w-14 h-14 flex-shrink-0">
                    <svg viewBox="0 0 36 36" class="w-14 h-14 -rotate-90">
                      <circle cx="18" cy="18" r="14" fill="none" stroke="#f3f4f6" stroke-width="4"/>
                      <circle cx="18" cy="18" r="14" fill="none" stroke="#3B9EE8" stroke-width="4"
                              stroke-dasharray="35 65" stroke-linecap="round"/>
                    </svg>
                    <div class="absolute inset-0 flex items-center justify-center text-xs font-bold text-primary">7</div>
                  </div>
                  <div class="space-y-1.5 flex-1">
                    <div v-for="(c,j) in ['bg-primary/40','bg-teal-brand/40','bg-orange-brand/40','bg-purple-400/40']" :key="j"
                         class="h-1.5 rounded-full" :class="c" :style="{width:(80-j*15)+'%'}"></div>
                  </div>
                </div>
                <div class="space-y-1.5">
                  <div v-for="j in 2" :key="j" class="h-2 rounded-full bg-gray-100"></div>
                </div>
              </div>
            </template>

            <!-- Companion mockup -->
            <template v-else>
              <div class="bg-white/90 backdrop-blur rounded-2xl shadow-[0_8px_32px_rgba(139,92,246,0.15)] p-4 w-52">
                <div class="flex items-center gap-2 mb-3 pb-2 border-b border-gray-100">
                  <div class="w-7 h-7 rounded-full bg-blue-green flex items-center justify-center text-white text-xs font-bold">心</div>
                  <div class="h-2 bg-gray-200 rounded w-20"></div>
                  <div class="ml-auto w-2 h-2 rounded-full bg-green-400"></div>
                </div>
                <div class="space-y-2">
                  <div class="flex gap-1.5">
                    <div class="w-6 h-6 rounded-full bg-blue-green flex-shrink-0"></div>
                    <div class="bg-blue-50 rounded-xl rounded-tl-none px-3 py-1.5 flex-1">
                      <div class="h-1.5 bg-primary/30 rounded mb-1"></div>
                      <div class="h-1.5 bg-primary/20 rounded w-3/4"></div>
                    </div>
                  </div>
                  <div class="flex gap-1.5 justify-end">
                    <div class="bg-orange-50 rounded-xl rounded-tr-none px-3 py-1.5">
                      <div class="h-1.5 bg-orange-brand/40 rounded w-16"></div>
                    </div>
                    <div class="w-6 h-6 rounded-full bg-gray-200 flex-shrink-0"></div>
                  </div>
                  <div class="flex gap-1.5">
                    <div class="w-6 h-6 rounded-full bg-blue-green flex-shrink-0"></div>
                    <div class="bg-blue-50 rounded-xl rounded-tl-none px-3 py-1.5 flex-1">
                      <div class="h-1.5 bg-primary/30 rounded"></div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </div>

          <!-- Text body -->
          <div class="p-6 flex-1 flex flex-col">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br flex items-center justify-center shadow-sm flex-shrink-0" :class="s.iconGrad">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-html="s.icon"></svg>
              </div>
              <h3 class="font-bold text-gray-800 leading-snug">{{ s.title }}</h3>
            </div>
            <p class="text-gray-400 text-sm leading-relaxed mb-5">{{ s.desc }}</p>
            <!-- Tags as check list -->
            <ul class="space-y-2 mt-auto">
              <li v-for="tag in s.tags" :key="tag" class="flex items-center gap-2.5 text-sm text-gray-600">
                <span class="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <svg class="w-3 h-3 text-primary" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                  </svg>
                </span>
                {{ tag }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Bottom chips -->
      <div class="flex flex-wrap justify-center gap-3 mt-12">
        <RouterLink v-for="chip in [['AI 多模态分析','/screening'],['快捷心理测评','/screening'],['智能评估报告','/analytics'],['数字人心理伴','/companion']]"
                    :key="chip[0]" :to="chip[1]"
                    class="tag-chip no-underline">
          {{ chip[0] }}
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </RouterLink>
      </div>
    </div>
  </section>

  <!-- ====== Scenarios ====== -->
  <section class="py-24 relative overflow-hidden" style="background: linear-gradient(180deg,#F8FAFF 0%,#FFF8F5 100%)">
    <BgBlobs variant="warm" />
    <div class="relative z-10 max-w-7xl mx-auto px-6">
      <div class="text-center mb-14">
        <div class="inline-flex items-center gap-2 bg-orange-brand/10 text-orange-brand text-xs font-semibold px-4 py-2 rounded-full mb-5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          应用场景
        </div>
        <h2 class="text-3xl font-black text-gray-800">覆盖多类人群</h2>
        <p class="text-gray-400 mt-2 text-sm">提供专属心理支持，守护每一位用户</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div v-for="(s, i) in scenarios" :key="i"
             class="bg-white rounded-3xl overflow-hidden border border-gray-100 hover:shadow-[0_16px_48px_rgba(245,135,58,0.10)] hover:border-orange-100 transition-all duration-300 hover:-translate-y-2 group">

          <!-- Illustration area -->
          <div class="h-48 bg-gradient-to-br relative overflow-hidden flex items-center justify-center" :class="s.bgDecor">
            <!-- Abstract geometric decoration -->
            <div class="absolute top-0 right-0 w-32 h-32 rounded-full bg-white/15 -translate-y-1/2 translate-x-1/2"></div>
            <div class="absolute bottom-0 left-0 w-20 h-20 rounded-full bg-white/10 translate-y-1/2 -translate-x-1/2"></div>
            <!-- Ring decorations -->
            <div class="absolute top-4 right-8 w-8 h-8 rounded-full border-2 border-white/40"></div>
            <div class="absolute bottom-6 left-10 w-5 h-5 rounded-full border-2 border-white/30"></div>
            <!-- Dot grid -->
            <div class="absolute top-3 left-3 grid grid-cols-3 gap-1">
              <span v-for="k in 9" :key="k" class="w-1 h-1 rounded-full bg-white/30"></span>
            </div>

            <!-- Main icon -->
            <div class="relative z-10 w-[72px] h-[72px] rounded-2xl bg-gradient-to-br shadow-[0_8px_24px_rgba(0,0,0,0.15)] flex items-center justify-center group-hover:scale-110 transition-transform duration-300" :class="s.iconGrad">
              <svg class="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-html="s.icon"></svg>
            </div>
          </div>

          <!-- Card body -->
          <div class="p-6">
            <h3 class="font-bold text-gray-800 text-[17px] mb-2 leading-snug">{{ s.title }}</h3>
            <p class="text-gray-400 text-sm leading-relaxed mb-5">{{ s.desc }}</p>
            <div class="flex flex-wrap gap-2">
              <span v-for="tag in s.tags" :key="tag"
                    class="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border"
                    :class="i===0?'bg-blue-50 text-primary border-blue-100':i===1?'bg-orange-50 text-orange-brand border-orange-100':'bg-teal-brand/5 text-teal-brand border-teal-brand/20'">
                <span class="w-1 h-1 rounded-full inline-block flex-shrink-0"
                      :class="i===0?'bg-primary':i===1?'bg-orange-brand':'bg-teal-brand'"></span>
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ====== CTA ====== -->
  <section class="py-20 bg-white">
    <div class="max-w-3xl mx-auto px-6">
      <div class="relative bg-gradient-to-br from-sky-bg to-mint-bg rounded-3xl p-12 border border-primary/10 overflow-hidden text-center">
        <BgBlobs />
        <div class="relative z-10">
          <XjLogo :size="48" class="mx-auto mb-4" />
          <h2 class="text-3xl font-black text-gray-800 mb-2">使用说明与隐私承诺</h2>
          <p class="text-gray-400 text-sm mb-7">我们重视您的隐私，请放心使用</p>
          <ul class="text-gray-500 text-sm space-y-3 text-left max-w-xl mx-auto mb-9">
            <li v-for="tip in [
              '本平台采集的面部图像与语音数据仅用于本次评估分析，不做任何存储与第三方共享。',
              '评估结果仅供参考，不构成正式医学诊断，严重情况请及时寻求专业医疗帮助。',
              '建议在安静私密环境中使用，确保摄像头与麦克风权限正常开启，以获得最佳评估效果。'
            ]" :key="tip" class="flex items-start gap-3">
              <svg class="w-4 h-4 text-primary mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd"/>
              </svg>
              {{ tip }}
            </li>
          </ul>
          <RouterLink to="/screening" class="btn-primary text-base no-underline inline-flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            立即开始筛测
          </RouterLink>
          <p class="text-xs text-gray-400 mt-4">遵循 CC 相关隐私标准及实现相关知规程</p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.no-underline { text-decoration: none; }
.bg-primary\/8 { background-color: rgb(59 158 232 / 0.08); }
</style>
