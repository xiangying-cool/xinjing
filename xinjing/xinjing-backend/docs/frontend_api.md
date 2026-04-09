# 前端接口对接说明

> 更新时间：2026-03-15  


## 1. 通用规则

---

## 2. Health

### 2.1 `GET /api/v1/health`

- 前端要传：
  - 无路径参数
  - 无查询参数
  - 无请求体
- 后端返回（200）：

```json
{
  "status": "ok",
  "time": "2026-03-15T08:00:00+00:00"
}
```

### 2.2 `GET /api/v1/health/db`

- 前端要传：无
- 后端返回：
  - 数据库正常（200）：

```json
{
  "status": "ok",
  "database": "connected"
}
```

  - 数据库异常（200，业务状态 error）：

```json
{
  "status": "error",
  "database": "disconnected",
  "detail": "OperationalError"
}
```

### 2.3 `GET /health`（全局）

- 前端要传：无
- 后端返回（200）：

```json
{
  "status": "ok"
}
```

---

## 3. Auth

### 3.1 `POST /auth/register`

- 前端要传（JSON）：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `username` | string | 是 | 3~50 位，唯一 |
| `password` | string | 是 | 6~128 位 |
| `confirm_password` | string | 否 | 传了必须等于 `password` |
| `email` | string | 否 | 不传则后端自动生成 `<username>@xinjing.local` |
| `phone` | string | 否 | 传了则要求唯一 |
| `nickname` | string | 否 | 用户昵称 |
| `gender` | string | 否 | 性别 |
| `age_range` | string | 否 | 年龄段 |

- 后端返回（201）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | int | 用户 ID |
| `username` | string | 用户名 |
| `email` | string | 邮箱 |
| `phone` | string \| null | 手机号 |
| `role` | string | 角色（默认 `user`） |
| `status` | string | 状态（默认 `active`） |
| `last_login_at` | string \| null | 最近登录时间 |

- 常见错误：
  - `400`：用户名/邮箱/手机号已存在
  - `422`：字段格式校验失败

### 3.2 `POST /auth/login`

- 前端要传（JSON）：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `username` | string | 是 | 用户名或邮箱 |
| `password` | string | 是 | 密码 |

- 后端返回（200）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `access_token` | string | JWT token |
| `token_type` | string | 固定 `bearer` |
| `user` | object | 用户信息，字段同 `register` 返回 |

- 常见错误：
  - `401`：账号或密码错误
  - `403`：用户被禁用

---

<!-- ## 4. Users

### 4.1 `GET /users/{user_id}/profile`这部分暂时未实现

- 前端要传：
  - 路径参数：`user_id`（int）
- 后端返回（200）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | int | 档案 ID |
| `user_id` | int | 用户 ID |
| `nickname` | string \| null | 昵称 |
| `gender` | string \| null | 性别 |
| `age_range` | string \| null | 年龄段 |
| `education_level` | string \| null | 学历 |
| `occupation` | string \| null | 职业 |
| `emergency_contact` | string \| null | 紧急联系人 |
| `avatar_url` | string \| null | 头像地址 |
| `created_at` | string | 创建时间 |
| `updated_at` | string | 更新时间 |

说明：如果该用户还没有档案，后端会自动创建默认档案再返回。

### 4.2 `PUT /users/{user_id}/profile`

- 前端要传：
  - 路径参数：`user_id`
  - JSON（可部分传）：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `nickname` | string | 否 | 最长 50 |
| `gender` | string | 否 | 最长 20 |
| `age_range` | string | 否 | 最长 20 |
| `education_level` | string | 否 | 最长 30 |
| `occupation` | string | 否 | 最长 50 |
| `emergency_contact` | string | 否 | 最长 100 |
| `avatar_url` | string | 否 | 最长 255 |

- 后端返回（200）：更新后的完整档案对象（字段同 4.1） -->

---

## 5. Evaluations（辅助筛查）

### 5.1 `GET /evaluations/sessions`

- 前端要传（query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `user_id` | int | 否 | 按用户过滤 |
| `limit` | int | 否 | 默认 50，范围 1~200 |

- 后端返回（200）：会话数组，每项字段：
  - `id`, `session_no`, `user_id`, `status`, `screening_type`
  - `start_time`, `end_time`, `duration_seconds`
  - `used_modalities`, `missing_modalities`, `degraded_inference`
  - `confidence_score`, `overall_risk_level`, `created_at`, `updated_at`

### 5.2 `GET /evaluations/sessions/{session_id}`

- 前端要传：路径参数 `session_id`
- 后端返回（200）：

```json
{
  "session": { "...": "会话对象，字段同 5.1 单项" },
  "context": {
    "id": 1,
    "session_id": 10,
    "recent_stress_level": "medium",
    "sleep_status": "normal",
    "appetite_status": "normal",
    "self_evaluation": "stable",
    "social_avoidance_level": "low",
    "remark": "xxx",
    "created_at": "2026-03-15T08:00:00"
  }
}
```

