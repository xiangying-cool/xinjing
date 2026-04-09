from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal['system', 'user', 'assistant']
    content: str


class UserState(BaseModel):
    phq9_score: Optional[int] = None
    suicide_item_score: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    extra: Dict[str, Any] = Field(default_factory=dict)


class RetrievalFilters(BaseModel):
    categories: Optional[List[str]] = None
    source_names: Optional[List[str]] = None


class QueryRequest(BaseModel):
    query: str = Field(..., description='Current user query text. Audio/video should be converted to text upstream.')
    chat_history: List[ChatMessage] = Field(default_factory=list)
    user_state: Optional[UserState] = None
    filters: Optional[RetrievalFilters] = None
    top_k: Optional[int] = None
    return_prompt_bundle: bool = True
    debug: bool = False


class RetrievedChunk(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    category: str
    source_name: str
    source_url: Optional[str] = None
    section: Optional[str] = None
    content: str
    score: float
    dense_rank: Optional[int] = None
    sparse_rank: Optional[int] = None
    rerank_score: Optional[float] = None


class PromptBundle(BaseModel):
    system_prompt: str
    user_prompt: str
    citation_map: List[Dict[str, Any]]


class RiskAssessment(BaseModel):
    risk_level: Literal['low', 'medium', 'high'] = 'low'
    route: Literal['normal', 'crisis'] = 'normal'
    handoff_required: bool = False
    matched_rules: List[str] = Field(default_factory=list)
    fixed_reply: Optional[str] = None


class QueryResponse(BaseModel):
    query: str
    normalized_query: str
    rewritten_queries: List[str] = Field(default_factory=list)
    risk: RiskAssessment
    contexts: List[RetrievedChunk] = Field(default_factory=list)
    prompt_bundle: Optional[PromptBundle] = None
    answer: Optional[str] = None
    latency_ms: Dict[str, float] = Field(default_factory=dict)
    debug: Dict[str, Any] = Field(default_factory=dict)


class RebuildIndexResponse(BaseModel):
    status: Literal['ok'] = 'ok'
    chunk_count: int
    doc_count: int
    embedding_dimension: int
    storage_dir: str


class HealthResponse(BaseModel):
    status: Literal['ok'] = 'ok'
    index_ready: bool
    chunk_count: int
    llm_enabled: bool
    embedding_model: str
    rerank_model: str
