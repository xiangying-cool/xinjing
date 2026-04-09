/**
 * Mock Database Service
 * 使用 localStorage 模拟数据库，字段与真实数据库设计保持一致。
 * 后续对接真实后端时，只需将各方法替换为 axios API 调用即可。
 */

// ── 工具函数 ───────────────────────────────────────────────────────────────
function getTable(name) {
  try { return JSON.parse(localStorage.getItem(`xj_db_${name}`)) || [] } catch { return [] }
}
function saveTable(name, rows) {
  localStorage.setItem(`xj_db_${name}`, JSON.stringify(rows))
}
function nextId(rows) {
  return rows.length === 0 ? 1 : Math.max(...rows.map(r => r.id)) + 1
}
function now() { return new Date().toISOString() }

/** 简单密码哈希（演示用，非生产级） */
function hashPassword(password) {
  return btoa(unescape(encodeURIComponent(password + '_xinjing_salt')))
}
function verifyPassword(password, hash) {
  return hashPassword(password) === hash
}

// ─────────────────────────────────────────────────────────────────────────────
// 1. users 用户表
// ─────────────────────────────────────────────────────────────────────────────
export const usersDb = {
  findAll: () => getTable('users'),

  findById: (id) => getTable('users').find(u => u.id === id) || null,

  findByUsername: (username) =>
    getTable('users').find(u => u.username === username) || null,

  findByEmail: (email) =>
    email ? getTable('users').find(u => u.email === email) || null : null,

  /** 注册新用户；重复时抛出含 message 的 Error */
  create({ username, email = '', phone = '', password, role = 'user', status = 'active' }) {
    const users = getTable('users')
    if (users.find(u => u.username === username))       throw new Error('用户名已存在')
    if (email && users.find(u => u.email === email))   throw new Error('邮箱已被注册')
    if (phone && users.find(u => u.phone === phone))   throw new Error('手机号已被注册')
    const user = {
      id: nextId(users),
      username, email, phone,
      password_hash: hashPassword(password),
      role, status,
      last_login_at: null,
      created_at: now(),
      updated_at: now(),
    }
    users.push(user)
    saveTable('users', users)
    return user
  },

  /** 验证登录，成功返回用户对象（不含密码），失败返回 null */
  authenticate(username, password) {
    const user = getTable('users').find(u => u.username === username)
    if (!user || user.status !== 'active') return null
    if (!verifyPassword(password, user.password_hash)) return null
    // 更新最近登录时间
    const users = getTable('users')
    const idx = users.findIndex(u => u.id === user.id)
    users[idx].last_login_at = now()
    users[idx].updated_at    = now()
    saveTable('users', users)
    const { password_hash, ...safe } = users[idx]
    return safe
  },

  /** 初始化演示账号（仅首次） */
  seedDemo() {
    if (getTable('users').length === 0) {
      this.create({ username: 'demo', email: 'demo@xinjing.ai', phone: '13800138000', password: '123456' })
      userProfilesDb.create({
        user_id: 1, nickname: '演示用户', gender: 'other',
        age_range: '18-24', education_level: '本科', occupation: '学生',
        emergency_contact: '', avatar_url: '',
      })
    }
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 2. user_profiles 用户档案表
// ─────────────────────────────────────────────────────────────────────────────
export const userProfilesDb = {
  findByUserId: (user_id) =>
    getTable('user_profiles').find(p => p.user_id === user_id) || null,

  create({ user_id, nickname = '', gender = '', age_range = '',
            education_level = '', occupation = '', emergency_contact = '', avatar_url = '' }) {
    const profiles = getTable('user_profiles')
    const profile = {
      id: nextId(profiles), user_id,
      nickname, gender, age_range, education_level,
      occupation, emergency_contact, avatar_url,
      created_at: now(), updated_at: now(),
    }
    profiles.push(profile)
    saveTable('user_profiles', profiles)
    return profile
  },

  update(user_id, fields) {
    const profiles = getTable('user_profiles')
    const idx = profiles.findIndex(p => p.user_id === user_id)
    if (idx < 0) return null
    Object.assign(profiles[idx], fields, { updated_at: now() })
    saveTable('user_profiles', profiles)
    return profiles[idx]
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 3. evaluation_sessions 评估会话表
// ─────────────────────────────────────────────────────────────────────────────
export const evaluationSessionsDb = {
  findByUserId: (user_id) =>
    getTable('evaluation_sessions')
      .filter(s => s.user_id === user_id)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at)),

  findById: (id) => getTable('evaluation_sessions').find(s => s.id === id) || null,

  create({ user_id, screening_type = 'full', used_modalities = [] }) {
    const sessions = getTable('evaluation_sessions')
    const session = {
      id: nextId(sessions),
      session_no: `SES${Date.now()}`,
      user_id, status: 'in_progress', screening_type,
      start_time: now(), end_time: null, duration_seconds: 0,
      used_modalities, missing_modalities: [],
      degraded_inference: false, confidence_score: null,
      overall_risk_level: null,
      created_at: now(), updated_at: now(),
    }
    sessions.push(session)
    saveTable('evaluation_sessions', sessions)
    return session
  },

  update(id, fields) {
    const sessions = getTable('evaluation_sessions')
    const idx = sessions.findIndex(s => s.id === id)
    if (idx < 0) return null
    Object.assign(sessions[idx], fields, { updated_at: now() })
    saveTable('evaluation_sessions', sessions)
    return sessions[idx]
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 4. session_context_info 评估背景信息表
// ─────────────────────────────────────────────────────────────────────────────
export const sessionContextDb = {
  findBySessionId: (session_id) =>
    getTable('session_context_info').find(r => r.session_id === session_id) || null,

  create({ session_id, recent_stress_level = 3, sleep_status = '', appetite_status = '',
            self_evaluation = '', social_avoidance_level = 0, remark = '' }) {
    const rows = getTable('session_context_info')
    const row = {
      id: nextId(rows), session_id,
      recent_stress_level, sleep_status, appetite_status,
      self_evaluation, social_avoidance_level, remark,
      created_at: now(),
    }
    rows.push(row)
    saveTable('session_context_info', rows)
    return row
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 5 & 6. questionnaire_templates + questionnaire_questions（只读种子数据）
// ─────────────────────────────────────────────────────────────────────────────
export const QUESTIONNAIRE_TEMPLATES = [
  { id: 1, code: 'PHQ-2',  name: 'PHQ-2 抑郁初筛量表',   description: '两题快速筛查', total_score_rule: 'sum', is_active: true },
  { id: 2, code: 'PHQ-9',  name: 'PHQ-9 抑郁症状量表',   description: '九题全面评估', total_score_rule: 'sum', is_active: true },
  { id: 3, code: 'SLEEP',  name: '匹兹堡睡眠质量指数',    description: 'PSQI 睡眠评估', total_score_rule: 'sum', is_active: true },
  { id: 4, code: 'STRESS', name: '压力感知量表（PSS-10）', description: '压力自评',     total_score_rule: 'sum', is_active: true },
]

// ─────────────────────────────────────────────────────────────────────────────
// 7. questionnaire_answers 问卷答案表
// ─────────────────────────────────────────────────────────────────────────────
export const questionnaireAnswersDb = {
  findBySession: (session_id) =>
    getTable('questionnaire_answers').filter(a => a.session_id === session_id),

  batchCreate(session_id, template_id, answers) {
    const rows = getTable('questionnaire_answers')
    const newRows = answers.map((ans, i) => ({
      id: nextId([...rows, ...newRows.slice(0, i)]),
      session_id, template_id,
      question_id: ans.question_id,
      answer_value: ans.answer_value,
      answer_score: ans.answer_score,
      created_at: now(),
    }))
    saveTable('questionnaire_answers', [...rows, ...newRows])
    return newRows
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 8. questionnaire_results 问卷结果表
// ─────────────────────────────────────────────────────────────────────────────
export const questionnaireResultsDb = {
  findBySession: (session_id) =>
    getTable('questionnaire_results').filter(r => r.session_id === session_id),

  create({ session_id, template_id, total_score, severity_level, dimension_scores = {} }) {
    const rows = getTable('questionnaire_results')
    const row = {
      id: nextId(rows), session_id, template_id,
      total_score, severity_level, dimension_scores,
      created_at: now(),
    }
    rows.push(row)
    saveTable('questionnaire_results', rows)
    return row
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 9. media_assets 媒体资源表
// ─────────────────────────────────────────────────────────────────────────────
export const mediaAssetsDb = {
  findBySession: (session_id) =>
    getTable('media_assets').filter(a => a.session_id === session_id),

  create({ session_id, media_type, file_url, file_name = '',
            file_size = 0, duration_seconds = 0, format = '', upload_status = 'uploaded' }) {
    const rows = getTable('media_assets')
    const row = {
      id: nextId(rows), session_id, media_type,
      file_url, file_name, file_size, duration_seconds, format,
      upload_status, created_at: now(),
    }
    rows.push(row)
    saveTable('media_assets', rows)
    return row
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 10. modality_quality_metrics 模态质量表
// ─────────────────────────────────────────────────────────────────────────────
export const modalityQualityDb = {
  findBySession: (session_id) =>
    getTable('modality_quality_metrics').filter(r => r.session_id === session_id),

  create({ session_id, modality, quality_score, issue_tags = [], metrics = {} }) {
    const rows = getTable('modality_quality_metrics')
    const row = { id: nextId(rows), session_id, modality, quality_score, issue_tags, metrics, created_at: now() }
    rows.push(row)
    saveTable('modality_quality_metrics', rows)
    return row
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 11. feature_snapshots 特征摘要表
// ─────────────────────────────────────────────────────────────────────────────
export const featureSnapshotsDb = {
  findBySession: (session_id) =>
    getTable('feature_snapshots').filter(r => r.session_id === session_id),

  create({ session_id, modality, feature_summary = {}, feature_file_url = '' }) {
    const rows = getTable('feature_snapshots')
    const row = { id: nextId(rows), session_id, modality, feature_summary, feature_file_url, created_at: now() }
    rows.push(row)
    saveTable('feature_snapshots', rows)
    return row
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 12. model_inference_results 模型推理结果表
// ─────────────────────────────────────────────────────────────────────────────
export const modelInferenceDb = {
  findBySession: (session_id) =>
    getTable('model_inference_results').find(r => r.session_id === session_id) || null,

  create({ session_id, model_name = 'xinjing-v1', fusion_strategy = 'weighted',
            face_score = null, voice_score = null, scale_score = null, text_score = null,
            fused_score, risk_level, confidence_score, modality_weights = {},
            missing_modalities = [], explanation = '' }) {
    const rows = getTable('model_inference_results')
    const row = {
      id: nextId(rows), session_id, model_name, fusion_strategy,
      face_score, voice_score, scale_score, text_score,
      fused_score, risk_level, confidence_score,
      modality_weights, missing_modalities, explanation,
      created_at: now(),
    }
    rows.push(row)
    saveTable('model_inference_results', rows)
    return row
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 13. reports 评估报告表
// ─────────────────────────────────────────────────────────────────────────────
export const reportsDb = {
  findByUserId: (user_id) =>
    getTable('reports')
      .filter(r => r.user_id === user_id)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at)),

  findBySessionId: (session_id) =>
    getTable('reports').find(r => r.session_id === session_id) || null,

  create({ session_id, user_id, report_type = 'auto', report_json = {}, report_pdf_url = '' }) {
    const rows = getTable('reports')
    const row = {
      id: nextId(rows), session_id, user_id, report_type,
      report_json, report_pdf_url,
      generated_at: now(), created_at: now(),
    }
    rows.push(row)
    saveTable('reports', rows)
    return row
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 14. intervention_recommendations 干预推荐表
// ─────────────────────────────────────────────────────────────────────────────
export const interventionDb = {
  findBySession: (session_id) =>
    getTable('intervention_recommendations').filter(r => r.session_id === session_id),

  create({ session_id, user_id, recommendation_type, priority = 2, reason = '', content = '' }) {
    const rows = getTable('intervention_recommendations')
    const row = {
      id: nextId(rows), session_id, user_id,
      recommendation_type, priority, reason, content,
      created_at: now(),
    }
    rows.push(row)
    saveTable('intervention_recommendations', rows)
    return row
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 15 & 16. chat_sessions + chat_messages 陪伴聊天表
// ─────────────────────────────────────────────────────────────────────────────
export const chatSessionsDb = {
  findByUserId: (user_id) =>
    getTable('chat_sessions')
      .filter(s => s.user_id === user_id)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at)),

  findById: (id) => getTable('chat_sessions').find(s => s.id === id) || null,

  create({ user_id, session_topic = '日常陪伴', evaluation_session_id = null }) {
    const sessions = getTable('chat_sessions')
    const session = {
      id: nextId(sessions), user_id, evaluation_session_id, session_topic,
      status: 'active', started_at: now(), ended_at: null,
      created_at: now(), updated_at: now(),
    }
    sessions.push(session)
    saveTable('chat_sessions', sessions)
    return session
  },

  close(id) {
    const sessions = getTable('chat_sessions')
    const idx = sessions.findIndex(s => s.id === id)
    if (idx >= 0) {
      sessions[idx].status   = 'ended'
      sessions[idx].ended_at = now()
      sessions[idx].updated_at = now()
      saveTable('chat_sessions', sessions)
    }
  },
}

export const chatMessagesDb = {
  findBySessionId: (chat_session_id) =>
    getTable('chat_messages')
      .filter(m => m.chat_session_id === chat_session_id)
      .sort((a, b) => new Date(a.created_at) - new Date(b.created_at)),

  create({ chat_session_id, sender_type, content, message_type = 'text' }) {
    const messages = getTable('chat_messages')
    const message = {
      id: nextId(messages), chat_session_id,
      sender_type, content, message_type,
      created_at: now(),
    }
    messages.push(message)
    saveTable('chat_messages', messages)
    return message
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 17. emergency_alerts 紧急预警表
// ─────────────────────────────────────────────────────────────────────────────
export const emergencyAlertsDb = {
  findByUserId: (user_id) =>
    getTable('emergency_alerts')
      .filter(a => a.user_id === user_id)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at)),

  create({ user_id, session_id = null, source_type, alert_title, alert_content, risk_level }) {
    const rows = getTable('emergency_alerts')
    const row = {
      id: nextId(rows), user_id, session_id, source_type,
      alert_title, alert_content, risk_level,
      is_handled: false, handled_at: null,
      created_at: now(),
    }
    rows.push(row)
    saveTable('emergency_alerts', rows)
    return row
  },

  markHandled(id) {
    const rows = getTable('emergency_alerts')
    const idx = rows.findIndex(r => r.id === id)
    if (idx >= 0) { rows[idx].is_handled = true; rows[idx].handled_at = now(); saveTable('emergency_alerts', rows) }
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 18. emotion_checkins 情绪打卡表
// ─────────────────────────────────────────────────────────────────────────────
export const emotionCheckinsDb = {
  findByUserId: (user_id) =>
    getTable('emotion_checkins')
      .filter(r => r.user_id === user_id)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at)),

  findRecent: (user_id, limit = 30) =>
    getTable('emotion_checkins')
      .filter(r => r.user_id === user_id)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, limit),

  create({ user_id, mood_score, stress_score, sleep_score, energy_score, note = '' }) {
    const rows = getTable('emotion_checkins')
    const row = {
      id: nextId(rows), user_id,
      mood_score, stress_score, sleep_score, energy_score, note,
      created_at: now(),
    }
    rows.push(row)
    saveTable('emotion_checkins', rows)
    return row
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 19. mood_calendar_records 心情日历记录表
// ─────────────────────────────────────────────────────────────────────────────
export const moodCalendarDb = {
  findByUserId: (user_id) =>
    getTable('mood_calendar_records').filter(r => r.user_id === user_id),

  findByDate: (user_id, record_date) =>
    getTable('mood_calendar_records').find(r => r.user_id === user_id && r.record_date === record_date) || null,

  /** 插入或更新同一天的记录 */
  upsert({ user_id, record_date, mood_key, diary_text = '', weather_key = '' }) {
    const rows = getTable('mood_calendar_records')
    const idx  = rows.findIndex(r => r.user_id === user_id && r.record_date === record_date)
    if (idx >= 0) {
      Object.assign(rows[idx], { mood_key, diary_text, weather_key, updated_at: now() })
      saveTable('mood_calendar_records', rows)
      return rows[idx]
    }
    const row = {
      id: nextId(rows), user_id, record_date,
      mood_key, diary_text, weather_key,
      created_at: now(), updated_at: now(),
    }
    rows.push(row)
    saveTable('mood_calendar_records', rows)
    return row
  },

  delete(user_id, record_date) {
    const rows = getTable('mood_calendar_records').filter(
      r => !(r.user_id === user_id && r.record_date === record_date)
    )
    saveTable('mood_calendar_records', rows)
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 20. trend_snapshots 趋势快照表
// ─────────────────────────────────────────────────────────────────────────────
export const trendSnapshotsDb = {
  findByUserId: (user_id) =>
    getTable('trend_snapshots')
      .filter(r => r.user_id === user_id)
      .sort((a, b) => new Date(b.snapshot_date) - new Date(a.snapshot_date)),

  upsert({ user_id, snapshot_date, latest_risk_level = null,
            avg_mood_score = null, avg_stress_score = null,
            avg_sleep_score = null, phq9_latest_score = null }) {
    const rows = getTable('trend_snapshots')
    const idx  = rows.findIndex(r => r.user_id === user_id && r.snapshot_date === snapshot_date)
    const data = { user_id, snapshot_date, latest_risk_level, avg_mood_score, avg_stress_score, avg_sleep_score, phq9_latest_score }
    if (idx >= 0) {
      Object.assign(rows[idx], data)
      saveTable('trend_snapshots', rows)
      return rows[idx]
    }
    const row = { id: nextId(rows), ...data, created_at: now() }
    rows.push(row)
    saveTable('trend_snapshots', rows)
    return row
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// 初始化种子数据（首次运行时写入演示账号）
// ─────────────────────────────────────────────────────────────────────────────
usersDb.seedDemo()
