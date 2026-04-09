<script setup>
import { ref, reactive, computed, onUnmounted, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import { api } from '../services/api.js'

const router = useRouter()
const route = useRoute()
const { userId } = useAuth()

// 从 URL 参数获取预设的量表类型
onMounted(() => {
  const typeFromQuery = route.query.type
  if (typeFromQuery && banks[typeFromQuery]) {
    selectedType.value = typeFromQuery
    // 自动选择对应的评估
    const assessment = assessments.find(a => a.id === typeFromQuery)
    if (assessment) {
      selectAssessment(assessment)
    }
  }
})

// phase: intro | setup | recording | questionnaire | sos | done
const phase = ref('intro')
const currentQ = ref(0)
const answers = ref([])
const cameraActive = ref(false)
const micActive = ref(false)
const recordingTime = ref(0)
let timer = null

const sosTriggered = ref(false)
const scoreResult = ref(null)
const pendingReportId = ref(null)
const showError = ref(false)
const errorMessage = ref('')

// ─── AI 预测表单 ─────────────────────────────────────────────────────────────
const aiForm = reactive({
  age: 25,
  work_pressure: 5,
  job_satisfaction: 5,
  sleep_duration: 7,
  work_or_study_hours: 8,
  financial_stress: 3,
  gender: 'Male',
  working_status: 'Student',
  suicidal_thoughts: 'No',
  dietary_habits: 'Moderate',
  family_history: 'No',
})
const aiLoading = ref(false)

// ─── 量表选项 ──────────────────────────────────────────────────────────────
const assessments = [
  {
    id: 'phq9', title: 'PHQ-9 抑郁初筛', desc: '9道题 · 约3分钟',
    icon: '📋', color: 'from-blue-50 to-sky-50', badge: '临床标准',
    note: '基于 DSM-IV 诊断标准，国际通用快速筛查量表',
  },
  {
    id: 'sds', title: 'SDS 抑郁自评', desc: '20道题 · 约8分钟',
    icon: '🩺', color: 'from-orange-50 to-amber-50', badge: '综合全面',
    note: '含躯体化症状评估，国内临床常用，设有反向计分题',
  },
  {
    id: 'ais', title: 'AIS 睡眠评估', desc: '8道题 · 约3分钟',
    icon: '😴', color: 'from-purple-50 to-indigo-50', badge: '',
    note: '阿森斯失眠量表，评估近1个月的睡眠状况',
  },
  {
    id: 'pss', title: 'PSS 压力感知', desc: '10道题 · 约4分钟',
    icon: '🧠', color: 'from-green-50 to-emerald-50', badge: '',
    note: '压力知觉量表，评估主观感受到的压力水平',
  },
  {
    id: 'ai_predict', title: 'AI 深度学习预测', desc: '填写信息 · 即时结果',
    icon: '🤖', color: 'from-violet-50 to-fuchsia-50', badge: 'AI模型',
    note: '基于深度学习模型，结合生活与工作因素智能预测抑郁风险',
  },
]

// ─── 题库 ──────────────────────────────────────────────────────────────────
const banks = {
  phq9: {
    scale: 'PHQ-9',
    context: '在过去两周，您有多频繁地受到以下问题困扰？',
    questions: [
      '做事时提不起劲儿或没有兴趣',
      '感到心情低落、沮丧或绝望',
      '入睡困难、睡不安稳或睡眠过多',
      '感觉疲倦或没有活力',
      '食欲不振或吃得太多',
      '觉得自己很糟、很失败，或让自己及家人失望',
      '对事物专注有困难，例如阅读报纸或看电视时',
      '动作或说话速度缓慢到别人已经察觉？或刚好相反，烦躁或坐立不安',
      '有不如死掉或用某种方式伤害自己的念头',
    ],
    options: [
      { label: '完全没有', value: 0, sub: '0天' },
      { label: '有几天', value: 1, sub: '1–6天' },
      { label: '超过一半时间', value: 2, sub: '7–11天' },
      { label: '几乎天天', value: 3, sub: '12–14天' },
    ],
    reverseIndices: new Set(),
  },
  sds: {
    scale: 'SDS',
    context: '请根据您最近一周的实际感受选择，没有对错之分。',
    questions: [
      '我觉得情绪低落，郁闷',
      '我觉得一天中早晨心情最差',
      '我一阵阵哭出来或觉得想哭',
      '我晚上睡眠不好',
      '我吃得跟平常一样多',            // 反向 5
      '我与异性密切接触时和以往一样感到愉快', // 反向 6
      '我发现我的体重在下降',
      '我有便秘的苦恼',
      '我心跳比平时快',
      '我无缘无故地感到疲乏',
      '我的头脑跟平常一样清楚',         // 反向 11
      '我觉得做事情很容易',             // 反向 12
      '我坐卧不安，难以保持平静',
      '我对未来抱有希望',               // 反向 14
      '我比平时更容易激怒',
      '我觉得决定什么事很容易',         // 反向 16
      '我觉得自己是个有用的人，有人需要我', // 反向 17
      '我的生活过得很有意义',           // 反向 18
      '我认为如果我死了别人会生活得更好',
      '平常感兴趣的事我仍然照样感兴趣',  // 反向 20
    ],
    options: [
      { label: '偶尔或没有', value: 1, sub: '< 1天/周' },
      { label: '有时',       value: 2, sub: '1–2天/周' },
      { label: '经常',       value: 3, sub: '3–4天/周' },
      { label: '持续',       value: 4, sub: '5–7天/周' },
    ],
    // 0-indexed，对应题目 5,6,11,12,14,16,17,18,20
    reverseIndices: new Set([4, 5, 10, 11, 13, 15, 16, 17, 19]),
  },
  ais: {
    scale: 'AIS',
    context: '根据您近一个月内每周至少3次发生的睡眠情况来评估。',
    questions: [
      '入睡时间（关灯后多久才能睡着）',
      '夜间苏醒（夜里醒来次数多，难以再入睡）',
      '比期望的时间早醒',
      '总睡眠时间（比平时明显减少）',
      '总睡眠质量（无论睡多久，都觉得质量差）',
      '白天情绪（睡眠不好影响情绪状态）',
      '白天身体功能（精力、体力、注意力受影响）',
      '白天嗜睡（白天犯困、难以集中注意力）',
    ],
    options: [
      { label: '无问题', value: 0 },
      { label: '轻度',   value: 1 },
      { label: '中度',   value: 2 },
      { label: '重度',   value: 3 },
      { label: '极重度', value: 4 },
    ],
    reverseIndices: new Set(),
  },
  pss: {
    scale: 'PSS',
    context: '在过去一个月中，您有多频繁地有以下感受或想法？',
    questions: [
      '感到无法控制生活中重要的事情',
      '感到无法处理堆积的所有事情',
      '感到紧张不安或有压力',
      '成功地处理了生活中的麻烦',          // 反向 4
      '感到事情正按自己的意愿发展',         // 反向 5
      '发现无法应对所有必须做的事情',
      '能够控制生活中的烦恼',              // 反向 7
      '感到自己能掌控生活中的所有问题',     // 反向 8
      '因为事情超出控制而生气',
      '感到困难堆积如山，无法克服',
    ],
    options: [
      { label: '从未', value: 0 },
      { label: '偶尔', value: 1 },
      { label: '有时', value: 2 },
      { label: '经常', value: 3 },
      { label: '总是', value: 4 },
    ],
    reverseIndices: new Set([3, 4, 6, 7]),
  },
}

const selectedType = ref(null)
const selectedAssessment = ref(null)

const currentBank = computed(() => banks[selectedType.value] || banks.phq9)
const currentQuestions = computed(() => currentBank.value.questions)
const currentOptions = computed(() => currentBank.value.options)
const isReverseQ = computed(() => currentBank.value.reverseIndices.has(currentQ.value))

// 步骤条索引
const phaseStepIndex = computed(() => (
  { intro: 0, setup: 1, recording: 2, questionnaire: 3, ai_form: 3, sos: 3, done: 4 }[phase.value] ?? 0
))

// 分数进度（用于仪表盘 SVG）
const scorePercent = computed(() =>
  scoreResult.value ? scoreResult.value.total / scoreResult.value.max : 0
)
// SVG 圆弧：r=40, circumference = 2π*40 ≈ 251.3
const CIRC = 251.3
const scoreArc = computed(() => `${(CIRC * scorePercent.value).toFixed(1)} ${CIRC}`)

// ─── 流程控制 ───────────────────────────────────────────────────────────────
function selectAssessment(a) {
  selectedType.value = a.id
  selectedAssessment.value = a
}

function startSetup() {
  if (selectedType.value === 'ai_predict') {
    phase.value = 'ai_form'
  } else {
    phase.value = 'setup'
  }
}

async function submitAiForm() {
  aiLoading.value = true
  try {
    const res = await api.post('/depression-predict', { ...aiForm })
    scoreResult.value = {
      total: Math.round(res.probability * 100),
      max: 100,
      level: res.prediction,
      color: res.depressed ? '#e74c3c' : '#27ae60',
      desc: res.motivation,
      scale: 'AI抑郁预测',
      depressed: res.depressed,
    }
    pendingReportId.value = res.report_id || null
    const localRecord = {
      type: 'ai_predict',
      ...scoreResult.value,
      date: new Date().toLocaleString('zh-CN'),
    }
    try { localStorage.setItem('xj_screening_result', JSON.stringify(localRecord)) } catch (_) {}
    phase.value = 'done'
  } catch (e) {
    console.error('AI预测失败:', e)
    errorMessage.value = '预测请求失败，请检查网络或登录状态后重试'
    showError.value = true
    setTimeout(() => { showError.value = false }, 3000)
  } finally {
    aiLoading.value = false
  }
}

function startRecording() {
  phase.value = 'recording'
  recordingTime.value = 0
  timer = setInterval(() => {
    recordingTime.value++
    if (recordingTime.value >= 30) stopRecording()
  }, 1000)
}

function stopRecording() {
  clearInterval(timer)
  startQuestionnaire()
}

function skipToQuestionnaire() { startQuestionnaire() }

function startQuestionnaire() {
  answers.value = []
  currentQ.value = 0
  phase.value = 'questionnaire'
}

function selectAnswer(val) {
  answers.value[currentQ.value] = val
  const isLast = currentQ.value >= currentQuestions.value.length - 1
  if (!isLast) {
    currentQ.value++
  } else {
    finishQuestionnaire()
  }
}

async function finishQuestionnaire() {
  // 确保所有题目均已作答
  const totalQ = currentQuestions.value.length
  for (let i = 0; i < totalQ; i++) {
    if (answers.value[i] === undefined || answers.value[i] === null) {
      currentQ.value = i
      return // 跳回未作答题目
    }
  }

  const result = calcScore()
  scoreResult.value = result

  const isSOS = selectedType.value === 'phq9' && (answers.value[8] ?? 0) > 0
  if (isSOS) {
    sosTriggered.value = true
    phase.value = 'sos'
  } else {
    phase.value = 'done'
  }

  // 保存到 localStorage（本地备份）
  const localRecord = {
    type: selectedType.value,
    ...result,
    answers: answers.value,
    date: new Date().toLocaleString('zh-CN'),
  }
  try { localStorage.setItem('xj_screening_result', JSON.stringify(localRecord)) } catch (_) {}

  // 提交到后端
  if (userId.value) {
    try {
      const allModalities = ['face', 'voice', 'text']
      const usedModalities = [
        ...(cameraActive.value ? ['face'] : []),
        ...(micActive.value   ? ['voice'] : []),
        'text',
      ]
      const missingModalities = allModalities.filter(m => !usedModalities.includes(m))
      const session = await api.post('/evaluations/sessions', {
        screening_type: selectedType.value,
        used_modalities: usedModalities,
        missing_modalities: missingModalities,
      })
      const answerPayload = answers.value.map((v, i) => ({
        question_no: i + 1,
        answer_value: v ?? 0,
      }))
      const submitted = await api.post(`/evaluations/sessions/${session.session_id}/submit`, {
        template_code: selectedType.value,
        answers: answerPayload,
      })
      pendingReportId.value = submitted.report_id
      // 更新本地记录加上真实 report_id
      try {
        localStorage.setItem('xj_screening_result', JSON.stringify({
          ...localRecord,
          report_id: submitted.report_id,
        }))
      } catch (_) {}
    } catch (e) {
      console.error('提交后端失败，使用本地数据:', e)
    }
  }
}

// ─── 评分计算 ───────────────────────────────────────────────────────────────
function calcScore() {
  const bank = banks[selectedType.value] || banks.phq9

  if (selectedType.value === 'sds') {
    let raw = 0
    answers.value.forEach((v, i) => {
      const val = v ?? 1
      raw += bank.reverseIndices.has(i) ? (5 - val) : val
    })
    const total = Math.floor(raw * 1.25)
    if (total < 53)      return { total, max: 100, level: '正常',   color: '#22c55e', desc: '无明显抑郁症状，情绪状态良好，请继续保持健康的生活方式。', scale: 'SDS' }
    if (total <= 62)     return { total, max: 100, level: '轻度抑郁', color: '#eab308', desc: '存在轻度抑郁倾向，建议关注情绪变化，适当调节压力与作息。', scale: 'SDS' }
    if (total <= 72)     return { total, max: 100, level: '中度抑郁', color: '#f97316', desc: '存在中度抑郁症状，建议寻求专业心理咨询和支持。', scale: 'SDS' }
    return               { total, max: 100, level: '重度抑郁', color: '#dc2626', desc: '存在重度抑郁症状，请尽快寻求专业心理医生的帮助。', scale: 'SDS' }
  }

  if (selectedType.value === 'pss') {
    let total = 0
    answers.value.forEach((v, i) => {
      const val = v ?? 0
      total += bank.reverseIndices.has(i) ? (4 - val) : val
    })
    if (total <= 13)  return { total, max: 40, level: '低压力水平',   color: '#22c55e', desc: '压力处于可控范围内，您的应对能力良好。', scale: 'PSS' }
    if (total <= 26)  return { total, max: 40, level: '中等压力水平', color: '#eab308', desc: '存在一定压力，建议采用有效的压力管理和放松策略。', scale: 'PSS' }
    return            { total, max: 40, level: '高压力水平',   color: '#dc2626', desc: '压力水平较高，持续高压可能影响身心健康，建议积极寻求支持。', scale: 'PSS' }
  }

  const total = answers.value.reduce((s, v) => s + (v ?? 0), 0)

  if (selectedType.value === 'ais') {
    if (total <= 4)   return { total, max: 32, level: '无睡眠障碍', color: '#22c55e', desc: '睡眠质量良好，无明显障碍。', scale: 'AIS' }
    if (total <= 10)  return { total, max: 32, level: '可疑失眠',   color: '#eab308', desc: '存在可疑失眠症状，建议关注和改善睡眠卫生习惯。', scale: 'AIS' }
    if (total <= 14)  return { total, max: 32, level: '轻度失眠',   color: '#f97316', desc: '轻度失眠，建议建立规律的作息时间和睡前放松习惯。', scale: 'AIS' }
    if (total <= 20)  return { total, max: 32, level: '中度失眠',   color: '#ef4444', desc: '中度失眠，建议寻求专业睡眠咨询或认知行为治疗。', scale: 'AIS' }
    return            { total, max: 32, level: '重度失眠',   color: '#dc2626', desc: '重度失眠，建议尽快就医，排查潜在原因。', scale: 'AIS' }
  }

  // PHQ-9
  if (total <= 4)   return { total, max: 27, level: '无抑郁症状', color: '#22c55e', desc: '您目前状态良好，请继续保持健康的生活方式。', scale: 'PHQ-9' }
  if (total <= 9)   return { total, max: 27, level: '轻度抑郁',   color: '#eab308', desc: '存在轻度抑郁倾向，建议关注情绪状态，适当自我调适。', scale: 'PHQ-9' }
  if (total <= 14)  return { total, max: 27, level: '中度抑郁',   color: '#f97316', desc: '存在中度抑郁症状，建议寻求专业心理咨询。', scale: 'PHQ-9' }
  if (total <= 19)  return { total, max: 27, level: '中重度抑郁', color: '#ef4444', desc: '存在较重抑郁症状，强烈建议尽快寻求专业帮助。', scale: 'PHQ-9' }
  return            { total, max: 27, level: '重度抑郁',   color: '#dc2626', desc: '存在严重抑郁症状，请立即寻求专业心理医生帮助。', scale: 'PHQ-9' }
}

function goToReport() {
  router.push(pendingReportId.value ? `/report/${pendingReportId.value}` : '/report/local')
}

onUnmounted(() => clearInterval(timer))
const fmt = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`

// 分级参考范围配置
const scaleRanges = {
  phq9: [
    { range: '0–4',   label: '无症状', color: '#22c55e' },
    { range: '5–9',   label: '轻度',   color: '#eab308' },
    { range: '10–14', label: '中度',   color: '#f97316' },
    { range: '15–19', label: '中重度', color: '#ef4444' },
    { range: '20–27', label: '重度',   color: '#dc2626' },
  ],
  sds: [
    { range: '< 53',  label: '正常',   color: '#22c55e' },
    { range: '53–62', label: '轻度',   color: '#eab308' },
    { range: '63–72', label: '中度',   color: '#f97316' },
    { range: '> 72',  label: '重度',   color: '#dc2626' },
  ],
  ais: [
    { range: '0–4',   label: '无障碍', color: '#22c55e' },
    { range: '5–10',  label: '可疑',   color: '#eab308' },
    { range: '11–14', label: '轻度',   color: '#f97316' },
    { range: '15–20', label: '中度',   color: '#ef4444' },
    { range: '21–32', label: '重度',   color: '#dc2626' },
  ],
  pss: [
    { range: '0–13',  label: '低压力', color: '#22c55e' },
    { range: '14–26', label: '中压力', color: '#eab308' },
    { range: '27–40', label: '高压力', color: '#dc2626' },
  ],
  ai_predict: [
    { range: '0–64',  label: '暂无抑郁倾向', color: '#27ae60' },
    { range: '65–100', label: '可能存在抑郁', color: '#e74c3c' },
  ],
}
</script>

<template>
  <div class="min-h-screen bg-hero-gradient">
    <div class="max-w-5xl mx-auto px-6 py-12">

      <!-- Error Toast -->
      <transition name="fade">
        <div v-if="showError" class="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg">
          {{ errorMessage }}
        </div>
      </transition>

      <!-- Header -->
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">辅助筛查</h1>
        <p class="text-gray-500">通过多模态数据采集与心理量表，进行全面的心理状态评估</p>
      </div>

      <!-- Progress Steps -->
      <div class="flex items-center justify-center gap-2 mb-10">
        <template v-for="(s, i) in ['选择量表', '设备准备', '数据采集', '量表填写', '查看报告']" :key="i">
          <div class="flex items-center gap-2">
            <div
              class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all"
              :class="phaseStepIndex >= i ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500'"
            >{{ i + 1 }}</div>
            <span
              class="text-sm hidden sm:block"
              :class="phaseStepIndex >= i ? 'text-primary font-medium' : 'text-gray-400'"
            >{{ s }}</span>
          </div>
          <div v-if="i < 4" class="flex-1 h-px max-w-12 bg-gray-200"></div>
        </template>
      </div>

      <!-- ─── Phase: intro ─────────────────────────────────────── -->
      <div v-if="phase === 'intro'" class="space-y-8">
        <!-- 量表选择卡片 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div
            v-for="a in assessments" :key="a.id"
            class="relative bg-gradient-to-br rounded-2xl p-6 cursor-pointer border-2 transition-all duration-200 hover:shadow-card-hover hover:-translate-y-0.5"
            :class="[a.color, selectedType === a.id ? 'border-primary shadow-card' : 'border-transparent']"
            @click="selectAssessment(a)"
          >
            <span v-if="a.badge" class="absolute top-4 right-4 text-xs bg-primary text-white px-2 py-0.5 rounded-full">{{ a.badge }}</span>
            <div class="text-3xl mb-3">{{ a.icon }}</div>
            <h3 class="font-bold text-gray-800 mb-1">{{ a.title }}</h3>
            <p class="text-gray-500 text-sm mb-1">{{ a.desc }}</p>
            <p class="text-gray-400 text-xs leading-relaxed mb-3">{{ a.note }}</p>
            <div v-if="selectedType === a.id" class="flex items-center gap-1 text-primary text-sm font-medium">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              已选择
            </div>
          </div>
        </div>

        <!-- 多模态说明 -->
        <div class="bg-white rounded-2xl p-6 shadow-card border border-primary/10">
          <h3 class="font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span class="text-primary">🔍</span> 多模态采集说明
          </h3>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="flex items-start gap-3 p-3 bg-blue-50 rounded-xl">
              <span class="text-2xl">📸</span>
              <div>
                <div class="font-semibold text-sm text-gray-700">面部表情采集</div>
                <div class="text-xs text-gray-500 mt-0.5">实时分析7种基本情绪及 AU 面部动作编码</div>
              </div>
            </div>
            <div class="flex items-start gap-3 p-3 bg-orange-50 rounded-xl">
              <span class="text-2xl">🎤</span>
              <div>
                <div class="font-semibold text-sm text-gray-700">语音情感分析</div>
                <div class="text-xs text-gray-500 mt-0.5">提取语速、音调、韵律等声学特征</div>
              </div>
            </div>
            <div class="flex items-start gap-3 p-3 bg-green-50 rounded-xl">
              <span class="text-2xl">📋</span>
              <div>
                <div class="font-semibold text-sm text-gray-700">量表综合评分</div>
                <div class="text-xs text-gray-500 mt-0.5">标准化量表主观评估，结合生物信号分析</div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-center">
          <button
            class="btn-primary text-lg px-12"
            :disabled="!selectedType"
            :class="!selectedType ? 'opacity-50 cursor-not-allowed' : ''"
            @click="startSetup"
          >
            {{ selectedType === 'ai_predict' ? '下一步：填写信息' : '下一步：设备准备' }}
          </button>
        </div>
      </div>

      <!-- ─── Phase: setup ─────────────────────────────────────── -->
      <div v-else-if="phase === 'setup'" class="max-w-2xl mx-auto">
        <div class="bg-white rounded-3xl shadow-card p-8">
          <h2 class="text-xl font-bold text-gray-800 mb-1 text-center">设备权限与准备</h2>
          <p class="text-center text-gray-400 text-sm mb-7">开启设备权限采集多模态生物信号（可选）</p>

          <div class="space-y-4 mb-8">
            <div
              class="flex items-center justify-between p-4 rounded-2xl border-2 transition-all"
              :class="cameraActive ? 'border-green-300 bg-green-50' : 'border-gray-200 bg-gray-50'"
            >
              <div class="flex items-center gap-3">
                <span class="text-2xl">📸</span>
                <div>
                  <div class="font-semibold text-gray-800">摄像头权限</div>
                  <div class="text-sm text-gray-500">面部表情分析 · 检测7种基础情绪</div>
                </div>
              </div>
              <button
                class="px-4 py-2 rounded-full text-sm font-medium transition-all"
                :class="cameraActive ? 'bg-green-500 text-white' : 'bg-primary text-white'"
                @click="cameraActive = !cameraActive"
              >{{ cameraActive ? '✓ 已开启' : '开启' }}</button>
            </div>

            <div
              class="flex items-center justify-between p-4 rounded-2xl border-2 transition-all"
              :class="micActive ? 'border-green-300 bg-green-50' : 'border-gray-200 bg-gray-50'"
            >
              <div class="flex items-center gap-3">
                <span class="text-2xl">🎤</span>
                <div>
                  <div class="font-semibold text-gray-800">麦克风权限</div>
                  <div class="text-sm text-gray-500">语音情感分析 · 提取声学特征</div>
                </div>
              </div>
              <button
                class="px-4 py-2 rounded-full text-sm font-medium transition-all"
                :class="micActive ? 'bg-green-500 text-white' : 'bg-primary text-white'"
                @click="micActive = !micActive"
              >{{ micActive ? '✓ 已开启' : '开启' }}</button>
            </div>
          </div>

          <div class="bg-amber-50 rounded-2xl p-4 mb-8">
            <div class="flex items-start gap-2">
              <span class="text-amber-500 mt-0.5">💡</span>
              <div class="text-sm text-amber-700 space-y-1">
                <p>请确保处于安静、光线充足的环境中</p>
                <p>摄像头正对面部，距离约 50–80cm</p>
                <p>采集过程约需 30 秒，请保持自然状态并说几句话</p>
              </div>
            </div>
          </div>

          <div class="flex gap-4">
            <button class="btn-outline flex-1" @click="phase = 'intro'">返回</button>
            <button
              class="btn-primary flex-1"
              :disabled="!cameraActive || !micActive"
              :class="(!cameraActive || !micActive) ? 'opacity-50 cursor-not-allowed' : ''"
              @click="startRecording"
            >开始采集</button>
          </div>
          <button
            class="w-full mt-4 text-sm text-gray-400 hover:text-gray-600 transition-colors underline underline-offset-2"
            @click="skipToQuestionnaire"
          >跳过设备采集，直接填写量表</button>
        </div>
      </div>

      <!-- ─── Phase: recording ─────────────────────────────────── -->
      <div v-else-if="phase === 'recording'" class="max-w-2xl mx-auto">
        <div class="bg-white rounded-3xl shadow-card p-8 text-center">
          <div class="relative inline-block mb-6">
            <div class="w-48 h-36 bg-gray-900 rounded-2xl mx-auto flex items-center justify-center relative overflow-hidden">
              <div class="text-gray-600 text-4xl">👤</div>
              <div class="absolute top-3 right-3 flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                <span class="text-red-400 text-xs font-mono">REC</span>
              </div>
              <div class="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent animate-pulse"></div>
            </div>
            <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div class="w-48 h-36 rounded-2xl border-2 border-primary/30 animate-ping"></div>
            </div>
          </div>

          <div class="text-3xl font-mono font-bold text-primary mb-2">{{ fmt(recordingTime) }}</div>
          <p class="text-gray-500 mb-1">正在采集面部与语音数据...</p>
          <p class="text-gray-400 text-sm mb-8">请保持自然状态，说几句话来帮助系统分析</p>

          <!-- 音频波形（平滑正弦动画） -->
          <div class="flex items-center justify-center gap-1 h-10 mb-8">
            <div
              v-for="i in 22" :key="i"
              class="w-1.5 rounded-full bg-primary transition-all"
              :style="{ height: (Math.abs(Math.sin((i * 0.7) + recordingTime * 0.5)) * 70 + 15) + '%' }"
            ></div>
          </div>

          <div class="flex flex-wrap justify-center gap-2 mb-8">
            <span class="text-xs bg-blue-100 text-primary px-3 py-1 rounded-full animate-pulse">😊 情绪检测中</span>
            <span class="text-xs bg-green-100 text-green-600 px-3 py-1 rounded-full animate-pulse">🔊 语音分析中</span>
            <span class="text-xs bg-purple-100 text-purple-600 px-3 py-1 rounded-full animate-pulse">📊 特征提取中</span>
          </div>

          <button class="btn-primary" @click="stopRecording">采集完成，进入量表</button>
        </div>
      </div>

      <!-- ─── Phase: questionnaire ──────────────────────────────── -->
      <div v-else-if="phase === 'questionnaire'" class="max-w-2xl mx-auto">
        <div class="bg-white rounded-3xl shadow-card p-8">
          <!-- 进度头部 -->
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-500 font-medium">{{ currentQ + 1 }} / {{ currentQuestions.length }}</span>
            <div class="flex items-center gap-2">
              <span
                v-if="isReverseQ"
                class="text-xs bg-amber-100 text-amber-600 px-2 py-0.5 rounded-full font-medium"
              >反向计分</span>
              <span class="text-xs bg-primary text-white px-2.5 py-0.5 rounded-full font-bold">
                {{ currentBank.scale }}
              </span>
            </div>
          </div>

          <!-- 进度条 -->
          <div class="h-2 bg-gray-100 rounded-full mb-6 overflow-hidden">
            <div
              class="h-2 bg-blue-green rounded-full transition-all duration-500"
              :style="{ width: (currentQ / currentQuestions.length * 100) + '%' }"
            ></div>
          </div>

          <!-- 量表背景提示 -->
          <div class="text-xs text-gray-400 font-medium mb-2 tracking-wide">{{ currentBank.context }}</div>

          <!-- 题目 -->
          <h3 class="text-lg font-bold text-gray-800 mb-8 leading-relaxed min-h-[4rem]">
            {{ currentQ + 1 }}. {{ currentQuestions[currentQ] }}
          </h3>

          <!-- 选项 -->
          <div class="space-y-3">
            <button
              v-for="opt in currentOptions" :key="opt.value"
              class="w-full text-left p-4 rounded-2xl border-2 transition-all duration-200 font-medium"
              :class="answers[currentQ] === opt.value
                ? 'border-primary bg-blue-50 text-primary'
                : 'border-gray-100 text-gray-700 hover:border-primary hover:bg-blue-50 hover:text-primary'"
              @click="selectAnswer(opt.value)"
            >
              <div class="flex items-center gap-3">
                <div
                  class="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all"
                  :class="answers[currentQ] === opt.value ? 'border-primary bg-primary' : 'border-gray-300'"
                >
                  <div v-if="answers[currentQ] === opt.value" class="w-2 h-2 rounded-full bg-white"></div>
                </div>
                <span class="flex-1">{{ opt.label }}</span>
                <span v-if="opt.sub" class="text-xs text-gray-400 ml-auto">{{ opt.sub }}</span>
              </div>
            </button>
          </div>

          <!-- 返回上一题 -->
          <div class="mt-8">
            <button
              v-if="currentQ > 0"
              class="btn-outline text-sm px-5 py-2"
              @click="currentQ--"
            >← 上一题</button>
          </div>
        </div>
      </div>

      <!-- ─── Phase: ai_form ───────────────────────────────────── -->
      <div v-else-if="phase === 'ai_form'" class="max-w-2xl mx-auto">
        <div class="bg-white rounded-3xl shadow-card p-8">
          <div class="flex items-center gap-3 mb-6">
            <span class="text-3xl">🤖</span>
            <div>
              <h2 class="text-xl font-bold text-gray-800">AI 深度学习抑郁预测</h2>
              <p class="text-gray-400 text-sm">基于 Keras 深度学习模型，结合生活与工作因素进行风险评估</p>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-6">
            <!-- 年龄 -->
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">年龄</label>
              <div class="flex items-center border border-gray-200 rounded-xl overflow-hidden">
                <button class="px-3 py-2 bg-gray-50 text-gray-600 hover:bg-gray-100 text-lg" @click="aiForm.age = Math.max(15, aiForm.age - 1)">−</button>
                <input v-model.number="aiForm.age" type="number" min="15" max="80" class="flex-1 text-center py-2 text-gray-800 font-medium outline-none"/>
                <button class="px-3 py-2 bg-gray-50 text-gray-600 hover:bg-gray-100 text-lg" @click="aiForm.age = Math.min(80, aiForm.age + 1)">+</button>
              </div>
            </div>
            <!-- 工作/学习时长 -->
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">每日工作/学习时长（小时）</label>
              <div class="flex items-center border border-gray-200 rounded-xl overflow-hidden">
                <button class="px-3 py-2 bg-gray-50 text-gray-600 hover:bg-gray-100 text-lg" @click="aiForm.work_or_study_hours = Math.max(0, aiForm.work_or_study_hours - 1)">−</button>
                <input v-model.number="aiForm.work_or_study_hours" type="number" min="0" max="24" class="flex-1 text-center py-2 text-gray-800 font-medium outline-none"/>
                <button class="px-3 py-2 bg-gray-50 text-gray-600 hover:bg-gray-100 text-lg" @click="aiForm.work_or_study_hours = Math.min(24, aiForm.work_or_study_hours + 1)">+</button>
              </div>
            </div>
            <!-- 工作压力 -->
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">工作/学业压力（1–10）</label>
              <div class="flex items-center border border-gray-200 rounded-xl overflow-hidden">
                <button class="px-3 py-2 bg-gray-50 text-gray-600 hover:bg-gray-100 text-lg" @click="aiForm.work_pressure = Math.max(1, aiForm.work_pressure - 1)">−</button>
                <input v-model.number="aiForm.work_pressure" type="number" min="1" max="10" class="flex-1 text-center py-2 text-gray-800 font-medium outline-none"/>
                <button class="px-3 py-2 bg-gray-50 text-gray-600 hover:bg-gray-100 text-lg" @click="aiForm.work_pressure = Math.min(10, aiForm.work_pressure + 1)">+</button>
              </div>
            </div>
            <!-- 经济压力 -->
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">经济压力（1–10）</label>
              <div class="flex items-center border border-gray-200 rounded-xl overflow-hidden">
                <button class="px-3 py-2 bg-gray-50 text-gray-600 hover:bg-gray-100 text-lg" @click="aiForm.financial_stress = Math.max(1, aiForm.financial_stress - 1)">−</button>
                <input v-model.number="aiForm.financial_stress" type="number" min="1" max="10" class="flex-1 text-center py-2 text-gray-800 font-medium outline-none"/>
                <button class="px-3 py-2 bg-gray-50 text-gray-600 hover:bg-gray-100 text-lg" @click="aiForm.financial_stress = Math.min(10, aiForm.financial_stress + 1)">+</button>
              </div>
            </div>
            <!-- 工作满意度 -->
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">工作/学业满意度（1–10）</label>
              <div class="flex items-center border border-gray-200 rounded-xl overflow-hidden">
                <button class="px-3 py-2 bg-gray-50 text-gray-600 hover:bg-gray-100 text-lg" @click="aiForm.job_satisfaction = Math.max(1, aiForm.job_satisfaction - 1)">−</button>
                <input v-model.number="aiForm.job_satisfaction" type="number" min="1" max="10" class="flex-1 text-center py-2 text-gray-800 font-medium outline-none"/>
                <button class="px-3 py-2 bg-gray-50 text-gray-600 hover:bg-gray-100 text-lg" @click="aiForm.job_satisfaction = Math.min(10, aiForm.job_satisfaction + 1)">+</button>
              </div>
            </div>
            <!-- 睡眠时长 -->
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">每日睡眠时长（小时）</label>
              <div class="flex items-center border border-gray-200 rounded-xl overflow-hidden">
                <button class="px-3 py-2 bg-gray-50 text-gray-600 hover:bg-gray-100 text-lg" @click="aiForm.sleep_duration = Math.max(1, aiForm.sleep_duration - 0.5)">−</button>
                <input v-model.number="aiForm.sleep_duration" type="number" min="1" max="12" step="0.5" class="flex-1 text-center py-2 text-gray-800 font-medium outline-none"/>
                <button class="px-3 py-2 bg-gray-50 text-gray-600 hover:bg-gray-100 text-lg" @click="aiForm.sleep_duration = Math.min(12, aiForm.sleep_duration + 0.5)">+</button>
              </div>
            </div>
            <!-- 性别 -->
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">性别</label>
              <select v-model="aiForm.gender" class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-gray-800 outline-none focus:border-primary">
                <option value="Male">男</option>
                <option value="Female">女</option>
              </select>
            </div>
            <!-- 身份 -->
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">当前身份</label>
              <select v-model="aiForm.working_status" class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-gray-800 outline-none focus:border-primary">
                <option value="Working Professional">在职人员</option>
                <option value="Student">学生</option>
              </select>
            </div>
          </div>

          <!-- 全宽选项 -->
          <div class="space-y-4 mb-8">
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">饮食习惯</label>
              <select v-model="aiForm.dietary_habits" class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-gray-800 outline-none focus:border-primary">
                <option value="Healthy">健康规律</option>
                <option value="Moderate">一般</option>
                <option value="Unhealthy">不规律/不健康</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">是否有过自杀念头？</label>
              <select v-model="aiForm.suicidal_thoughts" class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-gray-800 outline-none focus:border-primary">
                <option value="No">否</option>
                <option value="Yes">是</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">家族是否有精神疾病史？</label>
              <select v-model="aiForm.family_history" class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-gray-800 outline-none focus:border-primary">
                <option value="No">否</option>
                <option value="Yes">是</option>
              </select>
            </div>
          </div>

          <p class="text-xs text-gray-400 text-center mb-5">本评估结果仅供参考，不构成医学诊断。如有需要请咨询专业医生。</p>

          <div class="flex gap-3">
            <button class="btn-outline flex-1" @click="phase = 'intro'">返回</button>
            <button
              class="btn-primary flex-1 flex items-center justify-center gap-2"
              :disabled="aiLoading"
              @click="submitAiForm"
            >
              <svg v-if="aiLoading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              {{ aiLoading ? '模型推理中...' : '开始AI预测' }}
            </button>
          </div>
        </div>
      </div>

      <!-- ─── Phase: SOS ────────────────────────────────────────── -->
      <div v-else-if="phase === 'sos'" class="max-w-2xl mx-auto">
        <div class="bg-white rounded-3xl shadow-card overflow-hidden">
          <!-- 红色警告头 -->
          <div class="bg-red-50 border-b-2 border-red-100 p-6">
            <div class="flex items-center gap-3 mb-3">
              <span class="text-4xl">🆘</span>
              <div>
                <h2 class="text-xl font-bold text-red-700">高风险预警</h2>
                <p class="text-red-500 text-sm">PHQ-9 第9题得分 > 0，已触发安全预警</p>
              </div>
            </div>
            <p class="text-red-700 text-sm leading-relaxed bg-red-100 rounded-xl p-3">
              我们注意到您的回答提示可能存在自我伤害的想法。这说明您现在承受着很大的痛苦。<strong>您的安全比任何评估都更重要。</strong>
            </p>
          </div>

          <div class="p-6 space-y-5">
            <p class="text-gray-600 text-sm leading-relaxed">
              您并不孤单，专业的帮助就在身边。如果您现在正处于危机或有伤害自己的想法，请立即联系以下支持热线：
            </p>

            <!-- 热线卡片 -->
            <div class="space-y-3">
              <div class="flex items-center gap-4 p-4 bg-red-50 rounded-2xl border border-red-100">
                <span class="text-3xl">📞</span>
                <div class="flex-1">
                  <div class="font-bold text-gray-800 text-sm">北京心理危机研究与干预中心</div>
                  <div class="text-primary text-xl font-mono font-bold tracking-wider">010-82951332</div>
                </div>
              </div>
              <div class="flex items-center gap-4 p-4 bg-red-50 rounded-2xl border border-red-100">
                <span class="text-3xl">📞</span>
                <div class="flex-1">
                  <div class="font-bold text-gray-800 text-sm">全国心理援助热线</div>
                  <div class="text-primary text-xl font-mono font-bold tracking-wider">400-161-9995</div>
                </div>
              </div>
              <div class="flex items-center gap-4 p-4 bg-gray-50 rounded-2xl border border-gray-200">
                <span class="text-3xl">🚑</span>
                <div class="flex-1">
                  <div class="font-bold text-gray-800 text-sm">紧急情况 · 立即求助</div>
                  <div class="text-red-600 text-xl font-mono font-bold tracking-wider">120 &nbsp;/&nbsp; 110</div>
                </div>
              </div>
            </div>

            <p class="text-xs text-gray-400 text-center">以上热线均由专业人员提供，免费保密，24小时可用</p>

            <button class="btn-primary w-full" @click="phase = 'done'">
              我已了解，继续查看评估结果
            </button>
          </div>
        </div>
      </div>

      <!-- ─── Phase: done ───────────────────────────────────────── -->
      <div v-else-if="phase === 'done' && scoreResult" class="max-w-2xl mx-auto">
        <div class="bg-white rounded-3xl shadow-card overflow-hidden">
          <!-- SOS 持续提示条 -->
          <div v-if="sosTriggered" class="bg-red-50 border-b border-red-100 px-6 py-3 flex items-center gap-3">
            <span class="text-red-500 text-lg">🔴</span>
            <p class="text-red-600 text-sm flex-1">如仍有危机想法，请立即拨打 <strong class="font-mono">400-161-9995</strong></p>
          </div>

          <div class="p-8">
            <!-- 分数仪表盘 -->
            <div class="text-center mb-8">
              <div class="relative inline-flex items-center justify-center mb-5">
                <svg class="w-40 h-40" viewBox="0 0 100 100" style="transform: rotate(-90deg)">
                  <circle cx="50" cy="50" r="40" fill="none" stroke="#f3f4f6" stroke-width="8"/>
                  <circle
                    cx="50" cy="50" r="40" fill="none"
                    :stroke="scoreResult.color" stroke-width="8"
                    stroke-linecap="round"
                    :stroke-dasharray="scoreArc"
                    style="transition: stroke-dasharray 1s ease"
                  />
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center">
                  <span class="text-4xl font-black text-gray-800">{{ scoreResult.total }}</span>
                  <span class="text-xs text-gray-400 font-medium">满分 {{ scoreResult.max }}</span>
                </div>
              </div>

              <div
                class="inline-flex items-center gap-2 px-5 py-2 rounded-full text-white font-bold text-lg mb-4"
                :style="{ backgroundColor: scoreResult.color }"
              >{{ scoreResult.level }}</div>

              <p class="text-gray-500 text-sm max-w-sm mx-auto leading-relaxed">{{ scoreResult.desc }}</p>
            </div>

            <!-- AI 抑郁预测 SOS 提示 -->
            <div v-if="selectedType === 'ai_predict' && scoreResult.depressed" class="bg-red-50 border border-red-200 rounded-2xl p-4 mb-6">
              <div class="flex items-center gap-2 mb-2">
                <span class="text-red-500 text-lg">🔴</span>
                <span class="font-bold text-red-700 text-sm">关注提示</span>
              </div>
              <p class="text-red-600 text-sm leading-relaxed">
                模型检测到您可能存在抑郁风险。请记住您并不孤单，如有需要请立即拨打心理援助热线
                <strong class="font-mono">400-161-9995</strong>，或咨询专业医生进行诊断。
              </p>
            </div>

            <!-- 评分参考范围 -->
            <div class="bg-gray-50 rounded-2xl p-4 mb-6">
              <div class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">
                {{ scoreResult.scale }} 分级参考
              </div>
              <div class="flex gap-1.5">
                <div
                  v-for="seg in scaleRanges[selectedType]" :key="seg.range"
                  class="flex-1 text-center py-2 rounded-xl text-xs font-medium"
                  :style="{ backgroundColor: seg.color + '22', color: seg.color, outline: scoreResult.level === seg.label ? `2px solid ${seg.color}` : 'none' }"
                >
                  <div class="font-bold text-xs leading-tight">{{ seg.range }}</div>
                  <div class="text-xs leading-tight mt-0.5">{{ seg.label }}</div>
                </div>
              </div>
            </div>

            <!-- 多模态采集标注（AI 预测或跳过设备时不显示） -->
            <div v-if="selectedType !== 'ai_predict' && (cameraActive || micActive)" class="grid grid-cols-3 gap-3 mb-6 text-center">
              <div class="bg-blue-50 rounded-xl p-3">
                <div class="text-xl mb-1">📸</div>
                <div class="text-xs text-gray-500 font-medium">面部情绪</div>
                <div class="text-xs text-primary font-bold">已采集</div>
              </div>
              <div class="bg-orange-50 rounded-xl p-3">
                <div class="text-xl mb-1">🎤</div>
                <div class="text-xs text-gray-500 font-medium">语音特征</div>
                <div class="text-xs text-orange-500 font-bold">已采集</div>
              </div>
              <div class="bg-green-50 rounded-xl p-3">
                <div class="text-xl mb-1">📋</div>
                <div class="text-xs text-gray-500 font-medium">量表评分</div>
                <div class="text-xs text-green-500 font-bold">已完成</div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="flex flex-col sm:flex-row gap-4">
              <button class="btn-primary flex-1" @click="goToReport">查看详细报告</button>
              <RouterLink to="/companion" class="btn-outline flex-1 text-center no-underline">与心镜对话</RouterLink>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.no-underline { text-decoration: none; }
</style>
