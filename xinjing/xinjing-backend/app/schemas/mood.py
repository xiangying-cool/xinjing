from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class MoodCalendarUpsertRequest(BaseModel):
    user_id: Optional[int] = None
    mood_key: str = Field(pattern="^(sunny|partly|cloudy|rainy|stormy)$")
    diary_text: Optional[str] = Field(default=None, max_length=300)
    weather_key: Optional[str] = Field(default=None, max_length=20)


class MoodCalendarRecordOut(BaseModel):
    id: int
    user_id: int
    record_date: date
    mood_key: str
    diary_text: Optional[str]
    weather_key: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmotionCheckinCreateRequest(BaseModel):
    user_id: Optional[int] = None
    mood_score: int = Field(ge=1, le=5)
    stress_score: int = Field(ge=1, le=5)
    sleep_score: int = Field(ge=1, le=5)
    energy_score: int = Field(ge=1, le=5)
    note: Optional[str] = Field(default=None, max_length=255)


class EmotionCheckinOut(BaseModel):
    id: int
    user_id: int
    mood_score: int
    stress_score: int
    sleep_score: int
    energy_score: int
    note: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class TrendSnapshotUpsertRequest(BaseModel):
    user_id: Optional[int] = None
    latest_risk_level: Optional[str] = None
    avg_mood_score: Optional[int] = Field(default=None, ge=1, le=5)
    avg_stress_score: Optional[int] = Field(default=None, ge=1, le=5)
    avg_sleep_score: Optional[int] = Field(default=None, ge=1, le=5)
    phq9_latest_score: Optional[int] = Field(default=None, ge=0, le=27)


class TrendSnapshotOut(BaseModel):
    id: int
    user_id: int
    snapshot_date: date
    latest_risk_level: Optional[str]
    avg_mood_score: Optional[int]
    avg_stress_score: Optional[int]
    avg_sleep_score: Optional[int]
    phq9_latest_score: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}
