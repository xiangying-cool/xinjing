<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import { api } from '../services/api.js'

const router  = useRouter()
const { userId } = useAuth()

// ── 情绪类型定义 ──────────────────────────────────────────
const moodTypes = [
  { key: 'sunny',   label: '阳光',   icon: '☀️',  bg: 'bg-amber-400',  text: 'text-amber-700',  border: 'border-amber-300', light: 'bg-amber-50',   ring: 'ring-amber-400',  bar: 'bg-amber-400',  desc: '状态很好，心情愉悦开朗' },
  { key: 'partly',  label: '多云',   icon: '⛅',  bg: 'bg-sky-300',    text: 'text-sky-700',    border: 'border-sky-200',   light: 'bg-sky-50',     ring: 'ring-sky-300',    bar: 'bg-sky-300',    desc: '平静稳定，状态还不错' },
  { key: 'cloudy',  label: '阴天',   icon: '☁️',  bg: 'bg-slate-400',  text: 'text-slate-600',  border: 'border-slate-300', light: 'bg-slate-50',   ring: 'ring-slate-400',  bar: 'bg-slate-400',  desc: '有些疲惫，一般般吧' },
  { key: 'rainy',   label: '小雨',   icon: '🌧️', bg: 'bg-blue-400',   text: 'text-blue-700',   border: 'border-blue-300',  light: 'bg-blue-50',    ring: 'ring-blue-400',   bar: 'bg-blue-400',   desc: '心情有些低落，难过' },
  { key: 'stormy',  label: '暴风',   icon: '⛈️', bg: 'bg-indigo-500', text: 'text-indigo-100', border: 'border-indigo-400',light: 'bg-indigo-50',  ring: 'ring-indigo-500', bar: 'bg-indigo-500', desc: '情绪很差，感到痛苦' },
]
const getMood = (key) => moodTypes.find(m => m.key === key)

// ── Toast 提示 ─────────────────────────────────────────────
const toast = ref(null) // { msg, type: 'success'|'error' }
let toastTimer = null
function showToast(msg, type = 'success') {
  clearTimeout(toastTimer)
  toast.value = { msg, type }
  toastTimer = setTimeout(() => { toast.value = null }, 3000)
}

// ── 日期工具 ──────────────────────────────────────────────
const today = new Date()
today.setHours(0, 0, 0, 0)

