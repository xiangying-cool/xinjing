from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Optional
from uuid import uuid4

import joblib
import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.evaluation import EvaluationSession
from app.models.report import InterventionRecommendation, Report
from app.models.user import User

router = APIRouter(prefix="/depression-predict", tags=["depression-predict"])

ML_DIR = Path(__file__).resolve().parents[4] / "ml_models"


@lru_cache(maxsize=1)
def _load_models():
    """加载模型（进程内只加载一次）"""
    try:
        import tensorflow as tf  # noqa: F401 – lazy import to avoid startup cost when TF not needed
        scaler = joblib.load(ML_DIR / "scaler.pkl")
        keras_model = tf.keras.models.load_model(str(ML_DIR / "keras_model.h5"))
        return scaler, keras_model
    except Exception as exc:
        raise RuntimeError(f"ML模型加载失败: {exc}") from exc


# ── 请求 / 响应 Schema ────────────────────────────────────────────────────────

class DepressionPredictRequest(BaseModel):
    age: float
    work_pressure: float
    job_satisfaction: float
    sleep_duration: float
    work_or_study_hours: float
    financial_stress: float
    gender: str                  # "Male" | "Female"
    working_status: str          # "Working Professional" | "Student"
    suicidal_thoughts: str       # "Yes" | "No"
    dietary_habits: str          # "Healthy" | "Moderate" | "Unhealthy"
    family_history: str          # "Yes" | "No"


class DepressionPredictResponse(BaseModel):
    depressed: bool
    prediction: str              # "可能存在抑郁" | "暂无抑郁倾向"
    probability: float
    motivation: str
    report_id: Optional[int] = None


# ── 推理逻辑（与 streamlit_app.py 保持一致）────────────────────────────────────

def _preprocess(req: DepressionPredictRequest) -> pd.DataFrame:
    working_professional = 1 if req.working_status == "Working Professional" else 0
    suicidal = 1 if req.suicidal_thoughts == "Yes" else 0
    family = 1 if req.family_history == "Yes" else 0

    if req.dietary_habits == "Healthy":
        diet_moderate, diet_unhealthy = 0, 0
    elif req.dietary_habits == "Moderate":
        diet_moderate, diet_unhealthy = 1, 0
    else:
        diet_moderate, diet_unhealthy = 0, 1

    # 列名与 scaler 训练时保持一致（11 个特征，不含 Gender_Male）
    data = {
        "Age": [req.age],
        "Sleep_Duration": [req.sleep_duration],
        "Work/Study_Hours": [req.work_or_study_hours],
        "Financial_Stress": [req.financial_stress],
        "Study/job_Satisfaction": [req.job_satisfaction],
        "Academic/work_Pressure": [req.work_pressure],
        "Working_Professional_or_Student_Working_Professional": [working_professional],
        "Dietary_Habits_Moderate": [diet_moderate],
        "Dietary_Habits_Unhealthy": [diet_unhealthy],
        "Have_you_ever_had_suicidal_thoughts_?_Yes": [suicidal],
        "Family_History_of_Mental_Illness_Yes": [family],
    }
    return pd.DataFrame(data)


# ── 端点 ──────────────────────────────────────────────────────────────────────

@router.post("", response_model=DepressionPredictResponse)
def predict_depression(
    payload: DepressionPredictRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        scaler, keras_model = _load_models()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    input_df = _preprocess(payload)
    scaled = scaler.transform(input_df)
    prob = float(keras_model.predict(scaled, verbose=0)[0][0])
    depressed = prob > 0.65

    if depressed:
        prediction = "可能存在抑郁"
        motivation = (
            "根据您填写的信息，模型检测到您可能正在经历抑郁相关症状。"
            "请记住，您并不孤单，专业帮助近在眼前。"
            "建议您与信任的家人朋友沟通，或预约心理咨询师进一步评估。"
        )
        level = "阳性"
        color = "#e74c3c"
    else:
        prediction = "暂无抑郁倾向"
        motivation = (
            "根据您填写的信息，模型未检测到明显抑郁风险。"
            "继续保持健康的生活方式、规律睡眠和积极的社交互动，"
            "定期关注自己的情绪变化，有助于维护长期心理健康。"
        )
        level = "阴性"
        color = "#27ae60"

    # ── 保存报告 ──────────────────────────────────────────────────────────────
    now = datetime.utcnow()
    session = EvaluationSession(
        session_no=str(uuid4()),
        user_id=current_user.id,
        status="completed",
        screening_type="ai_predict",
        start_time=now,
        end_time=now,
        duration_seconds=0,
        used_modalities=["text"],
        missing_modalities=[],
        overall_risk_level=level,
    )
    db.add(session)
    db.flush()

    report_json = {
        "type": "ai_predict",
        "scale": "AI抑郁预测",
        "total": round(prob * 100),
        "max": 100,
        "level": level,
        "color": color,
        "desc": motivation,
        "date": now.strftime("%Y-%m-%d %H:%M:%S"),
        "depressed": depressed,
        "probability": prob,
        "inputs": payload.model_dump(),
    }
    report = Report(
        session_id=session.id,
        user_id=current_user.id,
        report_type="ai_predict",
        report_json=report_json,
    )
    db.add(report)

    recs_text = (
        ["建议寻求专业心理援助", "保持规律作息，增加有氧运动", "减少独处时间，主动联系亲友"]
        if depressed else
        ["继续维持健康生活方式", "定期进行心理健康自测", "保持适度运动与良好睡眠"]
    )
    db.flush()
    for i, text in enumerate(recs_text):
        db.add(InterventionRecommendation(
            session_id=session.id,
            user_id=current_user.id,
            recommendation_type="ai_predict",
            priority=i + 1,
            content=text,
        ))

    db.commit()
    db.refresh(report)

    return DepressionPredictResponse(
        depressed=depressed,
        prediction=prediction,
        probability=round(prob, 4),
        motivation=motivation,
        report_id=report.id,
    )
