from __future__ import annotations

import json
from typing import List

from openai import OpenAI

from app.config import Settings


class OpenAICompatibleLLM:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(
            base_url=settings.openai_base_url,
            api_key=settings.openai_api_key,
            timeout=settings.llm_timeout,
        )

    def chat(self, system_prompt: str, user_prompt: str, temperature: float | None = None) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.openai_model,
            temperature=self.settings.llm_temperature if temperature is None else temperature,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
        )
        return response.choices[0].message.content or ''

    def rewrite_queries(self, query: str, history: List[dict]) -> List[str]:
        prompt = (
            '请把用户问题改写成适合知识库检索的 2 到 3 个中文查询。\n'
            '要求:\n'
            '1. 只输出 JSON 数组，例如 ["查询1", "查询2"]\n'
            '2. 保留关键症状、需求、场景词\n'
            '3. 不要输出解释\n\n'
            f'历史对话: {json.dumps(history[-4:], ensure_ascii=False)}\n'
            f'当前问题: {query}'
        )
        raw = self.chat(system_prompt='你是一个检索查询改写器。', user_prompt=prompt, temperature=0.0)
        try:
            queries = json.loads(raw)
            if isinstance(queries, list):
                result = [str(item).strip() for item in queries if str(item).strip()]
                if result:
                    return result
        except json.JSONDecodeError:
            pass
        # LLM输出非预期格式时，回退到原始查询，避免检索阶段空查询
        return [query]
