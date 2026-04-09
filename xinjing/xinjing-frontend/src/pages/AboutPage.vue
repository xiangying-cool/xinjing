<script setup>
import BgBlobs from '../components/BgBlobs.vue'
import XjLogo from '../components/XjLogo.vue'

const team = [
  {
    name: '刘丰恺',
    role: '项目负责人 / 后端开发',
    desc: '负责整体项目规划、系统架构设计与后端 API 开发',
    gradient: 'from-primary to-blue-400',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
      d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5"/>`,
  },
  {
    name: '高嘉豪',
    role: 'AI算法 / 模型训练',
    desc: '负责多模态分析模型研发，包括面部表情识别与语音情感分析',
    gradient: 'from-teal-brand to-green-400',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
      d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25zm.75-12h9v9h-9v-9z"/>`,
  },
  {
    name: '刘宇轩',
    role: '产品设计 / 测试',
    desc: '负责产品原型规划、功能测试与用户体验验证',
    gradient: 'from-purple-400 to-primary',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
      d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42"/>`,
  },
  {
    name: '王艺',
    role: '心理学顾问 / 数据分析',
    desc: '负责心理量表内容把关、评估逻辑设计与测评数据分析',
    gradient: 'from-orange-brand to-amber-400',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
      d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"/>`,
  },
  {
    name: '杨熙锐',
    role: '前端开发 / UI设计',
    desc: '负责用户界面设计与前端功能实现，打造美观流畅的交互体验',
    gradient: 'from-pink-400 to-orange-brand',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
      d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456z"/>`,
  },
]

