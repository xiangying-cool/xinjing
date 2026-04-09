from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User, UserProfile
from app.schemas.auth import LoginRequest, RegisterRequest, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    existing_username = db.query(User).filter(User.username == payload.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    resolved_email = payload.email or f"{payload.username}@xinjing.local"
    existing_email = db.query(User).filter(User.email == resolved_email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    if payload.phone:
        phone_user = db.query(User).filter(User.phone == payload.phone).first()
        if phone_user:
            raise HTTPException(status_code=400, detail="Phone already exists")

    user = User(
        username=payload.username,
        email=resolved_email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role="user",
        status="active",
    )
    db.add(user)
    db.flush()

    profile = UserProfile(
        user_id=user.id,
        nickname=payload.nickname or payload.username,
        gender=payload.gender,
        age_range=payload.age_range,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenOut:
    # allow login by username OR email for easier frontend integration
    user = db.query(User).filter((User.username == payload.username) | (User.email == payload.username)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if user.status != "active":
        raise HTTPException(status_code=403, detail="User is disabled")

    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id), extra={"username": user.username})
    return TokenOut(access_token=token, user=user)
