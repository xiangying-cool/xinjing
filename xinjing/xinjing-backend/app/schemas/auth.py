from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str = Field(min_length=6, max_length=128)
    confirm_password: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None
    age_range: Optional[str] = None

    @model_validator(mode="after")
    def validate_confirm_password(self) -> "RegisterRequest":
        if self.confirm_password is not None and self.confirm_password != self.password:
            raise ValueError("Password and confirm_password do not match")
        return self


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str]
    role: str
    status: str
    last_login_at: Optional[datetime]

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
