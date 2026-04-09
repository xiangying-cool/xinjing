from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class CreateChatSessionRequest(BaseModel):
    user_id: int
    session_topic: Optional[str] = Field(default=None, max_length=100)
    evaluation_session_id: Optional[int] = None
    mode: Optional[str] = Field(default=None, max_length=30)

    @model_validator(mode="after")
    def normalize_topic(self) -> "CreateChatSessionRequest":
        if not self.session_topic:
            self.session_topic = self.mode or "日常陪伴"
        return self


class ChatSessionOut(BaseModel):
    id: int
    user_id: Optional[int]
    evaluation_session_id: Optional[int]
    session_topic: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageCreateRequest(BaseModel):
    sender_type: Optional[str] = Field(default=None, max_length=20)
    role: Optional[str] = Field(default=None, max_length=20)
    content: str = Field(min_length=1)
    message_type: str = Field(default="text", max_length=20)

    @model_validator(mode="after")
    def normalize_sender_type(self) -> "ChatMessageCreateRequest":
        raw = (self.sender_type or self.role or "").strip().lower()
        alias = {
            "assistant": "agent",
            "ai": "agent",
            "bot": "agent",
        }
        normalized = alias.get(raw, raw)
        if normalized not in {"user", "agent", "system"}:
            raise ValueError("sender_type must be one of: user, agent, system")
        self.sender_type = normalized
        return self


class ChatMessageOut(BaseModel):
    id: int
    chat_session_id: int
    sender_type: str
    content: str
    message_type: str
    created_at: datetime

    model_config = {"from_attributes": True}
