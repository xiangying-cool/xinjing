import json
import os
import threading
import time

import requests
from openai import OpenAI

from basereal import BaseReal
from logger import logger

_HISTORY_LOCK = threading.Lock()
_SESSION_HISTORY = {}

# ── RAG 服务配置 ──────────────────────────────────────────────────────────────
RAG_BASE_URL = os.getenv("RAG_BASE_URL", "http://127.0.0.1:8001")
RAG_RETRIEVE_URL = f"{RAG_BASE_URL}/v1/rag/retrieve"
RAG_TIMEOUT = float(os.getenv("RAG_TIMEOUT", "10"))
# 若为 False，则不调用 RAG，沿用原有关键词检测逻辑
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() not in ("false", "0", "no")
# ─────────────────────────────────────────────────────────────────────────────

CRISIS_KEYWORDS = (
    "自杀", "轻生", "不想活", "结束生命", "结束自己", "活着没意义",
    "伤害自己", "割腕", "跳楼", "吞药", "上吊", "suicide", "kill myself",
)

SAFETY_SYSTEM_PROMPT = (
    "你是一个温和、共情、非评判的心理支持数字人，主要服务情绪低落或抑郁倾向用户。"
    "请使用中文、短句、口语化表达。先共情，再澄清，再给1-2个可执行的小建议。"
    "不要做医学诊断，不承诺治愈，不给危险行为步骤。"
    "若用户提及自杀、自伤、立即危险："
    "先表达关切并鼓励立刻联系身边可信任的人和当地急救电话；"
    "引导用户离开危险物品并去有人在的地方；"
    "建议尽快联系专业心理热线或医生。"
)


def _emit_stream_text(text: str, nerfreal: BaseReal, pending: str) -> str:
    chunk = pending + (text or "")
    start = 0
    for idx, char in enumerate(chunk):
        if char in ",.!?;:，。！？；：\n":
            sentence = chunk[start:idx + 1].strip()
            start = idx + 1
            # Do not drop short first replies like "好的。" / "嗯，我在。"
            if sentence and any(c.isalnum() or ("\u4e00" <= c <= "\u9fff") for c in sentence):
                logger.info(sentence)
                nerfreal.put_msg_txt(sentence)
    return chunk[start:]


def _get_session_history(session_id: int, max_history: int):
    with _HISTORY_LOCK:
        history = _SESSION_HISTORY.get(session_id, [])
        return history[-max_history:]


def _append_history(session_id: int, role: str, content: str, max_history: int):
    with _HISTORY_LOCK:
        history = _SESSION_HISTORY.setdefault(session_id, [])
        history.append({"role": role, "content": content})
        if len(history) > max_history:
            _SESSION_HISTORY[session_id] = history[-max_history:]


def _crisis_guard(message: str, nerfreal: BaseReal) -> bool:
    """原有关键词危机检测，作为 RAG 不可用时的降级兜底。"""
    lower = message.lower()
    if any(k in message for k in CRISIS_KEYWORDS) or any(k in lower for k in CRISIS_KEYWORDS):
        safe_reply = (
            "我听到你现在非常痛苦，你的安全最重要。"
            "请你现在先远离可能伤害自己的物品，去一个有人在的地方。"
            "请立刻联系你信任的人陪你，并马上拨打当地急救电话或心理援助热线。"
            "如果你愿意，我可以先陪你做一次慢呼吸：吸气4秒，停2秒，呼气6秒，重复5轮。"
        )
        nerfreal.put_msg_txt(safe_reply)
        return True
    return False


def _call_rag_retrieve(message: str, history: list) -> dict | None:
    """
    调用 RAG 检索服务。

    返回:
        成功 → RAG 响应的字典（含 risk / prompt_bundle 等字段）
        失败 → None（调用方应降级到原始逻辑）
    """
    if not RAG_ENABLED:
        return None
    try:
        resp = requests.post(
            RAG_RETRIEVE_URL,
            json={"query": message, "chat_history": history, "debug": False},
            timeout=RAG_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        logger.warning("RAG 服务连接失败（%s），降级到原始逻辑", RAG_RETRIEVE_URL)
        return None
    except requests.exceptions.Timeout:
        logger.warning("RAG 服务超时（%.1fs），降级到原始逻辑", RAG_TIMEOUT)
        return None
    except Exception:
        logger.exception("调用 RAG 服务发生未知错误，降级到原始逻辑")
        return None


def _call_dashscope_stream(messages, model: str, base_url: str, api_key_env: str, temperature: float):
    api_key = os.getenv(api_key_env)
    if not api_key:
        raise RuntimeError(f"env {api_key_env} is not set")
    client = OpenAI(api_key=api_key, base_url=base_url)
    return client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True,
        stream_options={"include_usage": True},
    )


def _call_ollama_stream(messages, model: str, ollama_url: str, temperature: float):
    url = f"{ollama_url.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": temperature},
    }
    response = requests.post(url, json=payload, timeout=120, stream=True)
    response.raise_for_status()
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        data = json.loads(line)
        content = data.get("message", {}).get("content", "")
        done = bool(data.get("done"))
        yield content, done


