from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.evaluation import EvaluationSession, SessionContextInfo
from app.models.questionnaire import (
    QuestionnaireAnswer,
    QuestionnaireQuestion,
    QuestionnaireResult,
    QuestionnaireTemplate,
)
from app.models.report import EmergencyAlert, InterventionRecommendation, Report
from app.models.user import User
from app.schemas.evaluation import (
    EvaluationSessionDetailOut,
    EvaluationSessionOut,
    CreateSessionRequest,
    CreateSessionResponse,
    SubmitEvaluationRequest,
    SubmitEvaluationResponse,
)
from app.services.scoring import build_default_recommendations, calculate_score

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


SCALE_NAME_MAP = {
    "phq9": "PHQ-9",
    "sds": "SDS",
    "ais": "AIS",
    "pss": "PSS",
}


@router.get("/sessions", response_model=list[EvaluationSessionOut])
def list_sessions(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[EvaluationSession]:
    rows = (
        db.query(EvaluationSession)
        .filter(EvaluationSession.user_id == int(current_user.id))
        .order_by(EvaluationSession.created_at.desc())
        .limit(limit)
        .all()
    )
    return rows


@router.get("/sessions/{session_id}", response_model=EvaluationSessionDetailOut)
def get_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EvaluationSessionDetailOut:
    session = db.query(EvaluationSession).filter(
        EvaluationSession.id == session_id,
        EvaluationSession.user_id == int(current_user.id),
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    context = db.query(SessionContextInfo).filter(SessionContextInfo.session_id == session_id).first()
    return EvaluationSessionDetailOut(session=session, context=context)


@router.post("/sessions", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CreateSessionResponse:
    now = datetime.utcnow()
    session = EvaluationSession(
        session_no=f"ES-{uuid4().hex[:12].upper()}",
        user_id=int(current_user.id),
        status="created",
        screening_type=payload.screening_type,
        start_time=now,
        used_modalities=payload.used_modalities or [],
        missing_modalities=payload.missing_modalities or [],
        degraded_inference=bool(payload.missing_modalities),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return CreateSessionResponse(
        session_id=session.id,
        session_no=session.session_no,
        status=session.status,
        screening_type=session.screening_type,
        start_time=session.start_time,
    )


@router.post("/sessions/{session_id}/submit", response_model=SubmitEvaluationResponse)
def submit_evaluation(
    session_id: int,
    payload: SubmitEvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmitEvaluationResponse:
    session = db.query(EvaluationSession).filter(
        EvaluationSession.id == session_id,
        EvaluationSession.user_id == int(current_user.id),
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    existing_report = db.query(Report).filter(Report.session_id == session_id).first()
    if existing_report:
        raise HTTPException(status_code=409, detail="Session already submitted")

    if not payload.answers:
        raise HTTPException(status_code=400, detail="Answers cannot be empty")

    # 校验答案数量与量表期望题数一致
    EXPECTED_QUESTION_COUNT = {"phq9": 9, "sds": 20, "ais": 8, "pss": 10}
    expected = EXPECTED_QUESTION_COUNT.get(payload.template_code)
    if expected is not None and len(payload.answers) != expected:
        raise HTTPException(
            status_code=400,
            detail=f"{payload.template_code.upper()} 量表需要 {expected} 道题的答案，收到 {len(payload.answers)} 道",
        )

    template = (
        db.query(QuestionnaireTemplate)
        .filter(QuestionnaireTemplate.code == payload.template_code, QuestionnaireTemplate.is_active == 1)
        .first()
    )
    if not template:
        template = QuestionnaireTemplate(
            code=payload.template_code,
            name=SCALE_NAME_MAP.get(payload.template_code, payload.template_code.upper()),
            description=f"Auto created template for {payload.template_code}",
            is_active=1,
        )
        db.add(template)
        db.flush()

    answer_list = sorted(payload.answers, key=lambda x: x.question_no)
    answer_values: list[int] = []
    for ans in answer_list:
        question = (
            db.query(QuestionnaireQuestion)
            .filter(
                QuestionnaireQuestion.template_id == template.id,
                QuestionnaireQuestion.question_no == ans.question_no,
            )
            .first()
        )
        if not question:
            question = QuestionnaireQuestion(
                template_id=template.id,
                question_no=ans.question_no,
                question_text=f"Question {ans.question_no}",
            )
            db.add(question)
            db.flush()

        answer = QuestionnaireAnswer(
            session_id=session.id,
            template_id=template.id,
            question_id=question.id,
            answer_value=ans.answer_value,
            answer_score=ans.answer_value,
        )
        db.add(answer)
        answer_values.append(ans.answer_value)

    if payload.context:
        context_row = SessionContextInfo(
            session_id=session.id,
            recent_stress_level=payload.context.recent_stress_level,
            sleep_status=payload.context.sleep_status,
            appetite_status=payload.context.appetite_status,
            self_evaluation=payload.context.self_evaluation,
            social_avoidance_level=payload.context.social_avoidance_level,
            remark=payload.context.remark,
        )
        db.add(context_row)

    score = calculate_score(payload.template_code, answer_values)

    q_result = QuestionnaireResult(
        session_id=session.id,
        template_id=template.id,
        total_score=score.total,
        severity_level=score.level,
        dimension_scores={},
    )
    db.add(q_result)

    report_payload = {
        "type": payload.template_code,
        "scale": SCALE_NAME_MAP.get(payload.template_code, payload.template_code.upper()),
        "total": score.total,
        "max": score.max_score,
        "level": score.level,
        "color": score.color,
        "desc": score.desc,
        "answers": answer_values,
        "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "confidence_score": payload.confidence_score,
    }
    report = Report(
        session_id=session.id,
        user_id=session.user_id,
        report_type="screening",
        report_json=report_payload,
    )
    db.add(report)
    db.flush()

    recommendations = build_default_recommendations(payload.template_code, score.level)
    for idx, text in enumerate(recommendations, start=1):
        db.add(
            InterventionRecommendation(
                session_id=session.id,
                user_id=session.user_id,
                recommendation_type="self_help",
                priority=idx,
                reason="rule_based",
                content=text,
            )
        )

    # ── 量表层风险预警 ──────────────────────────────────────────────────────────
    # PHQ-9 第 9 题阳性（自杀意念）→ 高风险
    if payload.template_code == "phq9" and len(answer_values) >= 9 and answer_values[8] > 0 and session.user_id:
        db.add(
            EmergencyAlert(
                user_id=session.user_id,
                session_id=session.id,
                source_type="assessment",
                alert_title="PHQ-9 自杀意念阳性",
                alert_content="PHQ-9 第 9 题出现阳性信号（自杀意念），建议立即联系专业心理支持或拨打危机热线。",
                risk_level="high",
                is_handled=0,
            )
        )
    # PHQ-9 重度抑郁（总分 ≥ 20）→ 高风险
    elif payload.template_code == "phq9" and score.total >= 20 and session.user_id:
        db.add(
            EmergencyAlert(
                user_id=session.user_id,
                session_id=session.id,
                source_type="assessment",
                alert_title="PHQ-9 重度抑郁风险",
                alert_content=f"PHQ-9 总分 {score.total}，达到重度抑郁标准，建议尽快寻求专业心理医生帮助。",
                risk_level="high",
                is_handled=0,
            )
        )
    # PHQ-9 中重度抑郁（总分 15–19）→ 中风险
    elif payload.template_code == "phq9" and score.total >= 15 and session.user_id:
        db.add(
            EmergencyAlert(
                user_id=session.user_id,
                session_id=session.id,
                source_type="assessment",
                alert_title="PHQ-9 中重度抑郁风险",
                alert_content=f"PHQ-9 总分 {score.total}，存在中重度抑郁症状，建议尽快寻求专业心理咨询。",
                risk_level="medium",
                is_handled=0,
            )
        )
    # SDS 重度抑郁（标准分 > 72）→ 高风险
    elif payload.template_code == "sds" and score.level == "重度抑郁" and session.user_id:
        db.add(
            EmergencyAlert(
                user_id=session.user_id,
                session_id=session.id,
                source_type="assessment",
                alert_title="SDS 重度抑郁风险",
                alert_content=f"SDS 标准分 {score.total}，存在重度抑郁症状，建议尽快寻求专业心理医生帮助。",
                risk_level="high",
                is_handled=0,
            )
        )

    session.status = "done"
    session.end_time = datetime.utcnow()
    session.duration_seconds = int((session.end_time - session.start_time).total_seconds())
    session.confidence_score = payload.confidence_score
    session.overall_risk_level = score.level

    db.commit()

    return SubmitEvaluationResponse(
        report_id=report.id,
        session_id=session.id,
        total_score=score.total,
        risk_level=score.level,
        confidence_score=float(payload.confidence_score) if payload.confidence_score is not None else None,
    )