### 5.3 `POST /evaluations/sessions`

- 前端要传（JSON）：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `user_id` | int \| null | 否 | 用户 ID |
| `screening_type` | string | 是 | `phq9/sds/ais/pss` |
| `used_modalities` | string[] | 否 | 使用模态 |
| `missing_modalities` | string[] | 否 | 缺失模态 |

- 后端返回（201）：
  - `session_id`, `session_no`, `status`, `screening_type`, `start_time`

### 5.4 `POST /evaluations/sessions/{session_id}/submit`

- 前端要传：
  - 路径参数：`session_id`
  - JSON：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `template_code` | string | 是 | `phq9/sds/ais/pss` |
| `answers` | array | 是 | 每项含 `question_no`(int), `answer_value`(int) |
| `context` | object | 否 | 背景信息（压力/睡眠/食欲等） |
| `confidence_score` | float | 否 | 置信度 |

- 后端返回（200）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `report_id` | int | 生成的报告 ID |
| `session_id` | int | 会话 ID |
| `total_score` | int | 总分 |
| `risk_level` | string | 风险等级 |
| `confidence_score` | float \| null | 置信度 |

后端在该接口内部会自动做：

- 写入问卷答案、问卷结果、背景信息
- 生成报告 `report_json`
- 生成干预建议
- PHQ-9 第9题>0时写入预警

---

## 6. Reports（需要 Bearer Token）

> 所有接口按当前登录用户隔离数据。

### 6.1 `GET /reports`

- 前端要传：
  - Header：`Authorization: Bearer <token>`
  - Query：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `limit` | int | 否 | 默认 50，范围 1~200 |
| `user_id` | int | 否 | 允许传，但必须等于当前登录用户，否则 403 |

- 后端返回（200）：报告数组，每项字段：
  - `id`, `session_id`, `user_id`, `report_type`
  - `report_json`, `report_pdf_url`, `generated_at`, `created_at`

### 6.2 `GET /reports/alerts`

- 前端要传：
  - Header：Bearer token
  - Query：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `user_id` | int | 否 | 必须等于当前用户 |
| `session_id` | int | 否 | 按会话过滤 |

- 后端返回（200）：预警数组，每项字段：
  - `id`, `user_id`, `session_id`, `source_type`
  - `alert_title`, `alert_content`, `risk_level`
  - `is_handled`, `handled_at`, `created_at`

### 6.3 `GET /reports/by-session/{session_id}`

- 前端要传：Bearer token + 路径参数 `session_id`
- 后端返回（200）：单个 `ReportOut`
- 常见错误：`404`（不存在或不是当前用户会话）

### 6.4 `GET /reports/{report_id}`

- 前端要传：Bearer token + 路径参数 `report_id`
- 后端返回（200）：单个 `ReportOut`

### 6.5 `GET /reports/{report_id}/frontend`

- 前端要传：Bearer token + 路径参数 `report_id`
- 后端返回（200）：`report_json`（给前端展示的结构化报告）

### 6.6 `GET /reports/session/{session_id}/recommendations`

- 前端要传：Bearer token + 路径参数 `session_id`
- 后端返回（200）：建议数组，每项字段：
  - `id`, `session_id`, `user_id`, `recommendation_type`
  - `priority`, `reason`, `content`, `created_at`

---

## 7. Mood Calendar（需要 Bearer Token）

> 所有接口按当前登录用户隔离数据，`user_id` 可不传。

### 7.1 `GET /mood-calendar/checkins`

- 前端要传：
  - Header：Bearer token
  - Query：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `limit` | int | 否 | 默认 30，范围 1~365 |
| `user_id` | int | 否 | 传了必须是当前用户 |

- 后端返回（200）：情绪打卡数组，每项字段：
  - `id`, `user_id`, `mood_score`, `stress_score`
  - `sleep_score`, `energy_score`, `note`, `created_at`

### 7.2 `POST /mood-calendar/checkins`

- 前端要传：
  - Header：Bearer token
  - JSON：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `mood_score` | int | 是 | 1~5 |
| `stress_score` | int | 是 | 1~5 |
| `sleep_score` | int | 是 | 1~5 |
| `energy_score` | int | 是 | 1~5 |
| `note` | string | 否 | 最长 255 |
| `user_id` | int | 否 | 可省略，后端自动取当前用户 |

- 后端返回（201）：单条 `EmotionCheckinOut`

### 7.3 `GET /mood-calendar/trends`

- 前端要传：
  - Header：Bearer token
  - Query：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `limit` | int | 否 | 默认 90，范围 1~366 |
| `user_id` | int | 否 | 传了必须是当前用户 |

