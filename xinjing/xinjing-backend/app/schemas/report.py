from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class ReportOut(BaseModel):
    id: int
    session_id: int
    user_id: Optional[int]
    report_type: str
    report_json: dict[str, Any]
    report_pdf_url: Optional[str]
    generated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class InterventionRecommendationOut(BaseModel):
    id: int
    session_id: int
    user_id: Optional[int]
    recommendation_type: str
    priority: int
    reason: Optional[str]
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EmergencyAlertOut(BaseModel):
    id: int
    user_id: int
    session_id: Optional[int]
    source_type: str
    alert_title: str
    alert_content: str
    risk_level: str
    is_handled: int
    handled_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
