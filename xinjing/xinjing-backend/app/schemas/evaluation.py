from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    user_id: Optional[int] = None
    screening_type: str = Field(pattern="^(phq9|sds|ais|pss)$")
    used_modalities: Optional[list[str]] = None
    missing_modalities: Optional[list[str]] = None


class CreateSessionResponse(BaseModel):
    session_id: int
    session_no: str
    status: str
    screening_type: str
    start_time: datetime


class ContextInfoIn(BaseModel):
    recent_stress_level: Optional[str] = None
    sleep_status: Optional[str] = None
    appetite_status: Optional[str] = None
    self_evaluation: Optional[str] = None
    social_avoidance_level: Optional[str] = None
    remark: Optional[str] = None


class AnswerIn(BaseModel):
    question_no: int
    answer_value: int


class SubmitEvaluationRequest(BaseModel):
    template_code: str = Field(pattern="^(phq9|sds|ais|pss)$")
    answers: list[AnswerIn]
    context: Optional[ContextInfoIn] = None
    confidence_score: Optional[float] = None


class SubmitEvaluationResponse(BaseModel):
    report_id: int
    session_id: int
    total_score: int
    risk_level: str
    confidence_score: Optional[float]


class EvaluationSessionOut(BaseModel):
    id: int
    session_no: str
    user_id: Optional[int]
    status: str
    screening_type: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[int]
    used_modalities: Optional[list[str]]
    missing_modalities: Optional[list[str]]
    degraded_inference: bool
    confidence_score: Optional[float]
    overall_risk_level: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ContextInfoOut(BaseModel):
    id: int
    session_id: int
    recent_stress_level: Optional[str]
    sleep_status: Optional[str]
    appetite_status: Optional[str]
    self_evaluation: Optional[str]
    social_avoidance_level: Optional[str]
    remark: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class EvaluationSessionDetailOut(BaseModel):
    session: EvaluationSessionOut
    context: Optional[ContextInfoOut]