- 后端返回（200）：趋势快照数组，每项字段：
  - `id`, `user_id`, `snapshot_date`, `latest_risk_level`
  - `avg_mood_score`, `avg_stress_score`, `avg_sleep_score`
  - `phq9_latest_score`, `created_at`

### 7.4 `PUT /mood-calendar/trends/{snapshot_date}`

- 前端要传：
  - Header：Bearer token
  - 路径参数：`snapshot_date`（`YYYY-MM-DD`）
  - JSON：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `latest_risk_level` | string \| null | 否 | 风险等级文本 |
| `avg_mood_score` | int \| null | 否 | 1~5 |
| `avg_stress_score` | int \| null | 否 | 1~5 |
| `avg_sleep_score` | int \| null | 否 | 1~5 |
| `phq9_latest_score` | int \| null | 否 | 0~27 |
| `user_id` | int | 否 | 可省略 |

- 后端返回（200）：`TrendSnapshotOut`（upsert 后最新数据）

### 7.5 `PUT /mood-calendar/{record_date}`

- 前端要传：
  - Header：Bearer token
  - 路径参数：`record_date`（`YYYY-MM-DD`）
  - JSON：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `mood_key` | string | 是 | `sunny/partly/cloudy/rainy/stormy` |
| `diary_text` | string \| null | 否 | 最长 300 |
| `weather_key` | string \| null | 否 | 最长 20 |
| `user_id` | int | 否 | 可省略 |

- 后端返回（200）：`MoodCalendarRecordOut`

### 7.6 `GET /mood-calendar`

- 前端要传：
  - Header：Bearer token
  - Query：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `month` | string | 否 | `YYYY-MM`，传了则按月份过滤 |
| `user_id` | int | 否 | 传了必须是当前用户 |

- 后端返回（200）：日历记录数组（`MoodCalendarRecordOut[]`）

### 7.7 `GET /mood-calendar/{record_date}`

- 前端要传：Bearer token + 路径参数 `record_date`
- 可选 query：`user_id`（若传必须为当前用户）
- 后端返回（200）：单条 `MoodCalendarRecordOut`

### 7.8 `DELETE /mood-calendar/{record_date}`

- 前端要传：Bearer token + 路径参数 `record_date`
- 可选 query：`user_id`（若传必须为当前用户）
- 后端返回：`204` 无 body

---

## 8. Chat

### 8.1 `POST /chat/sessions`

- 前端要传（JSON）：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `user_id` | int | 是 | 用户 ID |
| `session_topic` | string | 否 | 最长 100 |
| `evaluation_session_id` | int \| null | 否 | 关联筛查会话 |
| `mode` | string | 否 | 传了可用于自动填充 `session_topic` |

- 后端返回（201）：`ChatSessionOut`

### 8.2 `GET /chat/sessions`

- 前端要传（query）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `user_id` | int | 否 | 按用户过滤 |
| `limit` | int | 否 | 默认 50，范围 1~200 |

- 后端返回（200）：`ChatSessionOut[]`

### 8.3 `GET /chat/sessions/{session_id}`

- 前端要传：路径参数 `session_id`
- 后端返回（200）：`ChatSessionOut`

### 8.4 `PATCH /chat/sessions/{session_id}/close`

- 前端要传：路径参数 `session_id`
- 后端返回（200）：关闭后的 `ChatSessionOut`（`status=ended`）

### 8.5 `POST /chat/sessions/{session_id}/messages`

- 前端要传：
  - 路径参数：`session_id`
  - JSON：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `content` | string | 是 | 不能为空 |
| `message_type` | string | 否 | 默认 `text` |
| `sender_type` | string | 否 | `user/agent/system` |
| `role` | string | 否 | 兼容字段，`assistant` 会映射成 `agent` |

- 后端返回（200）：该会话全部消息数组 `ChatMessageOut[]`
- 额外行为：若你发的是 `user` 消息，后端会自动追加一条 `agent` 回复

### 8.6 `GET /chat/sessions/{session_id}/messages`

- 前端要传：路径参数 `session_id`
- 后端返回（200）：`ChatMessageOut[]`

---

## 9. 前端最小调用链建议

### 9.1 登录后

1. `POST /auth/login` 获取 `access_token` 和 `user.id`
2. 把 token 存到本地，并给后续请求自动加 `Authorization`

### 9.2 辅助筛查页

1. `POST /evaluations/sessions`
2. `POST /evaluations/sessions/{session_id}/submit`
3. `GET /reports/{report_id}/frontend`

### 9.3 情绪日历页

1. `GET /mood-calendar?month=YYYY-MM`
2. `PUT /mood-calendar/{record_date}`（新增/更新）
3. `GET /mood-calendar/trends?limit=90`

### 9.4 数据分析/报告页

1. `GET /reports?limit=50`
2. `GET /reports/{report_id}/frontend`
3. `GET /reports/session/{session_id}/recommendations`
4. `GET /reports/alerts`
