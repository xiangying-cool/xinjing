from __future__ import annotations

import re
from typing import List

from app.schemas import RiskAssessment, UserState


HIGH_RISK_PATTERNS = {
    'explicit_suicide': re.compile(r'(自杀|轻生|结束生命|去死|不想活了|活不下去|想死)'),
    'plan_or_action': re.compile(r'(今晚|现在|马上|准备|已经|遗书|跳楼|割腕|吃药|上吊|烧炭|服毒|刀片|安眠药)'),
}

MEDIUM_RISK_PATTERNS = {
    'passive_death_wish': re.compile(r'(消失就好了|活着没意义|活着好累|不如死了算了|希望不要醒来|没有活下去的意义)'),
    'severe_hopelessness': re.compile(r'(绝望|撑不住了|崩溃了|没人帮我|彻底没办法了)'),
}


def detect_risk(query: str, chat_history: List[str] | None = None, user_state: UserState | None = None) -> RiskAssessment:
    recent_text = ' '.join(chat_history[-4:] if chat_history else [])
    text = f'{recent_text} {query}'.strip()
    matched_rules: List[str] = []

    high_signal = False
    if HIGH_RISK_PATTERNS['explicit_suicide'].search(text):
        matched_rules.append('explicit_suicide')
        high_signal = True
    if HIGH_RISK_PATTERNS['plan_or_action'].search(text) and high_signal:
        matched_rules.append('plan_or_action')

    if user_state and (user_state.suicide_item_score or 0) > 0:
        matched_rules.append('suicide_item_score_positive')
        high_signal = True

    if high_signal:
        return RiskAssessment(
            risk_level='high',
            route='crisis',
            handoff_required=True,
            matched_rules=matched_rules,
            fixed_reply=(
                '我很担心你现在的安全。请不要独自承受，先把自己移到有人在的地方，并把可能用于伤害自己的物品放远。'
                '请立刻联系身边可信任的人陪你，或尽快拨打 12356 心理援助热线；如果你已经有明确计划、正在实施，'
                '或无法保证自己安全，请立即拨打 120/110 或前往最近急诊。'
            ),
        )

    medium_signal = False
    for name, pattern in MEDIUM_RISK_PATTERNS.items():
        if pattern.search(text):
            matched_rules.append(name)
            medium_signal = True

    if user_state and user_state.phq9_score is not None and user_state.phq9_score >= 15:
        matched_rules.append('phq9_ge_15')
        medium_signal = True

    if medium_signal:
        return RiskAssessment(
            risk_level='medium',
            route='normal',
            handoff_required=False,
            matched_rules=matched_rules,
        )

    return RiskAssessment(risk_level='low', route='normal', handoff_required=False, matched_rules=[])
