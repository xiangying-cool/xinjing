from dataclasses import dataclass


@dataclass
class ScoreResult:
    total: int
    max_score: int
    level: str
    color: str
    desc: str


def calculate_score(scale: str, answers: list[int]) -> ScoreResult:
    scale = scale.lower()

    if scale == "sds":
        # SDS反向计分题（0-indexed）：对应题目2,5,6,11,12,14,16,17,18,20（1-indexed）
        reverse_indices = {1, 4, 5, 10, 11, 13, 15, 16, 17, 19}
        raw = 0
        for idx, val in enumerate(answers):
            safe_val = val if val is not None else 1
            raw += (5 - safe_val) if idx in reverse_indices else safe_val
        total = int(raw * 1.25)
        if total < 53:
            return ScoreResult(total, 100, "正常", "#22c55e", "无明显抑郁症状，情绪状态良好，请继续保持健康的生活方式。")
        if total <= 62:
            return ScoreResult(total, 100, "轻度抑郁", "#eab308", "存在轻度抑郁倾向，建议关注情绪变化，适当调节压力与作息。")
        if total <= 72:
            return ScoreResult(total, 100, "中度抑郁", "#f97316", "存在中度抑郁症状，建议寻求专业心理咨询和支持。")
        return ScoreResult(total, 100, "重度抑郁", "#dc2626", "存在重度抑郁症状，请尽快寻求专业心理医生的帮助。")

    if scale == "pss":
        reverse_indices = {3, 4, 6, 7}
        total = 0
        for idx, val in enumerate(answers):
            safe_val = val if val is not None else 0
            total += (4 - safe_val) if idx in reverse_indices else safe_val
        if total <= 13:
            return ScoreResult(total, 40, "低压力水平", "#22c55e", "压力处于可控范围内，您的应对能力良好。")
        if total <= 26:
            return ScoreResult(total, 40, "中等压力水平", "#eab308", "存在一定压力，建议采用有效的压力管理和放松策略。")
        return ScoreResult(total, 40, "高压力水平", "#dc2626", "压力水平较高，持续高压可能影响身心健康，建议积极寻求支持。")

    if scale == "ais":
        total = sum(v or 0 for v in answers)
        if total <= 4:
            return ScoreResult(total, 32, "无睡眠障碍", "#22c55e", "睡眠质量良好，无明显障碍。")
        if total <= 10:
            return ScoreResult(total, 32, "可疑失眠", "#eab308", "存在可疑失眠症状，建议关注和改善睡眠卫生习惯。")
        if total <= 14:
            return ScoreResult(total, 32, "轻度失眠", "#f97316", "轻度失眠，建议建立规律的作息时间和睡前放松习惯。")
        if total <= 20:
            return ScoreResult(total, 32, "中度失眠", "#ef4444", "中度失眠，建议寻求专业睡眠咨询或认知行为治疗。")
        return ScoreResult(total, 32, "重度失眠", "#dc2626", "重度失眠，建议尽快就医，排查潜在原因。")

    # default phq9
    total = sum(v or 0 for v in answers)
    if total <= 4:
        return ScoreResult(total, 27, "无抑郁症状", "#22c55e", "您目前状态良好，请继续保持健康的生活方式。")
    if total <= 9:
        return ScoreResult(total, 27, "轻度抑郁", "#eab308", "存在轻度抑郁倾向，建议关注情绪状态，适当自我调适。")
    if total <= 14:
        return ScoreResult(total, 27, "中度抑郁", "#f97316", "存在中度抑郁症状，建议寻求专业心理咨询。")
    if total <= 19:
        return ScoreResult(total, 27, "中重度抑郁", "#ef4444", "存在较重抑郁症状，强烈建议尽快寻求专业帮助。")
    return ScoreResult(total, 27, "重度抑郁", "#dc2626", "存在严重抑郁症状，请立即寻求专业心理医生帮助。")


