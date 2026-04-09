from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User, UserProfile
from app.schemas.user import UserProfileOut, UserProfileUpdateRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}/profile", response_model=UserProfileOut)
def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfile:
    if int(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Cannot access other user's data")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id, nickname=user.username)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("/{user_id}/profile", response_model=UserProfileOut)
def update_user_profile(
    user_id: int,
    payload: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfile:
    if int(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Cannot access other user's data")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id, nickname=user.username)
        db.add(profile)
        db.flush()

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile
