from datetime import datetime
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.chat import ChatMessage, ChatSession
from app.models.evaluation import EvaluationSession
from app.models.user import User
from app.schemas.chat import ChatMessageCreateRequest, ChatMessageOut, ChatSessionOut, CreateChatSessionRequest

router = APIRouter(prefix="/chat", tags=["chat"])

RAG_SERVICE_URL = "http://localhost:8001/v1/rag/answer"
RAG_TIMEOUT = 45.0  # seconds — LLM generation can take 10-15s

# 危机关键词兜底（RAG 服务不可用时的本地检测）
_CRISIS_KEYWORDS = ["自杀", "轻生", "不想活", "结束生命", "去死", "活不下去", "想死"]
_FALLBACK_CRISIS_REPLY = (
    "我非常担心你现在的状态。请先离开危险的地方，联系一个你信任的人陪在你身边。"
    "你也可以立即拨打心理援助热线：北京 010-82951332、全国 400-161-9995、紧急情况 120 / 110。"
    "你不是一个人，我们会陪你渡过这段时光。"
)

DEFAULT_REPLY_MAP = {
    "压力": "听起来你最近压力比较大。可以先告诉我压力最主要来自哪一件事，我们一起拆开看。",
    "睡": "睡眠会直接影响情绪。我们可以先做一个两分钟呼吸放松，然后再看你的入睡习惯。",
    "低落": "谢谢你愿意说出来。你现在不是一个人，我会陪你把这种感受慢慢说清楚。",
    "焦虑": "焦虑通常会让大脑一直高速运转。我们先把最担心的三件事写出来，再一件件处理。",
}


def _keyword_fallback_reply(text: str) -> str:
    """RAG 不可用时的本地关键词兜底回复，高风险优先检测。"""
    for kw in _CRISIS_KEYWORDS:
        if kw in text:
            return _FALLBACK_CRISIS_REPLY
    for keyword, reply in DEFAULT_REPLY_MAP.items():
        if keyword in text:
            return reply
    return "我收到了你的感受。你可以再多说一点最近最困扰你的场景，我会继续陪你梳理。"


def _get_user_state(db: Session, user_id: int) -> dict:
    """从数据库查询用户最近一次 PHQ-9 结果，构建 user_state 传给 RAG 服务。"""
    try:
        from app.models.questionnaire import QuestionnaireTemplate, QuestionnaireResult
        template = db.query(QuestionnaireTemplate).filter(
            QuestionnaireTemplate.code == "phq9",
            QuestionnaireTemplate.is_active == 1,
        ).first()
        if not template:
            return {}
        result = (
            db.query(QuestionnaireResult)
            .join(EvaluationSession, EvaluationSession.id == QuestionnaireResult.session_id)
            .filter(
                EvaluationSession.user_id == user_id,
                QuestionnaireResult.template_id == template.id,
            )
            .order_by(desc(QuestionnaireResult.created_at))
            .first()
        )
        if not result:
            return {}
        suicide_score = None
        if result.dimension_scores and "suicide_item" in result.dimension_scores:
            suicide_score = result.dimension_scores["suicide_item"]
        return {
            "phq9_score": result.total_score,
            "suicide_item_score": suicide_score,
        }
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning(f"获取用户状态时出错: {exc}")
        return {}


def _build_rag_history(messages: list) -> list:
    """将数据库消息列表转为 RAG 服务期望的 chat_history 格式（最近 6 条）。"""
    history = []
    for msg in messages[-6:]:
        role = "user" if msg.sender_type == "user" else "assistant"
        history.append({"role": role, "content": msg.content})
    return history


def call_rag_service(query: str, history: list, user_state: dict) -> Optional[str]:
    """同步调用 RAG 服务，返回回复文本；服务不可用时返回 None。"""
    payload = {
        "query": query,
        "chat_history": history,
        "user_state": user_state if user_state else None,
        "return_prompt_bundle": False,
    }
    try:
        resp = httpx.post(RAG_SERVICE_URL, json=payload, timeout=RAG_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        # 高风险时 RAG 直接返回 fixed_reply，优先使用
        risk = data.get("risk", {})
        if risk.get("fixed_reply"):
            return risk["fixed_reply"]
        return data.get("answer") or None
    except httpx.ConnectError as exc:
        import logging
        logging.getLogger(__name__).warning(f"RAG服务连接失败: {exc}")
        return None
    except httpx.TimeoutException as exc:
        import logging
        logging.getLogger(__name__).warning(f"RAG服务超时: {exc}")
        return None
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error(f"调用RAG服务时发生未知错误: {exc}")
        return None


@router.post("/sessions", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
def create_chat_session(
    payload: CreateChatSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSession:
    row = ChatSession(
        user_id=int(current_user.id),
        evaluation_session_id=payload.evaluation_session_id,
        session_topic=payload.session_topic or "日常陪伴",
        status="active",
        started_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/sessions", response_model=list[ChatSessionOut])
def list_chat_sessions(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatSession]:
    rows = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == int(current_user.id))
        .order_by(ChatSession.created_at.desc(), ChatSession.id.desc())
        .limit(limit)
        .all()
    )
    return rows


@router.get("/sessions/{session_id}", response_model=ChatSessionOut)
def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSession:
    row = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == int(current_user.id),
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return row


@router.patch("/sessions/{session_id}/close", response_model=ChatSessionOut)
def close_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSession:
    row = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == int(current_user.id),
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Chat session not found")

    row.status = "ended"
    row.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return row


@router.post("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
def add_chat_message(
    session_id: int,
    payload: ChatMessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatMessage]:
    chat_session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == int(current_user.id),
    ).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    if chat_session.status != "active":
        raise HTTPException(status_code=409, detail="Chat session is not active")

    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Message content cannot be empty")

    incoming = ChatMessage(
        chat_session_id=session_id,
        sender_type=payload.sender_type or "user",
        content=content,
        message_type=payload.message_type or "text",
    )
    db.add(incoming)
    db.flush()

    if incoming.sender_type == "user":
        # 构建对话历史（不含刚入库的这条，由 RAG 服务自行拼接 query）
        prev_messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.chat_session_id == session_id)
            .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
            .all()
        )
        history = _build_rag_history(prev_messages[:-1])  # 排除刚写入的用户消息
        user_state = _get_user_state(db, int(current_user.id))

        # 优先调用 RAG 服务；失败时降级为本地关键词兜底
        reply_text = call_rag_service(content, history, user_state)
        if not reply_text:
            reply_text = _keyword_fallback_reply(content)

        reply = ChatMessage(
            chat_session_id=session_id,
            sender_type="agent",
            content=reply_text,
            message_type="text",
        )
        db.add(reply)

    db.commit()

    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_session_id == session_id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )
    return rows


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
def list_chat_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatMessage]:
    chat_session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == int(current_user.id),
    ).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_session_id == session_id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )
    return rows
