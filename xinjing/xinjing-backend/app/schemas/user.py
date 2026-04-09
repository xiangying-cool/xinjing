from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserProfileOut(BaseModel):
    id: int
    user_id: int
    nickname: Optional[str]
    gender: Optional[str]
    age_range: Optional[str]
    education_level: Optional[str]
    occupation: Optional[str]
    emergency_contact: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfileUpdateRequest(BaseModel):
    nickname: Optional[str] = Field(default=None, max_length=50)
    gender: Optional[str] = Field(default=None, max_length=20)
    age_range: Optional[str] = Field(default=None, max_length=20)
    education_level: Optional[str] = Field(default=None, max_length=30)
    occupation: Optional[str] = Field(default=None, max_length=50)
    emergency_contact: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=255)
