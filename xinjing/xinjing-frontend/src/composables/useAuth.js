import { reactive, computed } from 'vue'
import { api } from '../services/api.js'

function hasValidUserId(user) {
  return Number.isInteger(Number(user?.id)) && Number(user.id) > 0
}

function hasValidSession(payload) {
  return !!payload?.token && hasValidUserId(payload?.user)
}

// 全局单例状态
const state = reactive({
  user:    null,   // users 表字段（不含 password_hash）
  profile: null,   // user_profiles 表字段
  token:   null,
})

// 初始化：从 localStorage 恢复登录状态
const saved = localStorage.getItem('xinjing_auth')
if (saved) {
  try {
    const parsed = JSON.parse(saved)
    if (hasValidSession(parsed)) {
      state.user    = parsed.user
      state.profile = parsed.profile
      state.token   = parsed.token
    } else {
      localStorage.removeItem('xinjing_auth')
    }
  } catch {}
}

function persist() {
  localStorage.setItem('xinjing_auth', JSON.stringify({
    user: state.user, profile: state.profile, token: state.token,
  }))
}

export function useAuth() {
  const isLoggedIn  = computed(() => !!state.token && hasValidUserId(state.user))
  const currentUser = computed(() => state.user)
  const userProfile = computed(() => state.profile)

  /** 当前用户 id */
  const userId = computed(() => (hasValidUserId(state.user) ? Number(state.user.id) : null))

  /** 显示名：优先昵称，其次用户名 */
  const displayName = computed(() =>
    state.profile?.nickname || state.user?.username || ''
  )

  // ── 登录 ──────────────────────────────────────────────
  async function login(username, password) {
    try {
      const data = await api.post('/auth/login', { username, password })
      // data = { access_token, token_type, user }
      state.token = data.access_token
      state.user  = data.user

      // 获取用户档案（有则取，无则跳过）
      try {
        state.profile = await api.get(`/users/${data.user.id}/profile`)
      } catch {
        state.profile = null
      }

      persist()
      return { ok: true }
    } catch (e) {
      return { ok: false, message: e.message }
    }
  }

  // ── 注册 ──────────────────────────────────────────────
  async function register({ username, password, nickname = '', email = '', phone = '',
                            gender = '', age_range = '' }) {
    try {
      await api.post('/auth/register', { username, password, nickname, email, phone, gender, age_range })
      // 注册成功后自动登录获取 token
      return await login(username, password)
    } catch (e) {
      return { ok: false, message: e.message }
    }
  }

  // ── 更新档案 ───────────────────────────────────────────
  async function updateProfile(fields) {
    if (!state.user) return
    try {
      const updated = await api.put(`/users/${state.user.id}/profile`, fields)
      state.profile = updated
      persist()
    } catch (e) {
      console.error('updateProfile failed:', e)
    }
  }

  // ── 登出 ──────────────────────────────────────────────
  function logout() {
    state.user    = null
    state.profile = null
    state.token   = null
    localStorage.removeItem('xinjing_auth')
  }

  return { isLoggedIn, currentUser, userProfile, userId, displayName,
           login, register, updateProfile, logout }
}
