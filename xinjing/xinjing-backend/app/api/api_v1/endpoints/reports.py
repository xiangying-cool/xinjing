from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.evaluation import EvaluationSession
from app.models.report import EmergencyAlert, InterventionRecommendation, Report
from app.models.user import User
from app.schemas.report import EmergencyAlertOut, InterventionRecommendationOut, ReportOut

router = APIRouter(prefix="/reports", tags=["reports"])


def resolve_requested_user_id(current_user: User, requested_user_id: int | None) -> int:
    if requested_user_id is None:
        return int(current_user.id)
    if int(requested_user_id) != int(current_user.id):
        raise HTTPException(status_code=403, detail="Cannot access other user's data")
    return int(current_user.id)


def query_reports_for_current_user(db: Session, current_user_id: int):
    return db.query(Report).outerjoin(EvaluationSession, EvaluationSession.id == Report.session_id).filter(
        or_(Report.user_id == current_user_id, EvaluationSession.user_id == current_user_id)
    )


@router.get("", response_model=list[ReportOut])
def list_reports(
    user_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Report]:
    target_user_id = resolve_requested_user_id(current_user=current_user, requested_user_id=user_id)
    query = query_reports_for_current_user(db=db, current_user_id=target_user_id)
    return query.order_by(Report.created_at.desc()).limit(limit).all()


@router.get("/alerts", response_model=list[EmergencyAlertOut])
def list_alerts(
    user_id: int | None = Query(default=None),
    session_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[EmergencyAlert]:
    target_user_id = resolve_requested_user_id(current_user=current_user, requested_user_id=user_id)
    query = db.query(EmergencyAlert).filter(EmergencyAlert.user_id == target_user_id)
    if session_id is not None:
        query = query.filter(EmergencyAlert.session_id == session_id)
    rows = query.order_by(EmergencyAlert.created_at.desc()).all()
    return rows


@router.get("/by-session/{session_id}", response_model=ReportOut)
def get_report_by_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Report:
    report = (
        query_reports_for_current_user(db=db, current_user_id=int(current_user.id))
        .filter(Report.session_id == session_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Report:
    report = query_reports_for_current_user(db=db, current_user_id=int(current_user.id)).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}/frontend")
def get_report_frontend_shape(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    report = query_reports_for_current_user(db=db, current_user_id=int(current_user.id)).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.report_json


@router.get("/session/{session_id}/recommendations", response_model=list[InterventionRecommendationOut])
def list_session_recommendations(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[InterventionRecommendation]:
    session = (
        db.query(EvaluationSession)
        .filter(EvaluationSession.id == session_id, EvaluationSession.user_id == int(current_user.id))
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    rows = (
        db.query(InterventionRecommendation)
        .filter(
            InterventionRecommendation.session_id == session_id,
            or_(
                InterventionRecommendation.user_id == int(current_user.id),
                InterventionRecommendation.user_id.is_(None),
            ),
        )
        .order_by(InterventionRecommendation.priority.asc(), InterventionRecommendation.id.asc())
        .all()
    )
    return rows
