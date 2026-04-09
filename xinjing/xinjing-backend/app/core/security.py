from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


# 使用 bcrypt 但设置 truncate_error=False 来避免长度限制错误
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False,  # 自动截断长密码
    bcrypt__ident="2b",  # 使用兼容的标识符
)


def hash_password(password: str) -> str:
    # 确保密码是字符串并编码为 bytes
    if isinstance(password, str):
        password = password.encode('utf-8')
    # bcrypt 限制 72 bytes，超长会自动截断
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    if isinstance(password, str):
        password = password.encode('utf-8')
    try:
        return pwd_context.verify(password, password_hash)
    except Exception:
        # 如果验证失败，返回 False 而不是抛出异常
        return False


def create_access_token(subject: str, minutes: int | None = None, extra: dict[str, Any] | None = None) -> str:
    expire_minutes = minutes or settings.jwt_expire_minutes
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire_at}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