function fmtDate(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
const todayKey = fmtDate(today)

// ── 数据存储（mood_calendar_records 表） ───────────────────
// 内部格式：{ 'YYYY-MM-DD': { mood: 'sunny', diary: '...' } }
const moodData = ref({})

/** 从后端加载当前用户的所有记录到 moodData */
async function loadFromDb() {
  const uid = userId.value
  if (!uid) return
  try {
    const rows = await api.get(`/mood-calendar?user_id=${uid}`)
    const map  = {}
    rows.forEach(r => { map[r.record_date] = { mood: r.mood_key, diary: r.diary_text || '' } })
    moodData.value = map
  } catch (e) {
    console.error('加载情绪日历失败:', e)
  }
}

onMounted(async () => {
  await loadFromDb()
  loadCheckins()

  // 初始化编辑区
  const rec = moodData.value[todayKey]
  editingMood.value  = rec?.mood  || null
  editingDiary.value = rec?.diary || ''
  setTimeout(() => { visible.value = true }, 80)
})

// ── 日历视图 ──────────────────────────────────────────────
const currentYear  = ref(today.getFullYear())
const currentMonth = ref(today.getMonth())

const monthLabel = computed(() =>
  `${currentYear.value} 年 ${currentMonth.value + 1} 月`
)

function prevMonth() {
  if (currentMonth.value === 0) { currentMonth.value = 11; currentYear.value-- }
  else currentMonth.value--
}
function nextMonth() {
  const now = new Date()
  if (currentYear.value === now.getFullYear() && currentMonth.value === now.getMonth()) return
  if (currentMonth.value === 11) { currentMonth.value = 0; currentYear.value++ }
  else currentMonth.value++
}
const isNextMonthDisabled = computed(() => {
  const now = new Date()
  return currentYear.value === now.getFullYear() && currentMonth.value === now.getMonth()
})

const calendarDays = computed(() => {
  const y = currentYear.value, m = currentMonth.value
  const firstDow = new Date(y, m, 1).getDay()          // 0=Sun
  const offset   = firstDow === 0 ? 6 : firstDow - 1   // Mon-first
  const daysInM  = new Date(y, m + 1, 0).getDate()
  const days = []
  for (let i = 0; i < offset; i++) days.push(null)
  for (let d = 1; d <= daysInM; d++) {
    const date  = new Date(y, m, d)
    const key   = fmtDate(date)
    const isFut = date > today
    days.push({ day: d, key, record: moodData.value[key] || null, isToday: key === todayKey, isFuture: isFut })
  }
  return days
})

// ── 选中日期 & 编辑 ────────────────────────────────────────
const selectedKey  = ref(todayKey)
const editingMood  = ref(null)
const editingDiary = ref('')

const selectedDay    = computed(() => { const [y,m,d] = selectedKey.value.split('-').map(Number); return new Date(y,m-1,d) })
const isSelToday     = computed(() => selectedKey.value === todayKey)
const isSelFuture    = computed(() => selectedDay.value > today)
const selectedRecord = computed(() => moodData.value[selectedKey.value] || null)

function selectDay(day) {
  if (!day || day.isFuture) return
  selectedKey.value  = day.key
  const rec = moodData.value[day.key]
  editingMood.value  = rec?.mood  || null
  editingDiary.value = rec?.diary || ''
}

// 当切换月份时，若选中日不在当月则重置到今天
watch([currentYear, currentMonth], () => {
  const [y, m] = [currentYear.value, currentMonth.value]
  const [sy, sm] = selectedKey.value.split('-').map(Number)
  if (sy !== y || sm - 1 !== m) {
    // 选中本月今天或本月1号
    if (y === today.getFullYear() && m === today.getMonth()) {
      selectedKey.value = todayKey
      editingMood.value  = moodData.value[todayKey]?.mood  || null
      editingDiary.value = moodData.value[todayKey]?.diary || ''
    } else {
      const firstKey = `${y}-${String(m+1).padStart(2,'0')}-01`
      selectedKey.value  = firstKey
      editingMood.value  = moodData.value[firstKey]?.mood  || null
      editingDiary.value = moodData.value[firstKey]?.diary || ''
    }
  }
})

async function saveDayRecord() {
  if (!editingMood.value || !userId.value) return
  // 先乐观更新本地缓存（让 UI 立即响应）
  moodData.value[selectedKey.value] = {
    mood:  editingMood.value,
    diary: editingDiary.value.trim(),
  }
  // 异步同步到后端
  try {
    await api.put(`/mood-calendar/${selectedKey.value}`, {
      user_id:    userId.value,
      mood_key:   editingMood.value,
      diary_text: editingDiary.value.trim(),
    })
    showToast('打卡成功 ✓')
  } catch (e) {
    console.error('保存情绪记录失败:', e)
    showToast('保存失败，请稍后重试', 'error')
  }
}

// ── 四维情绪打卡 ─────────────────────────────────────────
const checkinDims = [
  { key: 'mood_score',   label: '情绪状态', icon: '😊', activeCls: 'bg-amber-400' },
  { key: 'stress_score', label: '压力水平', icon: '😰', activeCls: 'bg-rose-400' },
  { key: 'sleep_score',  label: '睡眠质量', icon: '💤', activeCls: 'bg-indigo-400' },
  { key: 'energy_score', label: '精力状态', icon: '⚡', activeCls: 'bg-green-400' },
]

const checkins         = ref([])
const checkinDone      = ref(false)
const checkinSubmitting = ref(false)
const checkinForm      = reactive({ mood_score: 0, stress_score: 0, sleep_score: 0, energy_score: 0, note: '' })

async function loadCheckins() {
  if (!userId.value) return
  try {
    const rows = await api.get('/mood-calendar/checkins?limit=7')
    checkins.value = rows
    const todayStr = fmtDate(new Date())
    const todayRec = rows.find(c => c.created_at?.slice(0, 10) === todayStr)
    if (todayRec) {
      Object.assign(checkinForm, {
        mood_score:   todayRec.mood_score,
        stress_score: todayRec.stress_score,
        sleep_score:  todayRec.sleep_score,
        energy_score: todayRec.energy_score,
        note:         todayRec.note || '',
      })
      checkinDone.value = true
    }
  } catch { /* silent */ }
}

async function submitCheckin() {
  const { mood_score, stress_score, sleep_score, energy_score, note } = checkinForm
  if (!mood_score || !stress_score || !sleep_score || !energy_score) return
  checkinSubmitting.value = true
  try {
    const row = await api.post('/mood-calendar/checkins', {
      mood_score, stress_score, sleep_score, energy_score,
      note: note.trim() || null,
    })
    const todayStr = fmtDate(new Date())
    checkins.value = [row, ...checkins.value.filter(c => c.created_at?.slice(0, 10) !== todayStr).slice(0, 6)]
    checkinDone.value = true
    showToast('四维打卡完成 ✓')
    // 同步保存趋势快照
    api.put(`/mood-calendar/trends/${todayStr}`, {
      avg_mood_score:   mood_score,
      avg_stress_score: stress_score,
      avg_sleep_score:  sleep_score,
    }).catch(() => {})
  } catch (e) {
    console.error('提交打卡失败:', e)
    showToast('提交失败，请稍后重试', 'error')
  } finally {
    checkinSubmitting.value = false
  }
}

async function deleteRecord() {
  const key = selectedKey.value
  if (!key || !userId.value || !moodData.value[key]) return
  // 乐观删除
  const backup = moodData.value[key]
  delete moodData.value[key]
  moodData.value = { ...moodData.value }
  try {
    await api.delete(`/mood-calendar/${key}?user_id=${userId.value}`)
  } catch (e) {
    console.error('删除情绪记录失败:', e)
    moodData.value[key] = backup
    moodData.value = { ...moodData.value }
  }
}

// ── 统计 ──────────────────────────────────────────────────
const monthStats = computed(() => {
  const y = currentYear.value, m = currentMonth.value
  const counts = {}
  moodTypes.forEach(t => { counts[t.key] = 0 })
  let total = 0
  Object.entries(moodData.value).forEach(([key, rec]) => {
    const [ky, km] = key.split('-').map(Number)
    if (ky === y && km - 1 === m && rec.mood) {
      counts[rec.mood] = (counts[rec.mood] || 0) + 1
      total++
    }
  })
  return { counts, total }
})

const streak = computed(() => {
  let count = 0, d = new Date(today)
  while (true) {
    if (moodData.value[fmtDate(d)]?.mood) { count++; d.setDate(d.getDate() - 1) }
    else break
  }
  return count
})

const totalDiaries = computed(() =>
  Object.values(moodData.value).filter(r => r.diary).length
)

const totalSunny = computed(() =>
  Object.values(moodData.value).filter(r => r.mood === 'sunny').length
)

// ── 近期日记 ─────────────────────────────────────────────
const recentDiaries = computed(() =>
  Object.entries(moodData.value)
    .filter(([, r]) => r.diary)
    .sort(([a], [b]) => b.localeCompare(a))
    .slice(0, 6)
    .map(([key, r]) => {
      const [, mm, dd] = key.split('-')
      return { key, label: `${parseInt(mm)}/${parseInt(dd)}`, diary: r.diary, mood: getMood(r.mood) }
    })
)

// ── AI 洞察 ───────────────────────────────────────────────
const aiInsight = computed(() => {
  const { counts, total } = monthStats.value
  if (total === 0) return '本月还没有打卡记录，快来记录今天的情绪天气吧 🌈'
  const sunny  = counts.sunny  || 0
  const partly = counts.partly || 0
  const stormy = counts.stormy || 0
  const rainy  = counts.rainy  || 0
  if (sunny / total > 0.6)
    return `本月有 ${sunny} 天阳光灿烂，整体状态积极向上！继续保持这份好心情，你做得很棒 ☀️`
  if ((stormy + rainy) / total > 0.4)
    return `本月有 ${stormy + rainy} 天情绪较低落，记得多关爱自己。有需要时，可以去情绪陪伴与数字人倾诉 💙`
  if ((sunny + partly) / total > 0.6)
    return `本月整体情绪稳定偏好，有 ${sunny + partly} 天状态不错，继续保持规律作息和适当运动 🌤️`
  return `本月情绪有波动，这很正常。记录了 ${total} 天，坚持觉察自己是了解内心的第一步 🌱`
})

const aiTip = computed(() => {
  const tips = [
    '研究发现，坚持记录情绪日记有助于提升自我觉察，减少焦虑感。每天1分钟，积累了解自己的力量。',
    '命名情绪本身就有疗愈效果。当你说出"我现在很焦虑"，大脑杏仁核的活动会随之降低。',
    '情绪没有好坏之分，每种情绪都在传递重要信息。试着问问自己：这种感受想告诉我什么？',
    '规律运动、充足睡眠和社交连接是维持情绪稳定的三大支柱。你今天照顾好自己了吗？',
  ]
  // 根据当天日期选 tip（固定不随机抖动）
  return tips[today.getDate() % tips.length]
})

// ── 周趋势（近7天） ───────────────────────────────────────
const weekTrend = computed(() => {
  const moodScore = { sunny: 5, partly: 4, cloudy: 3, rainy: 2, stormy: 1 }
  const result = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(today.getDate() - i)
    const key = fmtDate(d)
    const rec = moodData.value[key]
    const dow = ['日','一','二','三','四','五','六'][d.getDay()]
    result.push({
      key,
      label: i === 0 ? '今' : dow,
      score: rec?.mood ? moodScore[rec.mood] : null,
      mood:  rec?.mood ? getMood(rec.mood) : null,
    })
  }
  return result
})