def build_default_recommendations(scale: str, level: str) -> list[str]:
    """根据量表类型和风险等级返回针对性干预建议（最多 4 条）。"""

    # ── PHQ-9 ───────────────────────────────────────────────────────────────
    if scale == "phq9":
        if "重度" in level:
            return [
                "当前评估提示存在较严重的抑郁症状，强烈建议尽快预约精神科或心理科医生进行专业评估。",
                "请告知身边的家人或朋友你的状态，不要独自承受，让他们陪伴和支持你。",
                "如出现伤害自己的想法，请立即拨打心理援助热线：400-161-9995 或 120。",
                "在就医前，可使用心镜数字人陪伴功能进行情绪疏导，每天记录情绪变化。",
            ]
        if "中度" in level:
            return [
                "建议近期预约心理咨询师进行专业评估，不必等待症状加重才寻求帮助。",
                "每天尝试记录三件让你感到轻松或积极的事情，培养情绪觉察能力。",
                "保持规律作息，减少单独待着的时间，主动与家人或朋友保持联系。",
                "每周进行 2–3 次轻度有氧运动（如散步 30 分钟），有助于改善情绪。",
            ]
        if "轻度" in level:
            return [
                "注意情绪变化，若症状持续两周以上，建议预约专业心理咨询。",
                "尝试每天进行 10 分钟正念冥想或深呼吸练习，缓解压力积累。",
                "保持规律作息和适量运动，避免过度使用社交媒体加重情绪波动。",
            ]
        return [
            "你目前心理状态良好，请继续保持健康的生活方式。",
            "每月进行一次情绪自测，及时发现状态变化。",
            "使用心镜情绪日历功能，记录每日情绪，建立长期的情绪档案。",
        ]

    # ── SDS ─────────────────────────────────────────────────────────────────
    if scale == "sds":
        if "重度" in level:
            return [
                "SDS 评分提示存在重度抑郁症状，建议尽快就医，由精神科医生进行综合评估和治疗。",
                "请将评估结果告知身边信任的人，寻求家庭和社会支持。",
                "如有伤害自己的念头，请立即拨打 400-161-9995 或 120。",
                "治疗期间可结合心镜数字人陪伴功能，配合专业治疗进行心理支持。",
            ]
        if "中度" in level:
            return [
                "SDS 评分提示存在中度抑郁倾向，建议尽快寻求心理咨询或心理科门诊评估。",
                "减少生活中的重大决策，避免因情绪低落做出可能后悔的选择。",
                "建立规律的日常结构（固定起床时间、餐饮、运动），有助于情绪稳定。",
            ]
        if "轻度" in level:
            return [
                "存在轻度抑郁倾向，建议关注情绪变化，适当增加社交活动和户外运动。",
                "尝试进行认知重构：记录让你感到沮丧的想法，并用更平衡的视角重新审视。",
                "使用心镜情绪陪伴功能，每日进行简短的情绪疏导对话。",
            ]
        return [
            "SDS 评分在正常范围内，请继续保持良好的生活和情绪管理习惯。",
            "定期进行心理健康自测，关注自身情绪变化。",
        ]

    # ── AIS ─────────────────────────────────────────────────────────────────
    if scale == "ais":
        if "重度" in level:
            return [
                "重度失眠会严重影响心理健康，建议尽快就医，排查器质性原因，并考虑认知行为治疗（CBT-I）。",
                "睡前 1 小时完全避免屏幕使用，保持卧室黑暗、安静、凉爽（约 18–20°C）。",
                "避免白天长时间补觉，建立固定的起床时间（包括周末），重置生物钟。",
            ]
        if "中度" in level:
            return [
                "建议咨询睡眠专科或心理科，了解是否适合进行失眠认知行为治疗（CBT-I）。",
                "睡前 1 小时进行放松活动（温水浴、轻柔拉伸、冥想），避免刺激性内容。",
                "限制床上活动仅用于睡眠，减少在床上使用手机的时间。",
            ]
        if "轻度" in level or "可疑" in level:
            return [
                "关注睡眠质量，建立固定的作息时间，避免熬夜和白天过度午睡。",
                "睡前 1 小时避免咖啡因、剧烈运动和刺激性内容，营造放松的睡前环境。",
                "使用心镜「睡前安抚」功能，尝试 4-7-8 呼吸法辅助入睡。",
            ]
        return [
            "你的睡眠质量良好，请继续保持规律作息。",
            "避免长期熬夜和睡眠不足，关注睡眠变化对情绪的影响。",
        ]

    # ── PSS ─────────────────────────────────────────────────────────────────
    if scale == "pss":
        if "高压力" in level:
            return [
                "当前压力水平较高，持续高压会增加焦虑和抑郁风险，建议寻求专业心理支持。",
                "识别主要压力来源，尝试将大压力事件分解为可执行的小步骤，逐步应对。",
                "每天安排至少 20 分钟的放松时间（散步、冥想、阅读），为自己创造「心理喘息区」。",
                "减少不必要的承诺，学会对超出能力范围的要求说「不」。",
            ]
        if "中等" in level:
            return [
                "压力处于中等水平，建议主动采用压力管理策略，防止进一步积累。",
                "每周进行 3 次有氧运动，运动是经过科学验证的最有效压力缓解方式之一。",
                "尝试正念减压练习（MBSR），每天 10 分钟的正念冥想有助于降低皮质醇水平。",
            ]
        return [
            "你的压力水平处于健康范围，请继续保持良好的压力应对习惯。",
            "定期评估压力来源，提前识别和管理潜在压力因素。",
        ]

    # ── 通用兜底 ─────────────────────────────────────────────────────────────
    recommendations = [
        "保持规律作息，每天保证 7 小时以上睡眠。",
        "每周进行 3 次轻度有氧运动，如散步或瑜伽。",
        "使用心镜情绪陪伴功能，进行日常情绪疏导对话。",
    ]
    if "重度" in level:
        recommendations.append("建议尽快寻求线下专业心理医生的帮助。")
    return recommendations