def _run_llm_stream(messages, llm_provider, llm_model, llm_base_url,
                    llm_api_key_env, ollama_url, temperature,
                    nerfreal: BaseReal) -> str:
    """
    执行流式 LLM 调用，将结果通过 put_msg_txt 推送给数字人，并返回完整回答文本。
    """
    pending = ""
    answer_all = ""
    first = True
    start = time.perf_counter()

    try:
        if llm_provider == "ollama":
            stream = _call_ollama_stream(messages, llm_model, ollama_url, temperature)
            for text, done in stream:
                if first and text:
                    logger.info("llm provider=%s, model=%s", llm_provider, llm_model)
                    logger.info("llm Time to first chunk: %.3fs", time.perf_counter() - start)
                    first = False
                if text:
                    answer_all += text
                    pending = _emit_stream_text(text, nerfreal, pending)
                if done:
                    break
        else:
            stream = _call_dashscope_stream(
                messages=messages,
                model=llm_model,
                base_url=llm_base_url,
                api_key_env=llm_api_key_env,
                temperature=temperature,
            )
            for chunk in stream:
                if len(chunk.choices) <= 0:
                    continue
                text = chunk.choices[0].delta.content or ""
                if first and text:
                    logger.info("llm provider=%s, model=%s", llm_provider, llm_model)
                    logger.info("llm Time to first chunk: %.3fs", time.perf_counter() - start)
                    first = False
                if text:
                    answer_all += text
                    pending = _emit_stream_text(text, nerfreal, pending)
    except Exception:
        logger.exception("llm stream failed")
        nerfreal.put_msg_txt("抱歉，我现在连接模型失败了。请稍后重试。")
        return answer_all

    if pending.strip():
        nerfreal.put_msg_txt(pending.strip())
        answer_all += pending.strip()

    logger.info("llm Time to last chunk: %.3fs", time.perf_counter() - start)
    return answer_all


def llm_response(message, nerfreal: BaseReal):
    """
    主入口：先调 RAG 检索，再按风险路由决定走危机固定回复还是 LLM 流式生成。

    路由逻辑：
        RAG 可用 & risk.route == "crisis"  → 直接输出 fixed_reply，不再调 LLM
        RAG 可用 & risk.route == "normal"  → 用 RAG 返回的 prompt_bundle 调 LLM
        RAG 不可用（超时/连接失败）         → 降级：关键词危机检测 + 原始 SAFETY_SYSTEM_PROMPT
    """
    start = time.perf_counter()
    opt = nerfreal.opt

    llm_provider = getattr(opt, "llm_provider", "dashscope")
    llm_model = getattr(opt, "llm_model", "qwen-plus")
    llm_base_url = getattr(opt, "llm_base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    llm_api_key_env = getattr(opt, "llm_api_key_env", "DASHSCOPE_API_KEY")
    ollama_url = getattr(opt, "ollama_url", "http://127.0.0.1:11434")
    max_history = int(getattr(opt, "llm_max_history", 8))
    temperature = float(getattr(opt, "llm_temperature", 0.7))
    session_id = int(getattr(nerfreal, "sessionid", 0))

    history = _get_session_history(session_id, max_history)

    # ── ① 调用 RAG 检索服务 ───────────────────────────────────────────────────
    # 将会话历史转换为 RAG 接口期望的 chat_history 格式（最近 max_history 条）
    chat_history_for_rag = [{"role": m["role"], "content": m["content"]} for m in history]
    rag_result = _call_rag_retrieve(message, chat_history_for_rag)

    if rag_result:
        risk = rag_result.get("risk", {})
        route = risk.get("route", "normal")
        handoff = risk.get("handoff_required", False)

        # ── ② 高风险危机路由：直接输出固定回复，跳过 LLM ─────────────────────
        if route == "crisis" or handoff:
            fixed_reply = risk.get("fixed_reply") or (
                "我很担心你现在的安全，请立刻联系身边可信任的人，"
                "或拨打心理援助热线 12356 / 急救电话 120。"
            )
            logger.info("RAG 危机路由触发，matched_rules=%s", risk.get("matched_rules", []))
            nerfreal.put_msg_txt(fixed_reply)
            _append_history(session_id, "user", message, max_history)
            _append_history(session_id, "assistant", fixed_reply, max_history)
            logger.info("crisis reply sent, total=%.3fs", time.perf_counter() - start)
            return

        # ── ③ 普通路由：用 RAG 增强的 prompt 调 LLM ─────────────────────────
        prompt_bundle = rag_result.get("prompt_bundle") or {}
        system_prompt = prompt_bundle.get("system_prompt", SAFETY_SYSTEM_PROMPT)
        user_prompt = prompt_bundle.get("user_prompt", message)

        # RAG 已将历史和知识整合进 user_prompt，无需重复拼接历史
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        logger.info(
            "RAG 普通路由，risk_level=%s，知识片段数=%d",
            risk.get("risk_level", "low"),
            len(rag_result.get("contexts", [])),
        )

    else:
        # ── ④ RAG 降级路由：原有关键词检测 + 原始 SAFETY_SYSTEM_PROMPT ────────
        logger.info("RAG 降级路由，使用原始关键词危机检测")
        if _crisis_guard(message, nerfreal):
            return
        messages = (
            [{"role": "system", "content": SAFETY_SYSTEM_PROMPT}]
            + history
            + [{"role": "user", "content": message}]
        )

    # ── ⑤ 流式调用 LLM ───────────────────────────────────────────────────────
    answer_all = _run_llm_stream(
        messages=messages,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_base_url=llm_base_url,
        llm_api_key_env=llm_api_key_env,
        ollama_url=ollama_url,
        temperature=temperature,
        nerfreal=nerfreal,
    )

    if answer_all:
        _append_history(session_id, "user", message, max_history)
        _append_history(session_id, "assistant", answer_all, max_history)

    logger.info("llm_response total=%.3fs", time.perf_counter() - start)
