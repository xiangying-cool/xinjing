<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ref, reactive, computed, onMounted } from 'vue'
import { api } from '../services/api.js'

const route = useRoute()
const router = useRouter()
const mounted = ref(false)

// ─── Demo / fallback 数据 ────────────────────────────────────────────────────
const DEMO = {
  type: 'phq9',
  scale: 'PHQ-9',
  total: 7,
  max: 27,
  level: '轻度抑郁',
  color: '#eab308',
  desc: '存在轻度抑郁倾向，建议关注情绪状态，适当自我调适。',
  date: '2025-03-08 14:32',
  answers: [1, 2, 1, 1, 0, 1, 1, 0, 0],
}

// 先用 localStorage 数据（或 DEMO）填充，onMounted 里再从后端更新
const localSaved = (() => {
  try { return JSON.parse(localStorage.getItem('xj_screening_result') || 'null') } catch { return null }
})()

const raw = reactive({ ...(localSaved || DEMO) })

// ─── PHQ-9 条目标签 ──────────────────────────────────────────────────────────
const itemLabels = {
  phq9: ['兴趣缺乏', '情绪低落', '睡眠障碍', '疲乏无力', '食欲异常', '自我否定', '注意力差', '运动迟缓', '自杀意念'],
  sds:  ['情绪低落', '晨重性', '易哭泣', '睡眠问题', '食欲变化', '性兴趣', '体重下降', '便秘', '心跳加速', '易疲乏',
         '思维清晰', '做事能力', '坐立不安', '对未来', '易激怒', '决策能力', '自我价值', '生活意义', '自杀念头', '兴趣保持'],
  ais:  ['入睡时间', '夜间苏醒', '早醒', '睡眠时长', '睡眠质量', '白天情绪', '白天功能', '白天嗜睡'],
  pss:  ['失控感', '事务堆积', '压力紧张', '顺利应对', '如愿发展', '无法应对', '控制烦恼', '掌控全局', '控制失常', '困难堆积'],
}

const labels = itemLabels[raw.type] || itemLabels.phq9

// 分项数据
const scoreItems = computed(() => {
  const ans = raw.answers || []
  return labels.map((label, i) => ({ label, score: ans[i] ?? 0 }))
})

// 等级颜色 Tailwind class
const levelClass = computed(() => {
  const c = raw.color
  if (c === '#22c55e' || c === '#27ae60') return { bg: 'bg-green-50 border-green-200', text: 'text-green-500' }
  if (c === '#eab308') return { bg: 'bg-yellow-50 border-yellow-200', text: 'text-yellow-500' }
  if (c === '#f97316') return { bg: 'bg-orange-50 border-orange-200', text: 'text-orange-500' }
  if (c === '#ef4444' || c === '#e74c3c') return { bg: 'bg-red-50 border-red-200', text: 'text-red-400' }
  return { bg: 'bg-red-50 border-red-300', text: 'text-red-600' }
})

// 分级进度条：各量表的分级段
const ranges = {
  phq9: [
    { label: '无症状', max: 4,  color: '#22c55e' },
    { label: '轻度',   max: 9,  color: '#eab308' },
    { label: '中度',   max: 14, color: '#f97316' },
    { label: '中重度', max: 19, color: '#ef4444' },
    { label: '重度',   max: 27, color: '#dc2626' },
  ],
  sds: [
    { label: '正常',   max: 52,  color: '#22c55e' },
    { label: '轻度',   max: 62,  color: '#eab308' },
    { label: '中度',   max: 72,  color: '#f97316' },
    { label: '重度',   max: 100, color: '#dc2626' },
  ],
  ais: [
    { label: '无障碍', max: 4,  color: '#22c55e' },
    { label: '可疑',   max: 10, color: '#eab308' },
    { label: '轻度',   max: 14, color: '#f97316' },
    { label: '中度',   max: 20, color: '#ef4444' },
    { label: '重度',   max: 32, color: '#dc2626' },
  ],
  pss: [
    { label: '低压力', max: 13, color: '#22c55e' },
    { label: '中压力', max: 26, color: '#eab308' },
    { label: '高压力', max: 40, color: '#dc2626' },
  ],
  ai_predict: [
    { label: '暂无倾向', max: 64,  color: '#27ae60' },
    { label: '可能抑郁', max: 100, color: '#e74c3c' },
  ],
}

const currentRanges = computed(() => ranges[raw.type] || ranges.phq9)

// 当前分数落在哪个区间（高亮该段）
const activeRangeIndex = computed(() => {
  const rs = currentRanges.value
  for (let i = 0; i < rs.length; i++) {
    if (raw.total <= rs[i].max) return i
  }
  return rs.length - 1
})