const tech = [
  { label: 'Vue 3 + Vite', desc: '前端框架', grad: 'from-green-400 to-teal-brand',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>` },
  { label: 'Tailwind CSS', desc: 'UI 样式', grad: 'from-blue-400 to-primary',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>` },
  { label: 'Python FastAPI', desc: '后端 API', grad: 'from-yellow-400 to-orange-brand',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"/>` },
  { label: 'MediaPipe', desc: '面部检测', grad: 'from-primary to-purple-400',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/>` },
  { label: 'OpenSMILE', desc: '语音特征', grad: 'from-teal-brand to-blue-400',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>` },
  { label: 'Claude API', desc: 'AI 对话', grad: 'from-orange-brand to-pink-400',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155"/>` },
]

const milestones = [
  { date: '2025-01', title: '项目立项', desc: '确定选题方向与技术路线，完成调研报告', dot: 'bg-primary' },
  { date: '2025-02', title: 'MVP 开发', desc: '完成基础功能原型，搭建核心框架', dot: 'bg-teal-brand' },
  { date: '2025-03', title: '功能完善', desc: '多模态分析模块集成，数字人对话上线', dot: 'bg-orange-brand' },
  { date: '2025-04', title: '测试迭代', desc: '用户测试与系统优化，准备参赛提交', dot: 'bg-purple-400' },
]

const missions = [
  {
    title: '早发现', desc: '通过多模态感知技术，在早期发现抑郁风险信号，帮助用户及时关注心理健康',
    grad: 'from-primary to-blue-400', bg: 'bg-sky-bg',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>`,
  },
  {
    title: '早干预', desc: '提供个性化情绪干预训练与数字人陪伴，在专业帮助到来前给予及时支持',
    grad: 'from-teal-brand to-green-400', bg: 'bg-mint-bg',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"/>`,
  },
  {
    title: '早康复', desc: '持续追踪情绪变化趋势，帮助用户和专业人员了解康复进展，调整支持方案',
    grad: 'from-orange-brand to-amber-400', bg: 'bg-orange-50',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z"/>`,
  },
]
</script>

<template>
  <div class="min-h-screen">

    <!-- ===== Hero ===== -->
    <section class="relative py-24 text-center bg-hero-gradient overflow-hidden">
      <BgBlobs />
      <div class="relative z-10 max-w-4xl mx-auto px-6">
        <div class="flex items-center justify-center gap-4 mb-6">
          <XjLogo :size="60" />
          <div class="text-6xl font-black bg-blue-green bg-clip-text text-transparent tracking-tight">心镜</div>
        </div>
        <h1 class="text-2xl font-bold text-gray-700 mb-4 leading-relaxed">
          基于多模态感知的抑郁症筛查与数字陪伴平台
        </h1>
        <p class="text-gray-500 leading-relaxed max-w-2xl mx-auto mb-8">
          心镜致力于通过人工智能技术，为大学生和青年群体提供便捷、私密、有温度的心理健康筛查与情绪陪伴服务，
          让每个人都能及早发现并关注自己的心理状态。
        </p>
        <div class="flex flex-wrap justify-center gap-3">
          <span class="inline-flex items-center gap-2 bg-white/80 backdrop-blur-sm text-primary text-sm px-5 py-2.5 rounded-full shadow-sm border border-primary/15 font-semibold">
            <svg class="w-4 h-4 text-orange-brand" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            第十九届中国大学生计算机设计大赛参赛作品
          </span>
        </div>
      </div>

      <!-- Wave -->
      <div class="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0 40L60 33C120 27 240 13 360 10C480 7 600 13 720 17C840 20 960 20 1080 17C1200 13 1320 7 1380 3L1440 0V40H0Z" fill="white"/>
        </svg>
      </div>
    </section>

    <!-- ===== Mission ===== -->
    <section class="py-20 bg-white">
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center mb-12">
          <div class="inline-flex items-center gap-2 bg-primary/8 text-primary text-xs font-semibold px-4 py-2 rounded-full mb-4">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/>
            </svg>
            我们的使命
          </div>
          <h2 class="text-3xl font-black text-gray-800">让心理健康筛查更简单、更智能、更有温度</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-7">
          <div v-for="m in missions" :key="m.title"
               class="group relative rounded-3xl p-8 text-center overflow-hidden border border-transparent hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1"
               :class="m.bg">
            <div class="absolute -top-8 -right-8 w-32 h-32 rounded-full opacity-10 bg-gradient-to-br" :class="m.grad"></div>
            <div class="relative">
              <div class="w-16 h-16 rounded-2xl bg-gradient-to-br shadow-sm flex items-center justify-center mx-auto mb-5 group-hover:scale-110 transition-transform duration-300" :class="m.grad">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-html="m.icon"></svg>
              </div>
              <h3 class="font-black text-xl text-gray-800 mb-3">{{ m.title }}</h3>
              <p class="text-gray-500 text-sm leading-relaxed">{{ m.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== Technology ===== -->
    <section class="py-20 bg-sky-bg relative overflow-hidden">
      <BgBlobs />
      <div class="relative z-10 max-w-5xl mx-auto px-6">
        <div class="text-center mb-12">
          <div class="inline-flex items-center gap-2 bg-teal-brand/10 text-teal-brand text-xs font-semibold px-4 py-2 rounded-full mb-4">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.25 9.75L16.5 12l-2.25 2.25m-4.5 0L7.5 12l2.25-2.25M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z"/>
            </svg>
            技术栈
          </div>
          <h2 class="text-3xl font-black text-gray-800">融合前沿 AI 技术与现代 Web 开发</h2>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div v-for="t in tech" :key="t.label"
               class="group bg-white rounded-2xl p-5 text-center shadow-card hover:shadow-card-hover transition-all duration-200 hover:-translate-y-1">
            <div class="w-12 h-12 rounded-2xl bg-gradient-to-br flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform duration-300" :class="t.grad">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-html="t.icon"></svg>
            </div>
            <div class="font-bold text-sm text-gray-800">{{ t.label }}</div>
            <div class="text-xs text-gray-400 mt-1">{{ t.desc }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== Timeline ===== -->
    <section class="py-20 bg-white">
      <div class="max-w-3xl mx-auto px-6">
        <div class="text-center mb-12">
          <div class="inline-flex items-center gap-2 bg-orange-brand/10 text-orange-brand text-xs font-semibold px-4 py-2 rounded-full mb-4">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            开发历程
          </div>
          <h2 class="text-3xl font-black text-gray-800">从想法到现实的每一步</h2>
        </div>
        <div class="relative pl-8">
          <!-- Line -->
          <div class="absolute left-3 top-2 bottom-2 w-0.5 bg-gradient-to-b from-primary via-teal-brand via-orange-brand to-purple-400 rounded-full"></div>

          <div v-for="(m, i) in milestones" :key="i" class="relative mb-8 last:mb-0 pl-8 group">
            <!-- Dot -->
            <div class="absolute -left-5 top-1 w-4 h-4 rounded-full border-2 border-white shadow-sm transition-transform duration-300 group-hover:scale-125" :class="m.dot"></div>

            <div class="bg-white rounded-2xl p-5 shadow-card hover:shadow-card-hover transition-all duration-200 border border-gray-100">
              <div class="flex items-center justify-between mb-1">
                <h3 class="font-bold text-gray-800">{{ m.title }}</h3>
                <span class="text-xs text-gray-400 bg-gray-100 px-3 py-1 rounded-full">{{ m.date }}</span>
              </div>
              <p class="text-gray-500 text-sm">{{ m.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== Team ===== -->
    <section class="py-20 bg-sky-bg relative overflow-hidden">
      <BgBlobs variant="warm" />
      <div class="relative z-10 max-w-6xl mx-auto px-6">
        <div class="text-center mb-12">
          <div class="inline-flex items-center gap-2 bg-purple-100 text-purple-600 text-xs font-semibold px-4 py-2 rounded-full mb-4">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z"/>
            </svg>
            团队成员
          </div>
          <h2 class="text-3xl font-black text-gray-800">五位怀揣热情的同学</h2>
          <p class="text-gray-500 mt-2">共同探索心理健康科技的边界</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
          <div v-for="m in team" :key="m.name"
               class="group bg-white rounded-2xl p-6 text-center shadow-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1 relative overflow-hidden">
            <!-- Top gradient bar -->
            <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r rounded-t-2xl" :class="m.gradient"></div>

            <!-- Avatar -->
            <div class="w-18 h-18 rounded-2xl bg-gradient-to-br flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 shadow-sm"
                 :class="m.gradient"
                 style="width:68px;height:68px">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-html="m.icon"></svg>
            </div>

            <!-- Name -->
            <h3 class="text-lg font-black text-gray-800 tracking-wide mb-2">{{ m.name }}</h3>

            <!-- Role -->
            <div class="inline-block bg-gray-50 border border-gray-100 text-gray-500 text-xs px-3 py-1.5 rounded-xl mb-3 font-medium leading-tight">
              {{ m.role }}
            </div>

            <!-- Desc -->
            <p class="text-gray-400 text-xs leading-relaxed">{{ m.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== Disclaimer ===== -->
    <section class="py-16 bg-white">
      <div class="max-w-3xl mx-auto px-6">
        <div class="relative bg-amber-50 border border-amber-200 rounded-3xl p-8 overflow-hidden">
          <div class="absolute top-0 right-0 w-32 h-32 rounded-full bg-amber-100 -translate-y-1/2 translate-x-1/2 opacity-50"></div>
          <div class="relative z-10 flex items-start gap-5">
            <div class="w-12 h-12 rounded-2xl bg-amber-100 flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/>
              </svg>
            </div>
            <div>
              <h3 class="font-black text-amber-800 text-lg mb-2">重要声明</h3>
              <p class="text-amber-700 text-sm leading-relaxed">
                心镜平台仅提供辅助性心理健康筛查，<strong>不构成正式医学诊断</strong>。
                若您的测评结果显示中度或重度风险，请及时寻求专业心理咨询师或精神科医生的帮助。
                如遇紧急情况，请拨打心理危机热线 <strong>400-161-9995</strong>。
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<style scoped>
.bg-primary\/8 { background-color: rgb(59 158 232 / 0.08); }
</style>
