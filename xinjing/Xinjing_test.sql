SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP DATABASE IF EXISTS xinjing_test;
CREATE DATABASE xinjing_test
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
USE xinjing_test;

CREATE TABLE users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户编号',
    username VARCHAR(64) NOT NULL COMMENT '用户名',
    email VARCHAR(128) NOT NULL COMMENT '邮箱',
    phone VARCHAR(32) NOT NULL COMMENT '手机号',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    role VARCHAR(32) NOT NULL DEFAULT 'user' COMMENT '角色',
    status VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT '状态',
    last_login_at DATETIME NULL COMMENT '最近登录时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_users_username (username),
    UNIQUE KEY uk_users_email (email),
    UNIQUE KEY uk_users_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

CREATE TABLE user_profiles (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '档案编号',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户编号',
    nickname VARCHAR(64) NULL COMMENT '昵称',
    gender VARCHAR(16) NULL COMMENT '性别',
    age_range VARCHAR(32) NULL COMMENT '年龄段',
    education_level VARCHAR(64) NULL COMMENT '学历',
    occupation VARCHAR(128) NULL COMMENT '职业',
    emergency_contact VARCHAR(128) NULL COMMENT '紧急联系人',
    avatar_url VARCHAR(255) NULL COMMENT '头像地址',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_profiles_user_id (user_id),
    CONSTRAINT fk_user_profiles_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户档案表';

CREATE TABLE evaluation_sessions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '会话编号',
    session_no VARCHAR(64) NOT NULL COMMENT '会话流水号',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户编号',
    status VARCHAR(32) NOT NULL DEFAULT 'completed' COMMENT '会话状态',
    screening_type VARCHAR(64) NULL COMMENT '筛查类型',
    start_time DATETIME NULL COMMENT '开始时间',
    end_time DATETIME NULL COMMENT '结束时间',
    duration_seconds INT NULL COMMENT '持续时长（秒）',
    used_modalities JSON NULL COMMENT '使用模态',
    missing_modalities JSON NULL COMMENT '缺失模态',
    degraded_inference TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否降级推理',
    confidence_score DECIMAL(5,4) NULL COMMENT '置信度',
    overall_risk_level VARCHAR(32) NULL COMMENT '总体风险等级',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_evaluation_sessions_session_no (session_no),
    KEY idx_evaluation_sessions_user_id (user_id),
    CONSTRAINT fk_evaluation_sessions_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评估会话表';

CREATE TABLE session_context_info (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '记录编号',
    session_id BIGINT UNSIGNED NOT NULL COMMENT '会话编号',
    recent_stress_level VARCHAR(32) NULL COMMENT '近期压力等级',
    sleep_status VARCHAR(64) NULL COMMENT '睡眠状态',
    appetite_status VARCHAR(64) NULL COMMENT '食欲状态',
    self_evaluation VARCHAR(255) NULL COMMENT '自我评价',
    social_avoidance_level VARCHAR(32) NULL COMMENT '社交回避程度',
    remark VARCHAR(500) NULL COMMENT '备注',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_session_context_info_session_id (session_id),
    CONSTRAINT fk_session_context_info_session_id FOREIGN KEY (session_id) REFERENCES evaluation_sessions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评估背景信息表';

CREATE TABLE questionnaire_templates (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '模板编号',
    code VARCHAR(64) NOT NULL COMMENT '问卷编码',
    name VARCHAR(128) NOT NULL COMMENT '问卷名称',
    description VARCHAR(500) NULL COMMENT '描述',
    total_score_rule VARCHAR(255) NULL COMMENT '总分规则',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_questionnaire_templates_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问卷模板表';

CREATE TABLE questionnaire_questions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '题目编号',
    template_id BIGINT UNSIGNED NOT NULL COMMENT '模板编号',
    question_no INT NOT NULL COMMENT '题号',
    question_text VARCHAR(500) NOT NULL COMMENT '题目内容',
    question_type VARCHAR(32) NOT NULL COMMENT '题目类型',
    options_json JSON NULL COMMENT '题目选项配置',
    score_mapping JSON NULL COMMENT '分值映射',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_questionnaire_questions_template_question_no (template_id, question_no),
    CONSTRAINT fk_questionnaire_questions_template_id FOREIGN KEY (template_id) REFERENCES questionnaire_templates (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问卷题目表';

CREATE TABLE questionnaire_answers (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '答案编号',
    session_id BIGINT UNSIGNED NOT NULL COMMENT '会话编号',
    template_id BIGINT UNSIGNED NOT NULL COMMENT '模板编号',
    question_id BIGINT UNSIGNED NOT NULL COMMENT '题目编号',
    answer_value VARCHAR(255) NULL COMMENT '答案值',
    answer_score DECIMAL(8,2) NULL COMMENT '答案得分',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_questionnaire_answers_unique (session_id, template_id, question_id),
    KEY idx_questionnaire_answers_template_id (template_id),
    KEY idx_questionnaire_answers_question_id (question_id),
    CONSTRAINT fk_questionnaire_answers_session_id FOREIGN KEY (session_id) REFERENCES evaluation_sessions (id),
    CONSTRAINT fk_questionnaire_answers_template_id FOREIGN KEY (template_id) REFERENCES questionnaire_templates (id),
    CONSTRAINT fk_questionnaire_answers_question_id FOREIGN KEY (question_id) REFERENCES questionnaire_questions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问卷答案表';

CREATE TABLE questionnaire_results (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '结果编号',
    session_id BIGINT UNSIGNED NOT NULL COMMENT '会话编号',
    template_id BIGINT UNSIGNED NOT NULL COMMENT '模板编号',
    total_score DECIMAL(8,2) NULL COMMENT '总分',
    severity_level VARCHAR(32) NULL COMMENT '严重程度',
    dimension_scores JSON NULL COMMENT '维度得分',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_questionnaire_results_unique (session_id, template_id),
    CONSTRAINT fk_questionnaire_results_session_id FOREIGN KEY (session_id) REFERENCES evaluation_sessions (id),
    CONSTRAINT fk_questionnaire_results_template_id FOREIGN KEY (template_id) REFERENCES questionnaire_templates (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问卷结果表';

CREATE TABLE media_assets (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '资源编号',
    session_id BIGINT UNSIGNED NOT NULL COMMENT '会话编号',
    media_type VARCHAR(32) NOT NULL COMMENT '媒体类型',
    file_url VARCHAR(255) NOT NULL COMMENT '文件地址',
    file_name VARCHAR(255) NOT NULL COMMENT '文件名',
    file_size BIGINT NULL COMMENT '文件大小（字节）',
    duration_seconds INT NULL COMMENT '时长（秒）',
    format VARCHAR(32) NULL COMMENT '格式',
    upload_status VARCHAR(32) NOT NULL DEFAULT 'uploaded' COMMENT '上传状态',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_media_assets_session_id (session_id),
    CONSTRAINT fk_media_assets_session_id FOREIGN KEY (session_id) REFERENCES evaluation_sessions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='媒体资源表';

CREATE TABLE modality_quality_metrics (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '质量记录编号',
    session_id BIGINT UNSIGNED NOT NULL COMMENT '会话编号',
    modality VARCHAR(32) NOT NULL COMMENT '模态类型',
    quality_score DECIMAL(5,2) NULL COMMENT '质量分数',
    issue_tags JSON NULL COMMENT '问题标签',
    metrics JSON NULL COMMENT '质量指标',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_modality_quality_metrics_session_id (session_id),
    CONSTRAINT fk_modality_quality_metrics_session_id FOREIGN KEY (session_id) REFERENCES evaluation_sessions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模态质量表';

CREATE TABLE feature_snapshots (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '特征编号',
    session_id BIGINT UNSIGNED NOT NULL COMMENT '会话编号',
    modality VARCHAR(32) NOT NULL COMMENT '模态类型',
    feature_summary JSON NULL COMMENT '特征摘要',
    feature_file_url VARCHAR(255) NULL COMMENT '特征文件地址',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_feature_snapshots_session_id (session_id),
    CONSTRAINT fk_feature_snapshots_session_id FOREIGN KEY (session_id) REFERENCES evaluation_sessions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='特征摘要表';

CREATE TABLE model_inference_results (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '结果编号',
    session_id BIGINT UNSIGNED NOT NULL COMMENT '会话编号',
    model_name VARCHAR(128) NOT NULL COMMENT '模型名称',
    fusion_strategy VARCHAR(64) NULL COMMENT '融合策略',
    face_score DECIMAL(8,2) NULL COMMENT '面部分数',
    voice_score DECIMAL(8,2) NULL COMMENT '语音分数',
    scale_score DECIMAL(8,2) NULL COMMENT '量表分数',
    text_score DECIMAL(8,2) NULL COMMENT '文本分数',
    fused_score DECIMAL(8,2) NULL COMMENT '融合总分',
    risk_level VARCHAR(32) NULL COMMENT '风险等级',
    confidence_score DECIMAL(5,4) NULL COMMENT '置信度',
    modality_weights JSON NULL COMMENT '模态权重',
    missing_modalities JSON NULL COMMENT '缺失模态',
    explanation JSON NULL COMMENT '解释信息',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_model_inference_results_session_id (session_id),
    CONSTRAINT fk_model_inference_results_session_id FOREIGN KEY (session_id) REFERENCES evaluation_sessions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模型推理结果表';

CREATE TABLE reports (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '报告编号',
    session_id BIGINT UNSIGNED NOT NULL COMMENT '会话编号',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户编号',
    report_type VARCHAR(32) NOT NULL COMMENT '报告类型',
    report_json JSON NULL COMMENT '报告JSON',
    report_pdf_url VARCHAR(255) NULL COMMENT 'PDF地址',
    generated_at DATETIME NULL COMMENT '生成时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_reports_session_id (session_id),
    KEY idx_reports_user_id (user_id),
    CONSTRAINT fk_reports_session_id FOREIGN KEY (session_id) REFERENCES evaluation_sessions (id),
    CONSTRAINT fk_reports_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评估报告表';

CREATE TABLE intervention_recommendations (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '推荐编号',
    session_id BIGINT UNSIGNED NOT NULL COMMENT '会话编号',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户编号',
    recommendation_type VARCHAR(64) NOT NULL COMMENT '推荐类型',
    priority VARCHAR(16) NULL COMMENT '优先级',
    reason VARCHAR(500) NULL COMMENT '推荐原因',
    content TEXT NULL COMMENT '推荐内容',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_intervention_recommendations_session_id (session_id),
    KEY idx_intervention_recommendations_user_id (user_id),
    CONSTRAINT fk_intervention_recommendations_session_id FOREIGN KEY (session_id) REFERENCES evaluation_sessions (id),
    CONSTRAINT fk_intervention_recommendations_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='干预推荐表';

CREATE TABLE chat_sessions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '会话编号',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户编号',
    evaluation_session_id BIGINT UNSIGNED NULL COMMENT '关联评估会话编号',
    session_topic VARCHAR(128) NULL COMMENT '会话主题',
    status VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT '会话状态',
    started_at DATETIME NULL COMMENT '开始时间',
    ended_at DATETIME NULL COMMENT '结束时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_chat_sessions_user_id (user_id),
    KEY idx_chat_sessions_evaluation_session_id (evaluation_session_id),
    CONSTRAINT fk_chat_sessions_user_id FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_chat_sessions_evaluation_session_id FOREIGN KEY (evaluation_session_id) REFERENCES evaluation_sessions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='陪伴聊天会话表';

CREATE TABLE chat_messages (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '消息编号',
    chat_session_id BIGINT UNSIGNED NOT NULL COMMENT '聊天会话编号',
    sender_type VARCHAR(32) NOT NULL COMMENT '发送方',
    content TEXT NOT NULL COMMENT '消息内容',
    message_type VARCHAR(32) NOT NULL DEFAULT 'text' COMMENT '消息类型',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_chat_messages_chat_session_id (chat_session_id),
    CONSTRAINT fk_chat_messages_chat_session_id FOREIGN KEY (chat_session_id) REFERENCES chat_sessions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='陪伴聊天消息表';

CREATE TABLE emergency_alerts (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '预警编号',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户编号',
    session_id BIGINT UNSIGNED NOT NULL COMMENT '会话编号',
    source_type VARCHAR(32) NOT NULL COMMENT '预警来源',
    alert_title VARCHAR(255) NOT NULL COMMENT '预警标题',
    alert_content TEXT NULL COMMENT '预警内容',
    risk_level VARCHAR(32) NOT NULL COMMENT '风险等级',
    is_handled TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已处理',
    handled_at DATETIME NULL COMMENT '处理时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_emergency_alerts_user_id (user_id),
    KEY idx_emergency_alerts_session_id (session_id),
    CONSTRAINT fk_emergency_alerts_user_id FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_emergency_alerts_session_id FOREIGN KEY (session_id) REFERENCES evaluation_sessions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='紧急预警表';

CREATE TABLE emotion_checkins (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '打卡编号',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户编号',
    mood_score TINYINT NULL COMMENT '心情评分',
    stress_score TINYINT NULL COMMENT '压力评分',
    sleep_score TINYINT NULL COMMENT '睡眠评分',
    energy_score TINYINT NULL COMMENT '精力评分',
    note VARCHAR(500) NULL COMMENT '备注',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_emotion_checkins_user_id (user_id),
    CONSTRAINT fk_emotion_checkins_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='情绪打卡表';

CREATE TABLE mood_calendar_records (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '记录编号',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户编号',
    record_date DATE NOT NULL COMMENT '记录日期',
    mood_key VARCHAR(32) NULL COMMENT '心情标识',
    diary_text TEXT NULL COMMENT '日记内容',
    weather_key VARCHAR(32) NULL COMMENT '天气标识',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_mood_calendar_records_user_date (user_id, record_date),
    CONSTRAINT fk_mood_calendar_records_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='心情日历记录表';

CREATE TABLE trend_snapshots (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '快照编号',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户编号',
    snapshot_date DATE NOT NULL COMMENT '快照日期',
    latest_risk_level VARCHAR(32) NULL COMMENT '最新风险等级',
    avg_mood_score DECIMAL(5,2) NULL COMMENT '平均心情评分',
    avg_stress_score DECIMAL(5,2) NULL COMMENT '平均压力评分',
    avg_sleep_score DECIMAL(5,2) NULL COMMENT '平均睡眠评分',
    phq9_latest_score DECIMAL(8,2) NULL COMMENT '最新PHQ9得分',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_trend_snapshots_user_date (user_id, snapshot_date),
    CONSTRAINT fk_trend_snapshots_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='趋势快照表';

INSERT INTO users (id, username, email, phone, password_hash, role, status, last_login_at, created_at, updated_at) VALUES
(1, 'zhangsan', 'zhangsan@example.com', '13800000001', '$2y$10$demo_hash_user_1', 'user', 'active', '2026-03-10 09:12:00', '2026-02-20 10:00:00', '2026-03-10 09:12:00'),
(2, 'lisi', 'lisi@example.com', '13800000002', '$2y$10$demo_hash_user_2', 'user', 'active', '2026-03-09 20:30:00', '2026-02-25 11:20:00', '2026-03-09 20:30:00'),
(3, 'admin01', 'admin@example.com', '13800000003', '$2y$10$demo_hash_admin', 'admin', 'active', '2026-03-11 08:00:00', '2026-02-18 08:30:00', '2026-03-11 08:00:00');

INSERT INTO user_profiles (id, user_id, nickname, gender, age_range, education_level, occupation, emergency_contact, avatar_url, created_at, updated_at) VALUES
(1, 1, '小张', '男', '18-24', '本科', '大学生', '母亲 13900000001', 'https://cdn.example.com/avatar/u1.png', '2026-02-20 10:05:00', '2026-02-20 10:05:00'),
(2, 2, '小李', '女', '25-34', '硕士', '产品经理', '配偶 13900000002', 'https://cdn.example.com/avatar/u2.png', '2026-02-25 11:25:00', '2026-02-25 11:25:00'),
(3, 3, '系统管理员', '未知', '35-44', '本科', '管理员', '值班电话 13900000003', 'https://cdn.example.com/avatar/admin.png', '2026-02-18 08:35:00', '2026-02-18 08:35:00');

INSERT INTO evaluation_sessions (id, session_no, user_id, status, screening_type, start_time, end_time, duration_seconds, used_modalities, missing_modalities, degraded_inference, confidence_score, overall_risk_level, created_at, updated_at) VALUES
(1, 'ES202603100001', 1, 'completed', 'depression_screening', '2026-03-10 09:00:00', '2026-03-10 09:15:20', 920, '["face", "voice", "scale", "text"]', '[]', 0, 0.9230, 'medium', '2026-03-10 09:00:00', '2026-03-10 09:15:20'),
(2, 'ES202603090001', 2, 'completed', 'stress_sleep_screening', '2026-03-09 20:00:00', '2026-03-09 20:08:30', 510, '["voice", "scale"]', '["face"]', 1, 0.8640, 'low', '2026-03-09 20:00:00', '2026-03-09 20:08:30'),
(3, 'ES202603110001', 1, 'completed', 'followup_screening', '2026-03-11 19:00:00', '2026-03-11 19:12:40', 760, '["face", "scale"]', '["voice", "text"]', 1, 0.8120, 'high', '2026-03-11 19:00:00', '2026-03-11 19:12:40');

INSERT INTO session_context_info (id, session_id, recent_stress_level, sleep_status, appetite_status, self_evaluation, social_avoidance_level, remark, created_at) VALUES
(1, 1, 'high', 'late_sleep', 'decreased', '最近状态不太稳定', 'medium', '临近考试，焦虑增加', '2026-03-10 09:02:00'),
(2, 2, 'medium', 'light_sleep', 'normal', '工作压力可控', 'low', '连续加班后有疲惫感', '2026-03-09 20:01:00'),
(3, 3, 'very_high', 'insomnia', 'decreased', '最近明显低落', 'high', '需要重点关注自伤风险', '2026-03-11 19:01:30');

INSERT INTO questionnaire_templates (id, code, name, description, total_score_rule, is_active, created_at) VALUES
(1, 'phq9', 'PHQ-9 抑郁初筛', '前端筛查页使用：PHQ-9，9题，0-3分', 'sum(9 questions, each 0-3), max 27', 1, '2026-02-01 10:00:00'),
(2, 'sds', 'SDS 抑郁自评量表', '前端筛查页使用：SDS，20题，1-4分（含反向计分）', 'raw_sum_with_reverse * 1.25, max 100', 1, '2026-02-01 10:05:00'),
(3, 'ais', 'AIS 失眠量表', '前端筛查页使用：AIS，8题，0-4分', 'sum(8 questions, each 0-4), max 32', 1, '2026-02-01 10:10:00'),
(4, 'pss', 'PSS 压力感知量表', '前端筛查页使用：PSS，10题，0-4分（含反向计分）', 'sum(10 questions with reverse items), max 40', 1, '2026-02-01 10:15:00');

INSERT INTO questionnaire_questions (id, template_id, question_no, question_text, question_type, options_json, score_mapping, created_at) VALUES
-- PHQ-9 (9)
(1, 1, 1, '做事时提不起劲儿或没有兴趣', 'single_choice', '[{"label":"完全没有","value":0,"sub":"0天"},{"label":"有几天","value":1,"sub":"1–6天"},{"label":"超过一半时间","value":2,"sub":"7–11天"},{"label":"几乎天天","value":3,"sub":"12–14天"}]', '{"0":0,"1":1,"2":2,"3":3}', '2026-02-01 10:20:00'),
(2, 1, 2, '感到心情低落、沮丧或绝望', 'single_choice', '[{"label":"完全没有","value":0,"sub":"0天"},{"label":"有几天","value":1,"sub":"1–6天"},{"label":"超过一半时间","value":2,"sub":"7–11天"},{"label":"几乎天天","value":3,"sub":"12–14天"}]', '{"0":0,"1":1,"2":2,"3":3}', '2026-02-01 10:20:10'),
(3, 1, 3, '入睡困难、睡不安稳或睡眠过多', 'single_choice', '[{"label":"完全没有","value":0,"sub":"0天"},{"label":"有几天","value":1,"sub":"1–6天"},{"label":"超过一半时间","value":2,"sub":"7–11天"},{"label":"几乎天天","value":3,"sub":"12–14天"}]', '{"0":0,"1":1,"2":2,"3":3}', '2026-02-01 10:20:20'),
(4, 1, 4, '感觉疲倦或没有活力', 'single_choice', '[{"label":"完全没有","value":0,"sub":"0天"},{"label":"有几天","value":1,"sub":"1–6天"},{"label":"超过一半时间","value":2,"sub":"7–11天"},{"label":"几乎天天","value":3,"sub":"12–14天"}]', '{"0":0,"1":1,"2":2,"3":3}', '2026-02-01 10:20:30'),
(5, 1, 5, '食欲不振或吃得太多', 'single_choice', '[{"label":"完全没有","value":0,"sub":"0天"},{"label":"有几天","value":1,"sub":"1–6天"},{"label":"超过一半时间","value":2,"sub":"7–11天"},{"label":"几乎天天","value":3,"sub":"12–14天"}]', '{"0":0,"1":1,"2":2,"3":3}', '2026-02-01 10:20:40'),
(6, 1, 6, '觉得自己很糟、很失败，或让自己及家人失望', 'single_choice', '[{"label":"完全没有","value":0,"sub":"0天"},{"label":"有几天","value":1,"sub":"1–6天"},{"label":"超过一半时间","value":2,"sub":"7–11天"},{"label":"几乎天天","value":3,"sub":"12–14天"}]', '{"0":0,"1":1,"2":2,"3":3}', '2026-02-01 10:20:50'),
(7, 1, 7, '对事物专注有困难，例如阅读报纸或看电视时', 'single_choice', '[{"label":"完全没有","value":0,"sub":"0天"},{"label":"有几天","value":1,"sub":"1–6天"},{"label":"超过一半时间","value":2,"sub":"7–11天"},{"label":"几乎天天","value":3,"sub":"12–14天"}]', '{"0":0,"1":1,"2":2,"3":3}', '2026-02-01 10:21:00'),
(8, 1, 8, '动作或说话速度缓慢到别人已经察觉？或刚好相反，烦躁或坐立不安', 'single_choice', '[{"label":"完全没有","value":0,"sub":"0天"},{"label":"有几天","value":1,"sub":"1–6天"},{"label":"超过一半时间","value":2,"sub":"7–11天"},{"label":"几乎天天","value":3,"sub":"12–14天"}]', '{"0":0,"1":1,"2":2,"3":3}', '2026-02-01 10:21:10'),
(9, 1, 9, '有不如死掉或用某种方式伤害自己的念头', 'single_choice', '[{"label":"完全没有","value":0,"sub":"0天"},{"label":"有几天","value":1,"sub":"1–6天"},{"label":"超过一半时间","value":2,"sub":"7–11天"},{"label":"几乎天天","value":3,"sub":"12–14天"}]', '{"0":0,"1":1,"2":2,"3":3}', '2026-02-01 10:21:20'),
-- SDS (20)
(10, 2, 1, '我觉得情绪低落，郁闷', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:22:00'),
(11, 2, 2, '我觉得一天中早晨心情最差', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:22:10'),
(12, 2, 3, '我一阵阵哭出来或觉得想哭', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:22:20'),
(13, 2, 4, '我晚上睡眠不好', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:22:30'),
(14, 2, 5, '我吃得跟平常一样多', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":4,"2":3,"3":2,"4":1}', '2026-02-01 10:22:40'),
(15, 2, 6, '我与异性密切接触时和以往一样感到愉快', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":4,"2":3,"3":2,"4":1}', '2026-02-01 10:22:50'),
(16, 2, 7, '我发现我的体重在下降', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:23:00'),
(17, 2, 8, '我有便秘的苦恼', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:23:10'),
(18, 2, 9, '我心跳比平时快', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:23:20'),
(19, 2, 10, '我无缘无故地感到疲乏', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:23:30'),
(20, 2, 11, '我的头脑跟平常一样清楚', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":4,"2":3,"3":2,"4":1}', '2026-02-01 10:23:40'),
(21, 2, 12, '我觉得做事情很容易', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":4,"2":3,"3":2,"4":1}', '2026-02-01 10:23:50'),
(22, 2, 13, '我坐卧不安，难以保持平静', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:24:00'),
(23, 2, 14, '我对未来抱有希望', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":4,"2":3,"3":2,"4":1}', '2026-02-01 10:24:10'),
(24, 2, 15, '我比平时更容易激怒', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:24:20'),
(25, 2, 16, '我觉得决定什么事很容易', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":4,"2":3,"3":2,"4":1}', '2026-02-01 10:24:30'),
(26, 2, 17, '我觉得自己是个有用的人，有人需要我', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":4,"2":3,"3":2,"4":1}', '2026-02-01 10:24:40'),
(27, 2, 18, '我的生活过得很有意义', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":4,"2":3,"3":2,"4":1}', '2026-02-01 10:24:50'),
(28, 2, 19, '我认为如果我死了别人会生活得更好', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:25:00'),
(29, 2, 20, '平常感兴趣的事我仍然照样感兴趣', 'single_choice', '[{"label":"偶尔或没有","value":1,"sub":"< 1天/周"},{"label":"有时","value":2,"sub":"1–2天/周"},{"label":"经常","value":3,"sub":"3–4天/周"},{"label":"持续","value":4,"sub":"5–7天/周"}]', '{"1":4,"2":3,"3":2,"4":1}', '2026-02-01 10:25:10'),
-- AIS (8)
(30, 3, 1, '入睡时间（关灯后多久才能睡着）', 'single_choice', '[{"label":"无问题","value":0},{"label":"轻度","value":1},{"label":"中度","value":2},{"label":"重度","value":3},{"label":"极重度","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:26:00'),
(31, 3, 2, '夜间苏醒（夜里醒来次数多，难以再入睡）', 'single_choice', '[{"label":"无问题","value":0},{"label":"轻度","value":1},{"label":"中度","value":2},{"label":"重度","value":3},{"label":"极重度","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:26:10'),
(32, 3, 3, '比期望的时间早醒', 'single_choice', '[{"label":"无问题","value":0},{"label":"轻度","value":1},{"label":"中度","value":2},{"label":"重度","value":3},{"label":"极重度","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:26:20'),
(33, 3, 4, '总睡眠时间（比平时明显减少）', 'single_choice', '[{"label":"无问题","value":0},{"label":"轻度","value":1},{"label":"中度","value":2},{"label":"重度","value":3},{"label":"极重度","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:26:30'),
(34, 3, 5, '总睡眠质量（无论睡多久，都觉得质量差）', 'single_choice', '[{"label":"无问题","value":0},{"label":"轻度","value":1},{"label":"中度","value":2},{"label":"重度","value":3},{"label":"极重度","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:26:40'),
(35, 3, 6, '白天情绪（睡眠不好影响情绪状态）', 'single_choice', '[{"label":"无问题","value":0},{"label":"轻度","value":1},{"label":"中度","value":2},{"label":"重度","value":3},{"label":"极重度","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:26:50'),
(36, 3, 7, '白天身体功能（精力、体力、注意力受影响）', 'single_choice', '[{"label":"无问题","value":0},{"label":"轻度","value":1},{"label":"中度","value":2},{"label":"重度","value":3},{"label":"极重度","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:27:00'),
(37, 3, 8, '白天嗜睡（白天犯困、难以集中注意力）', 'single_choice', '[{"label":"无问题","value":0},{"label":"轻度","value":1},{"label":"中度","value":2},{"label":"重度","value":3},{"label":"极重度","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:27:10'),
-- PSS (10)
(38, 4, 1, '感到无法控制生活中重要的事情', 'single_choice', '[{"label":"从未","value":0},{"label":"偶尔","value":1},{"label":"有时","value":2},{"label":"经常","value":3},{"label":"总是","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:28:00'),
(39, 4, 2, '感到无法处理堆积的所有事情', 'single_choice', '[{"label":"从未","value":0},{"label":"偶尔","value":1},{"label":"有时","value":2},{"label":"经常","value":3},{"label":"总是","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:28:10'),
(40, 4, 3, '感到紧张不安或有压力', 'single_choice', '[{"label":"从未","value":0},{"label":"偶尔","value":1},{"label":"有时","value":2},{"label":"经常","value":3},{"label":"总是","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:28:20'),
(41, 4, 4, '成功地处理了生活中的麻烦', 'single_choice', '[{"label":"从未","value":0},{"label":"偶尔","value":1},{"label":"有时","value":2},{"label":"经常","value":3},{"label":"总是","value":4}]', '{"0":4,"1":3,"2":2,"3":1,"4":0}', '2026-02-01 10:28:30'),
(42, 4, 5, '感到事情正按自己的意愿发展', 'single_choice', '[{"label":"从未","value":0},{"label":"偶尔","value":1},{"label":"有时","value":2},{"label":"经常","value":3},{"label":"总是","value":4}]', '{"0":4,"1":3,"2":2,"3":1,"4":0}', '2026-02-01 10:28:40'),
(43, 4, 6, '发现无法应对所有必须做的事情', 'single_choice', '[{"label":"从未","value":0},{"label":"偶尔","value":1},{"label":"有时","value":2},{"label":"经常","value":3},{"label":"总是","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:28:50'),
(44, 4, 7, '能够控制生活中的烦恼', 'single_choice', '[{"label":"从未","value":0},{"label":"偶尔","value":1},{"label":"有时","value":2},{"label":"经常","value":3},{"label":"总是","value":4}]', '{"0":4,"1":3,"2":2,"3":1,"4":0}', '2026-02-01 10:29:00'),
(45, 4, 8, '感到自己能掌控生活中的所有问题', 'single_choice', '[{"label":"从未","value":0},{"label":"偶尔","value":1},{"label":"有时","value":2},{"label":"经常","value":3},{"label":"总是","value":4}]', '{"0":4,"1":3,"2":2,"3":1,"4":0}', '2026-02-01 10:29:10'),
(46, 4, 9, '因为事情超出控制而生气', 'single_choice', '[{"label":"从未","value":0},{"label":"偶尔","value":1},{"label":"有时","value":2},{"label":"经常","value":3},{"label":"总是","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:29:20'),
(47, 4, 10, '感到困难堆积如山，无法克服', 'single_choice', '[{"label":"从未","value":0},{"label":"偶尔","value":1},{"label":"有时","value":2},{"label":"经常","value":3},{"label":"总是","value":4}]', '{"0":0,"1":1,"2":2,"3":3,"4":4}', '2026-02-01 10:29:30');

INSERT INTO questionnaire_answers (id, session_id, template_id, question_id, answer_value, answer_score, created_at) VALUES
(1, 1, 1, 1, '2', 2, '2026-03-10 09:03:00'),
(2, 1, 1, 2, '2', 2, '2026-03-10 09:03:20'),
(3, 1, 1, 3, '3', 3, '2026-03-10 09:03:40'),
(4, 1, 1, 4, '2', 2, '2026-03-10 09:04:00'),
(5, 1, 1, 5, '1', 1, '2026-03-10 09:04:20'),
(6, 1, 1, 6, '2', 2, '2026-03-10 09:04:40'),
(7, 1, 1, 7, '1', 1, '2026-03-10 09:05:00'),
(8, 1, 1, 8, '1', 1, '2026-03-10 09:05:20'),
(9, 1, 1, 9, '0', 0, '2026-03-10 09:05:40'),
(10, 2, 4, 38, '2', 2, '2026-03-09 20:02:00'),
(11, 2, 4, 39, '2', 2, '2026-03-09 20:02:20'),
(12, 2, 4, 40, '3', 3, '2026-03-09 20:02:40'),
(13, 2, 4, 41, '1', 3, '2026-03-09 20:03:00'),
(14, 3, 1, 1, '3', 3, '2026-03-11 19:03:00'),
(15, 3, 1, 2, '3', 3, '2026-03-11 19:03:20'),
(16, 3, 1, 3, '3', 3, '2026-03-11 19:03:40'),
(17, 3, 1, 4, '3', 3, '2026-03-11 19:04:00'),
(18, 3, 1, 5, '2', 2, '2026-03-11 19:04:20'),
(19, 3, 1, 6, '3', 3, '2026-03-11 19:04:40'),
(20, 3, 1, 7, '2', 2, '2026-03-11 19:05:00'),
(21, 3, 1, 8, '2', 2, '2026-03-11 19:05:20'),
(22, 3, 1, 9, '1', 1, '2026-03-11 19:05:40');

INSERT INTO questionnaire_results (id, session_id, template_id, total_score, severity_level, dimension_scores, created_at) VALUES
(1, 1, 1, 14, 'moderate', '{"mood":4,"sleep":3,"energy":2,"cognition":2,"risk":0}', '2026-03-10 09:06:00'),
(2, 2, 4, 10, 'low_stress', '{"stress":10}', '2026-03-09 20:03:30'),
(3, 3, 1, 22, 'severe', '{"mood":6,"sleep":3,"energy":3,"cognition":4,"risk":1}', '2026-03-11 19:06:00');

INSERT INTO media_assets (id, session_id, media_type, file_url, file_name, file_size, duration_seconds, format, upload_status, created_at) VALUES
(1, 1, 'video', 'https://cdn.example.com/session/1/face.mp4', 'face.mp4', 5242880, 45, 'mp4', 'uploaded', '2026-03-10 09:06:30'),
(2, 1, 'audio', 'https://cdn.example.com/session/1/voice.wav', 'voice.wav', 1048576, 38, 'wav', 'uploaded', '2026-03-10 09:06:40'),
(3, 1, 'report_pdf', 'https://cdn.example.com/report/1/report.pdf', 'report.pdf', 820000, NULL, 'pdf', 'generated', '2026-03-10 09:15:30'),
(4, 2, 'audio', 'https://cdn.example.com/session/2/voice.wav', 'voice.wav', 980000, 32, 'wav', 'uploaded', '2026-03-09 20:04:00'),
(5, 3, 'video', 'https://cdn.example.com/session/3/face.mp4', 'face.mp4', 6100000, 52, 'mp4', 'uploaded', '2026-03-11 19:06:30');

INSERT INTO modality_quality_metrics (id, session_id, modality, quality_score, issue_tags, metrics, created_at) VALUES
(1, 1, 'face', 92.50, '["stable_light"]', '{"face_detect_ratio":0.98,"blur_score":0.06}', '2026-03-10 09:07:00'),
(2, 1, 'voice', 88.20, '["minor_noise"]', '{"snr":23.5,"silence_ratio":0.12}', '2026-03-10 09:07:10'),
(3, 2, 'voice', 84.00, '["normal"]', '{"snr":20.1,"silence_ratio":0.10}', '2026-03-09 20:04:10'),
(4, 2, 'face', 45.00, '["missing_stream"]', '{"face_detect_ratio":0.00}', '2026-03-09 20:04:20'),
(5, 3, 'face', 90.00, '["normal"]', '{"face_detect_ratio":0.97,"blur_score":0.08}', '2026-03-11 19:07:00');

INSERT INTO feature_snapshots (id, session_id, modality, feature_summary, feature_file_url, created_at) VALUES
(1, 1, 'face', '{"expression_activity":0.42,"blink_frequency":18,"gaze_stability":0.83}', 'https://cdn.example.com/features/1/face.json', '2026-03-10 09:07:30'),
(2, 1, 'voice', '{"speech_rate":3.8,"pause_duration_avg":1.2,"pitch_variation":0.31}', 'https://cdn.example.com/features/1/voice.json', '2026-03-10 09:07:40'),
(3, 2, 'voice', '{"speech_rate":4.1,"pause_duration_avg":0.8,"pitch_variation":0.46}', 'https://cdn.example.com/features/2/voice.json', '2026-03-09 20:04:40'),
(4, 3, 'face', '{"expression_activity":0.21,"blink_frequency":9,"gaze_stability":0.61}', 'https://cdn.example.com/features/3/face.json', '2026-03-11 19:07:30');

INSERT INTO model_inference_results (id, session_id, model_name, fusion_strategy, face_score, voice_score, scale_score, text_score, fused_score, risk_level, confidence_score, modality_weights, missing_modalities, explanation, created_at) VALUES
(1, 1, 'mh_fusion_v1', 'weighted_sum', 58.00, 62.00, 70.00, 66.00, 64.80, 'medium', 0.9230, '{"face":0.20,"voice":0.20,"scale":0.40,"text":0.20}', '[]', '{"top_factors":["sleep_issue","low_interest","stress_high"]}', '2026-03-10 09:08:00'),
(2, 2, 'mh_fusion_v1', 'degraded_scale_voice', NULL, 48.00, 42.00, NULL, 44.40, 'low', 0.8640, '{"voice":0.40,"scale":0.60}', '["face"]', '{"top_factors":["work_stress","light_sleep"],"degraded":true}', '2026-03-09 20:05:00'),
(3, 3, 'mh_fusion_v1', 'degraded_face_scale', 82.00, NULL, 88.00, NULL, 85.60, 'high', 0.8120, '{"face":0.35,"scale":0.65}', '["voice","text"]', '{"top_factors":["self_harm_item_positive","insomnia","persistent_low_mood"],"degraded":true}', '2026-03-11 19:08:00');

INSERT INTO reports (id, session_id, user_id, report_type, report_json, report_pdf_url, generated_at, created_at) VALUES
(1, 1, 1, 'full', '{"summary":"中度风险，建议睡眠干预与持续观察","risk_level":"medium"}', 'https://cdn.example.com/report/1/report.pdf', '2026-03-10 09:15:25', '2026-03-10 09:15:25'),
(2, 2, 2, 'brief', '{"summary":"轻度压力波动，建议规律作息","risk_level":"low"}', 'https://cdn.example.com/report/2/report.pdf', '2026-03-09 20:08:20', '2026-03-09 20:08:20'),
(3, 3, 1, 'urgent', '{"summary":"高风险，建议立即人工复核并启动预警","risk_level":"high"}', 'https://cdn.example.com/report/3/report.pdf', '2026-03-11 19:12:30', '2026-03-11 19:12:30');

INSERT INTO intervention_recommendations (id, session_id, user_id, recommendation_type, priority, reason, content, created_at) VALUES
(1, 1, 1, 'sleep_guidance', 'P1', '存在明显睡眠问题', '建议连续 7 天进行睡眠记录，并完成晚间呼吸放松训练。', '2026-03-10 09:15:40'),
(2, 1, 1, 'emotion_journal', 'P2', '近期压力较高且情绪波动明显', '建议每天晚间记录情绪日记，持续观察情绪变化趋势。', '2026-03-10 09:15:50'),
(3, 2, 2, 'stress_relief', 'P2', '轻度压力波动', '建议午休前完成 5 分钟正念放松练习，每周查看一次趋势图。', '2026-03-09 20:08:25'),
(4, 3, 1, 'offline_help', 'P1', '量表及模型均提示高风险', '建议联系家属或专业心理咨询师，并由人工尽快复核。', '2026-03-11 19:12:35');

INSERT INTO chat_sessions (id, user_id, evaluation_session_id, session_topic, status, started_at, ended_at, created_at, updated_at) VALUES
(1, 1, 1, '考试压力疏导', 'completed', '2026-03-10 21:00:00', '2026-03-10 21:12:00', '2026-03-10 21:00:00', '2026-03-10 21:12:00'),
(2, 2, 2, '睡眠习惯调整', 'active', '2026-03-09 22:00:00', NULL, '2026-03-09 22:00:00', '2026-03-09 22:15:00');

INSERT INTO chat_messages (id, chat_session_id, sender_type, content, message_type, created_at) VALUES
(1, 1, 'user', '我最近总觉得很焦虑，晚上睡不着。', 'text', '2026-03-10 21:00:30'),
(2, 1, 'assistant', '可以先从呼吸放松开始，我们也一起拆解一下最近最担心的事情。', 'text', '2026-03-10 21:00:35'),
(3, 1, 'user', '主要是考试压力。', 'text', '2026-03-10 21:01:20'),
(4, 2, 'user', '加班后总是很难快速入睡。', 'text', '2026-03-09 22:01:00'),
(5, 2, 'assistant', '建议先尝试固定睡前 30 分钟不看屏幕，并保持卧室光线偏暗。', 'text', '2026-03-09 22:01:10');

INSERT INTO emergency_alerts (id, user_id, session_id, source_type, alert_title, alert_content, risk_level, is_handled, handled_at, created_at) VALUES
(1, 1, 3, 'model', '高风险预警', 'PHQ-9 第 9 题出现阳性，同时融合模型判定为高风险。', 'high', 0, NULL, '2026-03-11 19:12:40');

INSERT INTO emotion_checkins (id, user_id, mood_score, stress_score, sleep_score, energy_score, note, created_at) VALUES
(1, 1, 2, 4, 2, 2, '白天情绪一般，晚上焦虑明显', '2026-03-08 21:00:00'),
(2, 1, 3, 3, 2, 3, '课程较多但还能应付', '2026-03-09 21:00:00'),
(3, 2, 4, 2, 3, 3, '工作忙但整体平稳', '2026-03-09 21:30:00');

INSERT INTO mood_calendar_records (id, user_id, record_date, mood_key, diary_text, weather_key, created_at, updated_at) VALUES
(1, 1, '2026-03-08', 'anxious', '今天复习效率不高，晚上有些自责。', 'cloudy', '2026-03-08 22:00:00', '2026-03-08 22:00:00'),
(2, 1, '2026-03-09', 'tired', '白天很累，晚上还是睡不着。', 'rainy', '2026-03-09 22:00:00', '2026-03-09 22:00:00'),
(3, 2, '2026-03-09', 'calm', '今天虽然忙，但节奏还算可控。', 'sunny', '2026-03-09 22:10:00', '2026-03-09 22:10:00');

INSERT INTO trend_snapshots (id, user_id, snapshot_date, latest_risk_level, avg_mood_score, avg_stress_score, avg_sleep_score, phq9_latest_score, created_at) VALUES
(1, 1, '2026-03-10', 'medium', 2.50, 3.50, 2.00, 14.00, '2026-03-10 23:00:00'),
(2, 2, '2026-03-09', 'low', 4.00, 2.00, 3.00, NULL, '2026-03-09 23:00:00'),
(3, 1, '2026-03-11', 'high', 2.00, 4.50, 1.50, 22.00, '2026-03-11 23:00:00');

SET FOREIGN_KEY_CHECKS = 1;
