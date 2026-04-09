from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import extract
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.mood import EmotionCheckin, MoodCalendarRecord, TrendSnapshot
from app.models.user import User
from app.schemas.mood import (
    EmotionCheckinCreateRequest,
    EmotionCheckinOut,
    MoodCalendarRecordOut,
    MoodCalendarUpsertRequest,
    TrendSnapshotOut,
    TrendSnapshotUpsertRequest,
)

router = APIRouter(prefix="/mood-calendar", tags=["mood-calendar"])


def resolve_requested_user_id(current_user: User, requested_user_id: int | None) -> int:
    if requested_user_id is None:
        return int(current_user.id)
    if int(requested_user_id) != int(current_user.id):
        raise HTTPException(status_code=403, detail="Cannot access other user's data")
    return int(current_user.id)


@router.get("/checkins", response_model=list[EmotionCheckinOut])
def list_emotion_checkins(
    user_id: int | None = Query(default=None),
    limit: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[EmotionCheckin]:
    target_user_id = resolve_requested_user_id(current_user=current_user, requested_user_id=user_id)
    rows = (
        db.query(EmotionCheckin)
        .filter(EmotionCheckin.user_id == target_user_id)
        .order_by(EmotionCheckin.created_at.desc(), EmotionCheckin.id.desc())
        .limit(limit)
        .all()
    )
    return rows


@router.post("/checkins", response_model=EmotionCheckinOut, status_code=status.HTTP_201_CREATED)
def create_emotion_checkin(
    payload: EmotionCheckinCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EmotionCheckin:
    target_user_id = resolve_requested_user_id(current_user=current_user, requested_user_id=payload.user_id)
    row = EmotionCheckin(user_id=target_user_id, **payload.model_dump(exclude={"user_id"}))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/trends", response_model=list[TrendSnapshotOut])
def list_trend_snapshots(
    user_id: int | None = Query(default=None),
    limit: int = Query(default=90, ge=1, le=366),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TrendSnapshot]:
    target_user_id = resolve_requested_user_id(current_user=current_user, requested_user_id=user_id)
    rows = (
        db.query(TrendSnapshot)
        .filter(TrendSnapshot.user_id == target_user_id)
        .order_by(TrendSnapshot.snapshot_date.desc(), TrendSnapshot.id.desc())
        .limit(limit)
        .all()
    )
    return rows


@router.put("/trends/{snapshot_date}", response_model=TrendSnapshotOut)
def upsert_trend_snapshot(
    snapshot_date: date,
    payload: TrendSnapshotUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrendSnapshot:
    target_user_id = resolve_requested_user_id(current_user=current_user, requested_user_id=payload.user_id)
    row = (
        db.query(TrendSnapshot)
        .filter(
            TrendSnapshot.user_id == target_user_id,
            TrendSnapshot.snapshot_date == snapshot_date,
        )
        .first()
    )
    if not row:
        row = TrendSnapshot(
            user_id=target_user_id,
            snapshot_date=snapshot_date,
            latest_risk_level=payload.latest_risk_level,
            avg_mood_score=payload.avg_mood_score,
            avg_stress_score=payload.avg_stress_score,
            avg_sleep_score=payload.avg_sleep_score,
            phq9_latest_score=payload.phq9_latest_score,
        )
        db.add(row)
    else:
        row.latest_risk_level = payload.latest_risk_level
        row.avg_mood_score = payload.avg_mood_score
        row.avg_stress_score = payload.avg_stress_score
        row.avg_sleep_score = payload.avg_sleep_score
        row.phq9_latest_score = payload.phq9_latest_score

    db.commit()
    db.refresh(row)
    return row


@router.put("/{record_date}", response_model=MoodCalendarRecordOut)
def upsert_mood_record(
    record_date: date,
    payload: MoodCalendarUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MoodCalendarRecord:
    target_user_id = resolve_requested_user_id(current_user=current_user, requested_user_id=payload.user_id)
    row = (
        db.query(MoodCalendarRecord)
        .filter(
            MoodCalendarRecord.user_id == target_user_id,
            MoodCalendarRecord.record_date == record_date,
        )
        .first()
    )
    if not row:
        row = MoodCalendarRecord(
            user_id=target_user_id,
            record_date=record_date,
            mood_key=payload.mood_key,
            diary_text=payload.diary_text,
            weather_key=payload.weather_key,
        )
        db.add(row)
    else:
        row.mood_key = payload.mood_key
        row.diary_text = payload.diary_text
        row.weather_key = payload.weather_key
        row.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(row)
    return row


@router.get("", response_model=list[MoodCalendarRecordOut])
def list_mood_records(
    user_id: int | None = Query(default=None),
    month: str | None = Query(default=None, description="YYYY-MM; omitted means all records"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MoodCalendarRecord]:
    target_user_id = resolve_requested_user_id(current_user=current_user, requested_user_id=user_id)
    query = db.query(MoodCalendarRecord).filter(MoodCalendarRecord.user_id == target_user_id)

    if month:
        try:
            year, mon = month.split("-")
            year_num = int(year)
            mon_num = int(mon)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid month format, expected YYYY-MM") from exc
        if not (1 <= mon_num <= 12):
            raise HTTPException(status_code=400, detail="Invalid month value, must be between 01 and 12")

        query = query.filter(
            extract("year", MoodCalendarRecord.record_date) == year_num,
            extract("month", MoodCalendarRecord.record_date) == mon_num,
        )

    rows = query.order_by(MoodCalendarRecord.record_date.asc()).all()
    return rows


@router.get("/{record_date}", response_model=MoodCalendarRecordOut)
def get_mood_record(
    record_date: date,
    user_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MoodCalendarRecord:
    target_user_id = resolve_requested_user_id(current_user=current_user, requested_user_id=user_id)
    row = (
        db.query(MoodCalendarRecord)
        .filter(
            MoodCalendarRecord.user_id == target_user_id,
            MoodCalendarRecord.record_date == record_date,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Mood record not found")
    return row


@router.delete("/{record_date}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mood_record(
    record_date: date,
    user_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    target_user_id = resolve_requested_user_id(current_user=current_user, requested_user_id=user_id)
    row = (
        db.query(MoodCalendarRecord)
        .filter(
            MoodCalendarRecord.user_id == target_user_id,
            MoodCalendarRecord.record_date == record_date,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Mood record not found")

    db.delete(row)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