// 面部和语音（demo 固定值，实际应从后端获取）
const faceEmotions = [
  { label: '平静',   value: 45, color: '#3B9EE8' },
  { label: '轻微焦虑', value: 25, color: '#FBBF24' },
  { label: '沉思',   value: 20, color: '#A78BFA' },
  { label: '其他',   value: 10, color: '#D1D5DB' },
]
const voiceFeatures = [
  { label: '语速',     value: '正常（142词/分）', status: '正常' },
  { label: '音调变化', value: '波动较小',         status: '偏低' },
  { label: '停顿频率', value: '轻微增加',         status: '注意' },
  { label: '情感基调', value: '平静偏低落',       status: '注意' },
]

// 个性化建议：优先用后端返回的干预建议，降级到本地备选
const fallbackSuggestions = {
  phq9: ['保持规律作息，每天保证7小时以上睡眠', '尝试轻度有氧运动，如散步或瑜伽，每周3次', '每日进行5-10分钟正念冥想，有助于稳定情绪', '与心镜数字陪伴进行日常情绪疏导对话', '若症状持续两周以上，建议寻求专业心理咨询'],
  sds:  ['记录每日情绪日记，觉察情绪变化规律', '增加社交活动，与亲友保持联系', '避免独处时间过长，适当走出舒适圈', '尝试培养新的爱好或参与有意义的活动', '建议与专业心理咨询师进行定期评估'],
  ais:  ['建立固定的睡前仪式，如热水澡、轻音乐', '保持规律的起床时间，即使周末也不要过度补觉', '睡前1小时避免使用手机和电脑蓝光设备', '尝试腹式呼吸或渐进式肌肉放松练习', '如失眠持续影响日间功能，建议就医进行睡眠评估'],
  pss:  ['识别主要压力来源，制定切实可行的应对方案', '学习时间管理技巧，合理分配任务优先级', '每天安排30分钟"放空时间"进行放松', '与信任的人倾诉，分享压力和感受', '考虑正念减压（MBSR）等专业压力管理课程'],
  ai_predict: ['建议寻求专业心理援助，与心理医生进行进一步评估', '保持规律作息，增加有氧运动，有助于改善情绪', '减少独处时间，主动联系亲友保持社会联系', '使用心镜情绪陪伴功能，进行日常情绪疏导对话', '定期进行心理健康自测，关注自身情绪变化趋势'],
}
const backendSuggestions = ref([])
const currentSuggestions = computed(() =>
  backendSuggestions.value.length > 0
    ? backendSuggestions.value
    : (fallbackSuggestions[raw.type] || fallbackSuggestions.phq9)
)

// SOS 安全检查
const isSOS = computed(() => raw.type === 'phq9' && (raw.answers?.[8] ?? 0) > 0)

const reportId   = computed(() => route.params.id || 'local')
const reportDate = computed(() => raw.date || DEMO.date)

// 圆弧计算
const CIRC = 251.3
const arcDash = computed(() => `${(CIRC * raw.total / raw.max).toFixed(1)} ${CIRC}`)

// 导出报告：生成简洁文本内容下载
function exportReport() {
  const lines = [
    '心镜 · 智能评估报告',
    '='.repeat(40),
    `量表：${raw.scale}`,
    `报告日期：${raw.date}`,
    `报告编号：#${reportId.value}`,
    '',
    `总分：${raw.total} / ${raw.max}`,
    `等级：${raw.level}`,
    `描述：${raw.desc}`,
    '',
    '── 分项得分 ──',
    ...(raw.answers || []).map((v, i) => {
      const label = labels[i] || `第${i + 1}题`
      return `${i + 1}. ${label}：${v}分`
    }),
    '',
    '── 个性化建议 ──',
    ...currentSuggestions.value.map((s, i) => `${i + 1}. ${s}`),
    '',
    '免责声明：本报告仅供参考，不构成医学诊断。',
  ]
  const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `心镜评估报告_${raw.scale}_${(raw.date || '').slice(0, 10)}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  const id = route.params.id
  if (id && !isNaN(id) && id !== 'local') {
    try {
      // 拉完整报告（含 session_id）
      const report = await api.get(`/reports/${id}`)
      if (report?.report_json) {
        Object.assign(raw, report.report_json)
      }

      // 再拉该会话的后端干预建议
      try {
        const recs = await api.get(`/reports/session/${report.session_id}/recommendations`)
        if (recs?.length > 0) {
          backendSuggestions.value = recs.map(r => r.content)
        }
      } catch (_) { /* 建议加载失败不阻断页面 */ }
    } catch (e) {
      console.error('拉取报告失败，使用本地数据:', e)
    }
  }
  setTimeout(() => { mounted.value = true }, 300)
})
</script>

<template>
  <div class="min-h-screen bg-sky-bg">
    <div class="max-w-4xl mx-auto px-6 py-10">

      <!-- Header -->
      <div class="flex items-center gap-4 mb-8">
        <button
          class="w-10 h-10 rounded-full bg-white shadow-sm flex items-center justify-center text-gray-600 hover:text-primary transition-colors"
          @click="router.back()"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        <div>
          <h1 class="text-2xl font-bold text-gray-800">智能评估报告</h1>
          <p class="text-gray-400 text-sm">{{ reportDate }} · 报告编号 #{{ reportId }}</p>
        </div>
        <button class="ml-auto flex items-center gap-2 text-sm text-primary border border-primary/30 px-4 py-2 rounded-full hover:bg-primary/5 transition-colors" @click="exportReport">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
          </svg>
          导出报告
        </button>
      </div>

      <!-- SOS 预警条 -->
      <div v-if="isSOS" class="mb-6 bg-red-50 border-2 border-red-200 rounded-2xl p-4 flex items-center gap-4">
        <span class="text-3xl">🆘</span>
        <div class="flex-1">
          <p class="font-bold text-red-700 mb-1">高风险预警 · PHQ-9 第9题得分 &gt; 0</p>
          <p class="text-red-600 text-sm">如有危机想法，请立即拨打 <strong class="font-mono text-base">400-161-9995</strong>（全国心理援助热线）或 <strong class="font-mono">120</strong></p>
        </div>
      </div>

      <!-- 综合风险等级 -->
      <div class="rounded-2xl border-2 p-6 mb-6 flex flex-col sm:flex-row items-center gap-6" :class="levelClass.bg">
        <!-- 仪表圆环 -->
        <div class="relative flex-shrink-0">
          <svg class="w-28 h-28" viewBox="0 0 100 100" style="transform: rotate(-90deg)">
            <circle cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" stroke-width="9"/>
            <circle
              cx="50" cy="50" r="40" fill="none"
              :stroke="raw.color" stroke-width="9" stroke-linecap="round"
              :stroke-dasharray="mounted ? arcDash : `0 ${CIRC}`"
              style="transition: stroke-dasharray 1.2s ease"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="text-3xl font-black text-gray-800">{{ raw.total }}</span>
            <span class="text-xs text-gray-400">/ {{ raw.max }}</span>
          </div>
        </div>

        <div class="flex-1 text-center sm:text-left">
          <div class="flex items-center gap-3 mb-3 justify-center sm:justify-start">
            <span class="text-lg font-bold text-gray-700">{{ raw.scale }} · 综合评估</span>
            <span class="text-lg font-black" :class="levelClass.text">{{ raw.level }}</span>
          </div>

          <!-- 分级进度条 -->
          <div class="flex gap-1 mb-2">
            <div
              v-for="(r, i) in currentRanges" :key="r.label"
              class="flex-1 h-3 rounded-full transition-all"
              :style="{
                backgroundColor: i === activeRangeIndex ? r.color : r.color + '40',
                outline: i === activeRangeIndex ? `2px solid ${r.color}` : 'none',
              }"
            ></div>
          </div>
          <div class="flex justify-between text-xs text-gray-400 mb-3">
            <span v-for="r in currentRanges" :key="r.label">{{ r.label }}</span>
          </div>
          <p class="text-sm text-gray-500 leading-relaxed">{{ raw.desc }}</p>
        </div>
      </div>

      <!-- 量表分项详情（AI 预测无分项答案，隐藏此区块） -->
      <div v-if="raw.type !== 'ai_predict'" class="bg-white rounded-2xl shadow-card p-6 mb-6">
        <h3 class="font-bold text-gray-800 mb-5 flex items-center gap-2">
          <span class="text-primary">📋</span>
          {{ raw.scale }} 分项详情
          <span class="ml-auto text-xs text-gray-400 font-normal">共 {{ scoreItems.length }} 题</span>
        </h3>
        <div class="space-y-3">
          <div v-for="(item, i) in scoreItems" :key="i" class="flex items-center gap-3">
            <span class="text-xs text-gray-400 w-5 text-right flex-shrink-0">{{ i + 1 }}</span>
            <span class="text-sm text-gray-600 w-20 flex-shrink-0 truncate" :title="item.label">{{ item.label }}</span>
            <div class="flex-1 h-2.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                class="h-2.5 rounded-full transition-all duration-700"
                :class="item.score === 0 ? 'bg-green-300' : item.score === 1 ? 'bg-yellow-400' : item.score <= 2 ? 'bg-orange-400' : 'bg-red-400'"
                :style="{ width: mounted ? (item.score / (raw.type === 'sds' ? 4 : raw.type === 'ais' || raw.type === 'pss' ? 4 : 3) * 100) + '%' : '0%' }"
              ></div>
            </div>
            <span class="text-sm font-bold text-gray-700 w-4 flex-shrink-0">{{ item.score }}</span>
            <span
              class="text-xs px-2 py-0.5 rounded-full w-14 text-center flex-shrink-0 font-medium"
              :class="item.score === 0 ? 'bg-green-50 text-green-600' : item.score === 1 ? 'bg-yellow-50 text-yellow-600' : item.score <= 2 ? 'bg-orange-50 text-orange-600' : 'bg-red-50 text-red-600'"
            >
              {{ ['无', '偶有', '经常', '频繁', '持续'][Math.min(item.score, 4)] }}
            </span>
          </div>
        </div>
      </div>

      <!-- 多模态分析 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- 面部表情 -->
        <div class="bg-white rounded-2xl shadow-card p-6">
          <h3 class="font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span>📸</span> 面部表情分析
          </h3>
          <div class="flex items-center gap-4 mb-4">
            <div class="relative w-20 h-20 flex-shrink-0">
              <svg viewBox="0 0 36 36" class="w-20 h-20 -rotate-90">
                <circle cx="18" cy="18" r="15.9" fill="none" stroke="#f3f4f6" stroke-width="3.8"/>
                <circle cx="18" cy="18" r="15.9" fill="none" stroke="#3B9EE8" stroke-width="3.8"
                        stroke-dasharray="45 55" stroke-linecap="round"/>
                <circle cx="18" cy="18" r="15.9" fill="none" stroke="#FBBF24" stroke-width="3.8"
                        stroke-dasharray="25 75" stroke-dashoffset="-45" stroke-linecap="round"/>
                <circle cx="18" cy="18" r="15.9" fill="none" stroke="#A78BFA" stroke-width="3.8"
                        stroke-dasharray="20 80" stroke-dashoffset="-70" stroke-linecap="round"/>
              </svg>
              <div class="absolute inset-0 flex items-center justify-center text-lg">😐</div>
            </div>
            <div class="space-y-2 flex-1">
              <div v-for="em in faceEmotions" :key="em.label" class="flex items-center gap-2">
                <span class="w-3 h-3 rounded-full flex-shrink-0" :style="{ backgroundColor: em.color }"></span>
                <span class="text-sm text-gray-600">{{ em.label }}</span>
                <span class="text-sm font-semibold text-gray-800 ml-auto">{{ em.value }}%</span>
              </div>
            </div>
          </div>
          <p class="text-xs text-gray-400 bg-gray-50 rounded-xl p-3 leading-relaxed">
            面部情绪分析显示主要为平静状态，存在轻微焦虑迹象，与量表结果基本吻合。
          </p>
        </div>

        <!-- 语音分析 -->
        <div class="bg-white rounded-2xl shadow-card p-6">
          <h3 class="font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span>🎤</span> 语音情感分析
          </h3>
          <div class="space-y-3">
            <div v-for="vf in voiceFeatures" :key="vf.label"
                 class="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <div>
                <div class="text-sm font-medium text-gray-700">{{ vf.label }}</div>
                <div class="text-xs text-gray-400 mt-0.5">{{ vf.value }}</div>
              </div>
              <span
                class="text-xs px-2 py-1 rounded-full font-medium"
                :class="vf.status === '正常' ? 'bg-green-100 text-green-600' : vf.status === '注意' ? 'bg-yellow-100 text-yellow-600' : 'bg-orange-100 text-orange-600'"
              >{{ vf.status }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 个性化建议 -->
      <div class="bg-white rounded-2xl shadow-card p-6 mb-6">
        <h3 class="font-bold text-gray-800 mb-4 flex items-center gap-2">
          <span class="text-teal-brand">💡</span> 个性化建议
          <span class="ml-2 text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">基于 {{ raw.scale }} 结果</span>
        </h3>
        <ul class="space-y-3">
          <li v-for="(s, i) in currentSuggestions" :key="i" class="flex items-start gap-3">
            <span class="w-6 h-6 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center font-bold flex-shrink-0 mt-0.5">{{ i + 1 }}</span>
            <span class="text-gray-600 text-sm leading-relaxed">{{ s }}</span>
          </li>
        </ul>
      </div>

      <!-- CTA -->
      <div class="flex flex-col sm:flex-row gap-4">
        <RouterLink to="/companion" class="btn-primary flex-1 text-center no-underline">与心镜对话，获取情绪支持</RouterLink>
        <RouterLink to="/analytics" class="btn-outline flex-1 text-center no-underline">查看历史趋势</RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.no-underline { text-decoration: none; }
</style>