// ── 入场动画 ─────────────────────────────────────────────
const visible = ref(false)
</script>

<template>
  <div class="min-h-screen" style="background: linear-gradient(160deg, #EEF6FF 0%, #FFF5FB 45%, #EDFFF8 100%)">

    <!-- ── 页头 ─────────────────────────────────────────── -->
    <section class="pt-14 pb-6 px-6">
      <div class="max-w-7xl mx-auto">
        <div
          class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 transition-all duration-700"
          :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
        >
          <div>
            <div class="flex items-center gap-3 mb-1.5">
              <span class="text-5xl select-none">🌈</span>
              <div>
                <h1 class="text-3xl font-black text-gray-800 leading-tight">情绪日历</h1>
                <p class="text-sm text-gray-400 mt-0.5">记录每日情绪天气，洞察心情变化轨迹</p>
              </div>
            </div>
          </div>
          <!-- 今日天气快显 -->
          <div
            v-if="moodData[todayKey]?.mood"
            class="flex items-center gap-3 px-5 py-3 rounded-2xl border bg-white/80 backdrop-blur shadow-sm"
            :class="getMood(moodData[todayKey].mood)?.border"
          >
            <span class="text-3xl">{{ getMood(moodData[todayKey].mood)?.icon }}</span>
            <div>
              <div class="text-xs text-gray-400">今天的天气</div>
              <div class="font-bold text-gray-700">{{ getMood(moodData[todayKey].mood)?.label }}</div>
            </div>
          </div>
          <div v-else class="flex items-center gap-3 px-5 py-3 rounded-2xl border border-dashed border-gray-300 bg-white/60">
            <span class="text-3xl">🌀</span>
            <div>
              <div class="text-xs text-gray-400">今天还没打卡</div>
              <div class="text-sm font-medium text-gray-500">快去记录吧</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── 统计数字 ────────────────────────────────────── -->
    <section class="px-6 mb-6">
      <div class="max-w-7xl mx-auto">
        <div
          class="grid grid-cols-2 sm:grid-cols-4 gap-3 transition-all duration-700 delay-100"
          :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
        >
          <div class="bg-white/80 backdrop-blur rounded-2xl p-4 shadow-sm border border-white/90 flex items-center gap-3">
            <div class="w-11 h-11 rounded-xl bg-amber-100 flex items-center justify-center text-2xl flex-shrink-0">🔥</div>
            <div>
              <div class="text-2xl font-black text-amber-500 leading-tight">{{ streak }}</div>
              <div class="text-xs text-gray-400">连续打卡</div>
            </div>
          </div>
          <div class="bg-white/80 backdrop-blur rounded-2xl p-4 shadow-sm border border-white/90 flex items-center gap-3">
            <div class="w-11 h-11 rounded-xl bg-sky-100 flex items-center justify-center text-2xl flex-shrink-0">📅</div>
            <div>
              <div class="text-2xl font-black text-sky-500 leading-tight">{{ monthStats.total }}</div>
              <div class="text-xs text-gray-400">本月已记录</div>
            </div>
          </div>
          <div class="bg-white/80 backdrop-blur rounded-2xl p-4 shadow-sm border border-white/90 flex items-center gap-3">
            <div class="w-11 h-11 rounded-xl bg-amber-50 flex items-center justify-center text-2xl flex-shrink-0">☀️</div>
            <div>
              <div class="text-2xl font-black text-amber-400 leading-tight">{{ totalSunny }}</div>
              <div class="text-xs text-gray-400">阳光天数</div>
            </div>
          </div>
          <div class="bg-white/80 backdrop-blur rounded-2xl p-4 shadow-sm border border-white/90 flex items-center gap-3">
            <div class="w-11 h-11 rounded-xl bg-purple-100 flex items-center justify-center text-2xl flex-shrink-0">📝</div>
            <div>
              <div class="text-2xl font-black text-purple-500 leading-tight">{{ totalDiaries }}</div>
              <div class="text-xs text-gray-400">日记条数</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── 主体区域 ────────────────────────────────────── -->
    <section class="px-6 pb-16">
      <div class="max-w-7xl mx-auto">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

          <!-- ── 左 / 中：日历 + 周趋势 + 近期日记 ──────── -->
          <div class="lg:col-span-2 space-y-6">

            <!-- 日历卡片 -->
            <div
              class="bg-white/90 backdrop-blur rounded-3xl shadow-md border border-white/80 p-6 transition-all duration-700 delay-150"
              :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
            >
              <!-- 月份导航 -->
              <div class="flex items-center justify-between mb-5">
                <button
                  @click="prevMonth"
                  class="w-9 h-9 rounded-xl bg-gray-100 hover:bg-primary/10 hover:text-primary flex items-center justify-center transition-colors text-gray-400"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                  </svg>
                </button>
                <h2 class="text-lg font-bold text-gray-800">{{ monthLabel }}</h2>
                <button
                  @click="nextMonth"
                  :disabled="isNextMonthDisabled"
                  class="w-9 h-9 rounded-xl bg-gray-100 flex items-center justify-center transition-colors"
                  :class="isNextMonthDisabled ? 'opacity-30 cursor-not-allowed text-gray-300' : 'hover:bg-primary/10 hover:text-primary text-gray-400'"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                  </svg>
                </button>
              </div>

              <!-- 星期标题（周一起） -->
              <div class="grid grid-cols-7 mb-1.5">
                <div
                  v-for="d in ['一','二','三','四','五','六','日']"
                  :key="d"
                  class="text-center text-xs font-medium py-1"
                  :class="d === '六' || d === '日' ? 'text-rose-300' : 'text-gray-300'"
                >{{ d }}</div>
              </div>

              <!-- 日期格子 -->
              <div class="grid grid-cols-7 gap-1.5">
                <div v-for="(day, i) in calendarDays" :key="i">
                  <!-- 占位 -->
                  <div v-if="!day" class="aspect-square"></div>
                  <!-- 日期单元格 -->
                  <button
                    v-else
                    @click="selectDay(day)"
                    :disabled="day.isFuture"
                    class="w-full aspect-square rounded-xl flex flex-col items-center justify-center relative transition-all duration-150 select-none"
                    :class="[
                      day.isFuture ? 'opacity-25 cursor-not-allowed' : 'cursor-pointer',
                      day.key === selectedKey
                        ? 'scale-110 shadow-md z-10 ring-2 ring-offset-1 ' + (day.record?.mood ? getMood(day.record.mood)?.ring : 'ring-primary')
                        : day.record?.mood ? 'hover:scale-105' : 'hover:scale-105',
                      day.record?.mood
                        ? getMood(day.record.mood)?.bg + ' text-white shadow-sm'
                        : day.isToday
                          ? 'bg-primary/10 text-primary border border-primary/30'
                          : 'bg-gray-50 text-gray-400 hover:bg-gray-100',
                    ]"
                  >
                    <span class="text-[11px] font-bold leading-none">{{ day.day }}</span>
                    <span v-if="day.record?.mood" class="text-[13px] leading-none mt-0.5">{{ getMood(day.record.mood)?.icon }}</span>
                    <!-- 有日记的白点 -->
                    <span
                      v-if="day.record?.diary"
                      class="absolute top-0.5 right-1 w-1.5 h-1.5 rounded-full bg-white/80"
                    ></span>
                  </button>
                </div>
              </div>

              <!-- 图例 -->
              <div class="flex flex-wrap items-center gap-x-5 gap-y-2 mt-5 pt-4 border-t border-gray-100">
                <div v-for="m in moodTypes" :key="m.key" class="flex items-center gap-1.5 text-xs text-gray-400">
                  <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" :class="m.bg"></span>
                  <span>{{ m.icon }} {{ m.label }}</span>
                </div>
                <div class="flex items-center gap-1.5 text-xs text-gray-300 ml-auto">
                  <span class="w-1.5 h-1.5 rounded-full bg-gray-300 flex-shrink-0"></span>
                  <span>有日记</span>
                </div>
              </div>
            </div>

            <!-- 近7天趋势 -->
            <div
              class="bg-white/90 backdrop-blur rounded-3xl shadow-md border border-white/80 p-6 transition-all duration-700 delay-200"
              :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
            >
              <h3 class="font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span class="text-lg">📈</span> 近7天情绪趋势
              </h3>
              <div class="flex items-end gap-2 h-28">
                <div
                  v-for="item in weekTrend"
                  :key="item.key"
                  class="flex-1 flex flex-col items-center gap-1.5 cursor-pointer"
                  @click="() => { currentYear.value = parseInt(item.key.split('-')[0]); currentMonth.value = parseInt(item.key.split('-')[1]) - 1; selectDay({ key: item.key, record: moodData[item.key] || null, isToday: item.key === todayKey, isFuture: false, day: parseInt(item.key.split('-')[2]) }) }"
                >
                  <!-- 表情 -->
                  <span class="text-lg leading-none">{{ item.mood ? item.mood.icon : '·' }}</span>
                  <!-- 柱子 -->
                  <div class="w-full rounded-t-lg transition-all duration-700 relative overflow-hidden"
                    :style="{ height: item.score ? (item.score / 5 * 60) + 'px' : '6px' }"
                    :class="item.score ? item.mood?.bar : 'bg-gray-100'"
                  >
                    <!-- 高光 -->
                    <div v-if="item.score" class="absolute inset-x-0 top-0 h-1/3 bg-white/25 rounded-t-lg"></div>
                  </div>
                  <!-- 星期 -->
                  <span class="text-[11px] font-medium" :class="item.key === todayKey ? 'text-primary font-bold' : 'text-gray-400'">
                    {{ item.label }}
                  </span>
                </div>
              </div>
              <!-- 情绪分值说明 -->
              <div class="flex justify-between text-[10px] text-gray-300 mt-3 px-1">
                <span>暴风 ↓</span>
                <span>↑ 阳光</span>
              </div>
            </div>

            <!-- AI 洞察 -->
            <div
              class="rounded-3xl border p-5 flex items-start gap-4 transition-all duration-700 delay-250"
              :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
              style="background: linear-gradient(135deg, #EEF6FF 0%, #F0FFF8 100%); border-color: #BFDBFE;"
            >
              <div class="w-10 h-10 rounded-2xl bg-primary/15 flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.347.347a3.75 3.75 0 01-1.065 2.432V21H9v-2.121a3.75 3.75 0 01-1.065-2.432L7.343 16.3z"
                  />
                </svg>
              </div>
              <div class="flex-1">
                <div class="text-xs font-semibold text-primary mb-1.5">AI 情绪洞察</div>
                <p class="text-sm text-gray-600 leading-relaxed">{{ aiInsight }}</p>
              </div>
            </div>

            <!-- 近期日记回顾 -->
            <div
              v-if="recentDiaries.length > 0"
              class="bg-white/90 backdrop-blur rounded-3xl shadow-md border border-white/80 p-6 transition-all duration-700 delay-300"
              :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
            >
              <h3 class="font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span class="text-lg">📖</span> 近期日记回顾
              </h3>
              <div class="space-y-2.5">
                <div
                  v-for="entry in recentDiaries"
                  :key="entry.key"
                  class="flex items-start gap-3 px-4 py-3 rounded-2xl cursor-pointer hover:opacity-90 transition-opacity"
                  :class="entry.mood?.light"
                  @click="() => { currentYear.value = parseInt(entry.key.split('-')[0]); currentMonth.value = parseInt(entry.key.split('-')[1]) - 1; selectDay({ key: entry.key, record: moodData[entry.key] || null, isToday: entry.key === todayKey, isFuture: false, day: parseInt(entry.key.split('-')[2]) }) }"
                >
                  <span class="text-xl flex-shrink-0 mt-0.5">{{ entry.mood?.icon }}</span>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm text-gray-700 leading-snug line-clamp-1">{{ entry.diary }}</p>
                    <p class="text-xs text-gray-400 mt-0.5">{{ entry.label }} · {{ entry.mood?.label }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ── 右：打卡面板 + 分布 + 贴士 ─────────────── -->
          <div class="space-y-5 sticky top-20 self-start">

            <!-- 打卡 / 查看面板 -->
            <div
              class="bg-white/90 backdrop-blur rounded-3xl shadow-md border border-white/80 p-6 transition-all duration-700 delay-200"
              :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
            >
              <!-- 标题行 -->
              <div class="flex items-center justify-between mb-5">
                <h3 class="font-bold text-gray-800">
                  {{ isSelToday ? '今日打卡' : `${selectedDay.getMonth()+1} 月 ${selectedDay.getDate()} 日` }}
                </h3>
                <span
                  v-if="isSelToday"
                  class="text-xs bg-primary/10 text-primary px-2.5 py-1 rounded-full font-semibold"
                >今天</span>
                <span
                  v-else-if="selectedRecord"
                  class="text-xs bg-gray-100 text-gray-500 px-2.5 py-1 rounded-full"
                >历史</span>
              </div>

              <!-- 情绪选择器 -->
              <p class="text-xs text-gray-400 mb-3">今天的情绪天气是？</p>
              <div class="grid grid-cols-5 gap-1.5 mb-4">
                <button
                  v-for="m in moodTypes"
                  :key="m.key"
                  @click="isSelToday && (editingMood = m.key)"
                  :disabled="!isSelToday"
                  class="flex flex-col items-center gap-1 py-2.5 px-1 rounded-xl border-2 transition-all duration-150"
                  :class="editingMood === m.key
                    ? [m.border, m.light, 'scale-[1.08] shadow-sm']
                    : 'border-transparent bg-gray-50 hover:bg-gray-100'"
                  :title="m.desc"
                >
                  <span class="text-xl leading-none">{{ m.icon }}</span>
                  <span class="text-[10px] font-medium text-gray-500 leading-none">{{ m.label }}</span>
                </button>
              </div>

              <!-- 当前选中情绪描述 -->
              <Transition name="fade">
                <div
                  v-if="editingMood"
                  class="text-xs text-center py-2 px-3 rounded-xl mb-4 font-medium"
                  :class="[getMood(editingMood)?.light, getMood(editingMood)?.text]"
                >
                  {{ getMood(editingMood)?.icon }} {{ getMood(editingMood)?.desc }}
                </div>
              </Transition>

              <!-- 一句话日记 -->
              <div class="mb-5">
                <label class="text-xs text-gray-400 mb-1.5 flex items-center gap-1.5">
                  <span>✏️</span> 一句话日记
                  <span class="text-gray-300 font-normal">（选填）</span>
                </label>
                <textarea
                  v-model="editingDiary"
                  :disabled="!isSelToday"
                  placeholder="今天发生了什么？一句话记录下来..."
                  maxlength="300"
                  rows="3"
                  class="w-full text-sm rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/40 transition-all placeholder-gray-300 leading-relaxed"
                  :class="!isSelToday ? 'opacity-60 cursor-not-allowed' : ''"
                ></textarea>
                <div class="text-right text-xs text-gray-300 mt-0.5">{{ editingDiary.length }}/300</div>
              </div>

              <!-- 保存按钮 -->
              <button
                v-if="isSelToday"
                @click="saveDayRecord"
                :disabled="!editingMood"
                class="w-full py-3 rounded-xl font-semibold text-sm transition-all duration-200"
                :class="editingMood
                  ? 'bg-primary text-white hover:bg-primary/90 shadow-md shadow-primary/25 hover:-translate-y-0.5'
                  : 'bg-gray-100 text-gray-300 cursor-not-allowed'"
              >
                {{ moodData[todayKey] ? '更新今日记录 ✓' : '完成打卡 ✓' }}
              </button>

              <!-- 历史记录提示 -->
              <div v-else-if="selectedRecord" class="text-center">
                <div class="text-3xl mb-1">{{ getMood(selectedRecord.mood)?.icon }}</div>
                <div class="text-sm font-semibold" :class="getMood(selectedRecord.mood)?.text.replace('text-','text-')">
                  {{ getMood(selectedRecord.mood)?.label }}
                </div>
                <div v-if="selectedRecord.diary" class="text-xs text-gray-500 mt-2 italic leading-relaxed">
                  "{{ selectedRecord.diary }}"
                </div>
                <button
                  @click="deleteRecord"
                  class="mt-4 px-4 py-1.5 rounded-xl text-xs text-red-400 border border-red-200 hover:bg-red-50 transition-colors"
                >
                  删除此记录
                </button>
              </div>
              <div v-else class="text-center text-xs text-gray-300 py-2">这天没有记录</div>

              <!-- 快捷跳情绪陪伴 -->
              <div v-if="isSelToday && (editingMood === 'rainy' || editingMood === 'stormy')" class="mt-4 pt-4 border-t border-gray-100">
                <p class="text-xs text-gray-500 mb-2 text-center">感觉不太好？去聊聊吧</p>
                <RouterLink
                  to="/companion"
                  class="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-teal-brand/10 text-teal-brand text-sm font-medium hover:bg-teal-brand/20 transition-colors no-underline"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                  与数字人倾诉
                </RouterLink>
              </div>
            </div>

            <!-- 本月情绪分布 -->
            <div
              v-if="monthStats.total > 0"
              class="bg-white/90 backdrop-blur rounded-3xl shadow-md border border-white/80 p-5 transition-all duration-700 delay-300"
              :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
            >
              <h3 class="font-bold text-gray-700 text-sm mb-4 flex items-center gap-2">
                <span>📊</span> 本月情绪分布
              </h3>
              <div class="space-y-3">
                <div v-for="m in moodTypes" :key="m.key" class="flex items-center gap-2">
                  <span class="text-base w-5 flex-shrink-0">{{ m.icon }}</span>
                  <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all duration-1000"
                      :class="m.bg"
                      :style="{ width: monthStats.total > 0 ? ((monthStats.counts[m.key] || 0) / monthStats.total * 100) + '%' : '0%' }"
                    ></div>
                  </div>
                  <span class="text-xs text-gray-400 w-5 text-right flex-shrink-0">{{ monthStats.counts[m.key] || 0 }}</span>
                </div>
              </div>
              <!-- 饼图风格的总结 -->
              <div class="mt-4 pt-3 border-t border-gray-100 text-xs text-gray-400 text-center">
                共记录 {{ monthStats.total }} 天 · 好状态占比 {{ monthStats.total > 0 ? Math.round(((monthStats.counts.sunny||0)+(monthStats.counts.partly||0))/monthStats.total*100) : 0 }}%
              </div>
            </div>

            <!-- 四维情绪打卡 -->
            <div
              class="bg-white/90 backdrop-blur rounded-3xl shadow-md border border-white/80 p-5 transition-all duration-700 delay-350"
              :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
            >
              <h3 class="font-bold text-gray-700 text-sm mb-4 flex items-center gap-2">
                <span>💪</span> 今日四维打卡
                <span
                  v-if="checkinDone"
                  class="ml-auto text-[10px] bg-green-100 text-green-600 px-2 py-0.5 rounded-full font-medium"
                >已打卡 ✓</span>
              </h3>

              <!-- 四个维度评分 -->
              <div class="space-y-3 mb-4">
                <div
                  v-for="dim in checkinDims"
                  :key="dim.key"
                  class="flex items-center gap-2"
                >
                  <span class="text-base w-5 flex-shrink-0 leading-none">{{ dim.icon }}</span>
                  <span class="text-[11px] text-gray-500 w-14 flex-shrink-0">{{ dim.label }}</span>
                  <div class="flex gap-1.5 flex-1">
                    <button
                      v-for="n in 5"
                      :key="n"
                      @click="!checkinDone && (checkinForm[dim.key] = n)"
                      :disabled="checkinDone"
                      class="w-5 h-5 rounded-full transition-all duration-150 flex-shrink-0"
                      :class="n <= checkinForm[dim.key] ? dim.activeCls : 'bg-gray-100 hover:bg-gray-200'"
                    ></button>
                  </div>
                  <span class="text-[10px] text-gray-400 w-4 text-right flex-shrink-0">
                    {{ checkinForm[dim.key] || '-' }}
                  </span>
                </div>
              </div>

              <!-- 备注 -->
              <textarea
                v-if="!checkinDone"
                v-model="checkinForm.note"
                placeholder="今天有什么感受？（选填）"
                rows="2"
                maxlength="255"
                class="w-full text-xs rounded-xl border border-gray-200 bg-gray-50 px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all placeholder-gray-300 mb-3"
              ></textarea>

              <!-- 提交按钮 -->
              <button
                v-if="!checkinDone"
                @click="submitCheckin"
                :disabled="!checkinForm.mood_score || !checkinForm.stress_score || !checkinForm.sleep_score || !checkinForm.energy_score || checkinSubmitting"
                class="w-full py-2.5 rounded-xl text-sm font-semibold transition-all duration-200"
                :class="checkinForm.mood_score && checkinForm.stress_score && checkinForm.sleep_score && checkinForm.energy_score && !checkinSubmitting
                  ? 'bg-primary text-white hover:bg-primary/90 shadow-md shadow-primary/20'
                  : 'bg-gray-100 text-gray-300 cursor-not-allowed'"
              >
                {{ checkinSubmitting ? '提交中…' : '提交打卡' }}
              </button>

              <!-- 近期记录 -->
              <div v-if="checkins.length > 0" class="mt-4 pt-3 border-t border-gray-100">
                <p class="text-[10px] text-gray-400 mb-2">近期记录</p>
                <div class="space-y-1.5">
                  <div
                    v-for="c in checkins.slice(0, 5)"
                    :key="c.id"
                    class="flex items-center gap-2 text-[10px] text-gray-500 bg-gray-50 rounded-xl px-2.5 py-1.5"
                  >
                    <span class="text-gray-400 w-10 flex-shrink-0">{{ c.created_at?.slice(5, 10) }}</span>
                    <div class="flex gap-2 flex-1">
                      <span v-for="dim in checkinDims" :key="dim.key" class="flex items-center gap-0.5">
                        <span class="leading-none">{{ dim.icon }}</span>
                        <span class="font-medium text-gray-600">{{ c[dim.key] }}</span>
                      </span>
                    </div>
                    <span v-if="c.note" class="text-gray-400 truncate max-w-[60px]" :title="c.note">{{ c.note }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 情绪小贴士 -->
            <div
              class="rounded-3xl border border-teal-100 p-5 transition-all duration-700 delay-350"
              :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
              style="background: linear-gradient(135deg, #F0FDF9 0%, #ECFDF5 100%)"
            >
              <h3 class="font-semibold text-teal-700 text-sm mb-2.5 flex items-center gap-1.5">
                <span>💡</span> 今日情绪小贴士
              </h3>
              <p class="text-xs text-teal-600 leading-relaxed">{{ aiTip }}</p>
            </div>

            <!-- 前往辅助筛查 -->
            <div
              class="rounded-3xl border border-blue-100 p-5 transition-all duration-700 delay-400"
              :class="visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
              style="background: linear-gradient(135deg, #EFF6FF 0%, #EEF2FF 100%)"
            >
              <p class="text-xs text-blue-600 mb-3 leading-relaxed">想更全面了解自己的心理状态？专业量表评估更精准。</p>
              <RouterLink
                to="/screening"
                class="flex items-center justify-between w-full py-2.5 px-4 bg-white rounded-xl text-sm font-medium text-primary border border-primary/20 hover:border-primary/50 hover:shadow-sm transition-all no-underline"
              >
                <span>前往辅助筛查</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
              </RouterLink>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- Toast 提示 -->
    <Transition name="toast">
      <div
        v-if="toast"
        class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-5 py-3 rounded-2xl shadow-lg text-sm font-medium flex items-center gap-2 pointer-events-none"
        :class="toast.type === 'error' ? 'bg-red-500 text-white' : 'bg-gray-800 text-white'"
      >
        <span>{{ toast.type === 'error' ? '❌' : '✅' }}</span>
        {{ toast.msg }}
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.no-underline { text-decoration: none; }
.line-clamp-1 { overflow: hidden; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
.toast-enter-active, .toast-leave-active { transition: opacity 0.25s, transform 0.25s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(12px); }
.toast-enter-to, .toast-leave-from { opacity: 1; transform: translateX(-50%) translateY(0); }
</style>
