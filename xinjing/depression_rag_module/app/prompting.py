from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from app.internal_types import Chunk
from app.schemas import PromptBundle, RiskAssessment


def build_context_block(chunks: Iterable[Chunk]) -> Tuple[str, List[Dict]]:
    lines: List[str] = []
    citation_map: List[Dict] = []
    for i, chunk in enumerate(chunks, start=1):
        lines.append(
            f'[{i}] 标题: {chunk.title}\n'
            f'分类: {chunk.category}\n'
            f'来源: {chunk.source_name}\n'
            f'内容: {chunk.content}'
        )
        citation_map.append(
            {
                'id': i,
                'chunk_id': chunk.chunk_id,
                'doc_id': chunk.doc_id,
                'title': chunk.title,
                'source_name': chunk.source_name,
                'source_url': chunk.source_url,
                'category': chunk.category,
                'section': chunk.section,
            }
        )
    return '\n\n'.join(lines), citation_map


def build_system_prompt(risk: RiskAssessment) -> str:
    base = (
        '你是网站中的"心理支持数字人"的知识增强模块输出助手。'
        '你的目标是基于检索到的资料，为用户提供温和、共情、清晰、可执行的支持性回答。\n\n'
        '严格规则:\n'
        '1. 只能优先依据提供的资料回答；资料不足时要明确说"现有资料不足以支持更具体判断"。\n'
        '2. 不能把自己说成医生，不能做确定性诊断，不能替代线下专业评估。\n'
        '3. 不提供危险、自伤、自杀的具体方法、步骤、剂量或可操作细节。\n'
        '4. 先简短共情，再给出 2-4 条可执行建议，再补一句是否建议寻求专业帮助。\n'
        '5. 对重要事实尽量在句末用 [1][2] 这种形式标注资料编号。\n'
        '6. 语气要自然、温和，避免说教。\n'
        '7. **格式要求**: 使用 Markdown 格式让回复更美观:\n'
        '   - 关键句子用 **加粗** 突出\n'
        '   - 建议列表用 - 或 1. 2. 3. 编号\n'
        '   - 重要提醒用 💡 或 ⚠️ 等 emoji 开头\n'
        '   - 适当分段，每段不要太长\n'
    )
    if risk.risk_level == 'high':
        base += (
            '7. 当前对话存在高风险信号。你的首要任务是鼓励用户立即联系现实中的人和紧急支持系统，'
            '不要继续展开一般性心理教育内容。\n'
        )
    return base


def build_user_prompt(query: str, history: List[Dict[str, str]], context_block: str, risk: RiskAssessment) -> str:
    history_text = '\n'.join([f"{m['role']}: {m['content']}" for m in history[-6:]])
    crisis_hint = ''
    if risk.risk_level == 'high' and risk.fixed_reply:
        crisis_hint = f'\n高风险优先回复参考: {risk.fixed_reply}\n'

    return (
        f'对话历史(最近几轮):\n{history_text or "无"}\n\n'
        f'用户当前问题:\n{query}\n'
        f'{crisis_hint}\n'
        f'可用资料:\n{context_block or "无"}\n\n'
        '请输出最终可直接展示给用户的回答。'
    )


def build_prompt_bundle(query: str, history: List[Dict[str, str]], chunks: List[Chunk], risk: RiskAssessment) -> PromptBundle:
    context_block, citation_map = build_context_block(chunks)
    return PromptBundle(
        system_prompt=build_system_prompt(risk),
        user_prompt=build_user_prompt(query, history, context_block, risk),
        citation_map=citation_map,
    )
