#!/usr/bin/env python3
"""
Assessment pipeline simulation and DB validation.

What it verifies:
1) Backend health and DB connectivity
2) Register + login user via JSON API (or use provided user_id)
3) Create evaluation session via JSON API
4) Submit questionnaire answers via JSON API
5) Report + questionnaire rows are generated and report JSON is retrievable
6) Simulate multimodal ingestion into DB tables
7) Validate all related rows exist and are linked by session_id

Usage:
  python scripts/test_assessment_pipeline.py --base-url http://127.0.0.1:8000 --template-code phq9
  python scripts/test_assessment_pipeline.py --user-id 1 --template-code sds
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.session import SessionLocal
from app.models.evaluation import FeatureSnapshot, MediaAsset, ModalityQualityMetric, ModelInferenceResult
from app.models.questionnaire import QuestionnaireAnswer, QuestionnaireResult, QuestionnaireTemplate
from app.models.report import InterventionRecommendation, Report


ANSWERS_BY_TEMPLATE: dict[str, list[int]] = {
    "phq9": [2, 2, 3, 2, 1, 2, 1, 1, 0],
    "sds": [3, 2, 2, 3, 2, 2, 3, 2, 3, 3, 2, 2, 3, 2, 3, 2, 2, 2, 3, 2],
    "ais": [2, 2, 1, 2, 2, 1, 2, 1],
    "pss": [3, 2, 3, 1, 2, 3, 1, 1, 2, 3],
}


def request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 10.0,
) -> tuple[int, dict[str, Any], str]:
    body = None
    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)

    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = Request(url=url, data=body, headers=req_headers, method=method.upper())

    try:
        with urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read().decode("utf-8")
            data = json.loads(raw) if raw else {}
            return resp.status, data, content_type
    except HTTPError as exc:
        content_type = exc.headers.get("Content-Type", "") if exc.headers else ""
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            data = {"raw": raw}
        return exc.code, data, content_type
    except URLError as exc:
        raise RuntimeError(f"Network error when calling {url}: {exc}") from exc


def assert_step(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def assert_json_response(content_type: str, step: str) -> None:
    assert_step(
        "application/json" in content_type.lower(),
        f"{step} did not return JSON content-type, got: {content_type}",
    )


def is_username_exists_error(status: int, data: dict[str, Any]) -> bool:
    detail = str(data.get("detail", ""))
    return status in (400, 409) and "username already exists" in detail.lower()


def register_user(base_url: str, username: str, password: str) -> None:
    phone = f"13{random.randint(100000000, 999999999)}"
    payload = {
        "username": username,
        "phone": phone,
        "password": password,
        "confirm_password": password,
        "nickname": "pipeline_tester",
        "gender": "other",
        "age_range": "25-34",
    }
    print(f"[JSON][REQ] POST /api/v1/auth/register {json.dumps(payload, ensure_ascii=False)}")
    status, data, content_type = request_json("POST", f"{base_url}/api/v1/auth/register", payload=payload)
    assert_json_response(content_type, "POST /api/v1/auth/register")
    if status == 201:
        print(f"[STEP] register -> {status}, username={username}")
        return
    if is_username_exists_error(status, data):
        print(f"[INFO] User {username} already exists, continue with login.")
        return
    raise RuntimeError(f"register failed: {status} {data}")


def login_user(base_url: str, username: str, password: str) -> tuple[str, int]:
    payload = {"username": username, "password": password}
    print(f"[JSON][REQ] POST /api/v1/auth/login {json.dumps(payload, ensure_ascii=False)}")
    status, data, content_type = request_json("POST", f"{base_url}/api/v1/auth/login", payload=payload)
    assert_json_response(content_type, "POST /api/v1/auth/login")
    assert_step(status == 200, f"login failed: {status} {data}")
    token = data.get("access_token")
    assert_step(bool(token), f"login response missing access_token: {data}")
    user_id = data.get("user", {}).get("id")
    assert_step(user_id is not None, f"login response missing user.id: {data}")
    print(f"[STEP] login -> {status}, token_type={data.get('token_type')}")
    return str(token), int(user_id)


def simulate_multimodal_rows(session_id: int) -> dict[str, int]:
    db = SessionLocal()
    try:
        db.add_all(
            [
                MediaAsset(
                    session_id=session_id,
                    media_type="video",
                    file_url=f"https://mock.local/session/{session_id}/face.mp4",
                    file_name="face.mp4",
                    file_size=2_560_000,
                    duration_seconds=28,
                    format="mp4",
                    upload_status="uploaded",
                ),
                MediaAsset(
                    session_id=session_id,
                    media_type="audio",
                    file_url=f"https://mock.local/session/{session_id}/voice.wav",
                    file_name="voice.wav",
                    file_size=860_000,
                    duration_seconds=30,
                    format="wav",
                    upload_status="uploaded",
                ),
                ModalityQualityMetric(
                    session_id=session_id,
                    modality="face",
                    quality_score=91.5,
                    issue_tags=["stable_light"],
                    metrics={"face_detect_ratio": 0.97, "blur_score": 0.05},
                ),
                ModalityQualityMetric(
                    session_id=session_id,
                    modality="voice",
                    quality_score=88.4,
                    issue_tags=["normal"],
                    metrics={"snr": 24.2, "silence_ratio": 0.11},
                ),
                FeatureSnapshot(
                    session_id=session_id,
                    modality="face",
                    feature_summary={"expression_activity": 0.41, "gaze_stability": 0.82},
                    feature_file_url=f"https://mock.local/session/{session_id}/face_features.json",
                ),
                FeatureSnapshot(
                    session_id=session_id,
                    modality="voice",
                    feature_summary={"speech_rate": 3.7, "pitch_variation": 0.33},
                    feature_file_url=f"https://mock.local/session/{session_id}/voice_features.json",
                ),
                ModelInferenceResult(
                    session_id=session_id,
                    model_name="mock-fusion-v1",
                    fusion_strategy="weighted_sum",
                    face_score=0.43,
                    voice_score=0.38,
                    scale_score=0.52,
                    text_score=0.45,
                    fused_score=0.46,
                    risk_level="medium",
                    confidence_score=0.89,
                    modality_weights={"face": 0.2, "voice": 0.2, "scale": 0.4, "text": 0.2},
                    missing_modalities=[],
                    # Keep JSON-compatible text so it works even when DB column is JSON.
                    explanation=json.dumps(
                        {
                            "summary": "Simulated multimodal inference for integration testing.",
                            "source": "assessment_pipeline_script",
                        },
                        ensure_ascii=False,
                    ),
                ),
            ]
        )
        db.commit()

        media_cnt = db.query(MediaAsset).filter(MediaAsset.session_id == session_id).count()
        quality_cnt = db.query(ModalityQualityMetric).filter(ModalityQualityMetric.session_id == session_id).count()
        feature_cnt = db.query(FeatureSnapshot).filter(FeatureSnapshot.session_id == session_id).count()
        infer_cnt = db.query(ModelInferenceResult).filter(ModelInferenceResult.session_id == session_id).count()

        return {
            "media_assets": media_cnt,
            "modality_quality_metrics": quality_cnt,
            "feature_snapshots": feature_cnt,
            "model_inference_results": infer_cnt,
        }
    finally:
        db.close()


def validate_rows(session_id: int, report_id: int, template_code: str, expected_answer_count: int) -> dict[str, int]:
    db = SessionLocal()
    try:
        template = db.query(QuestionnaireTemplate).filter(QuestionnaireTemplate.code == template_code).first()
        assert_step(template is not None, f"template not found by code={template_code}")

        answer_cnt = db.query(QuestionnaireAnswer).filter(QuestionnaireAnswer.session_id == session_id).count()
        result_cnt = (
            db.query(QuestionnaireResult)
            .filter(
                QuestionnaireResult.session_id == session_id,
                QuestionnaireResult.template_id == template.id,
            )
            .count()
        )
        report_cnt = (
            db.query(Report)
            .filter(Report.id == report_id, Report.session_id == session_id)
            .count()
        )
        rec_cnt = db.query(InterventionRecommendation).filter(InterventionRecommendation.session_id == session_id).count()

        assert_step(
            answer_cnt == expected_answer_count,
            f"questionnaire answer count mismatch: expected={expected_answer_count}, got={answer_cnt}",
        )
        assert_step(result_cnt == 1, f"questionnaire result missing or duplicated: {result_cnt}")
        assert_step(report_cnt == 1, f"report missing by report_id/session_id: {report_cnt}")
        assert_step(rec_cnt >= 1, f"recommendations not generated: {rec_cnt}")

        return {
            "questionnaire_answers": answer_cnt,
            "questionnaire_results": result_cnt,
            "reports": report_cnt,
            "intervention_recommendations": rec_cnt,
        }
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate assessment + multimodal ingestion and validate DB rows.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Backend base URL")
    parser.add_argument("--template-code", default="phq9", choices=["phq9", "sds", "ais", "pss"])
    parser.add_argument("--username", default="test001", help="Fixed username used for testing.")
    parser.add_argument(
        "--user-id",
        type=int,
        default=None,
        help="Existing user id override. If omitted, use logged-in user's id.",
    )
    parser.add_argument("--password", default="12345678", help="Password for auto-created test user")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    answers = ANSWERS_BY_TEMPLATE[args.template_code]

    print(f"[INFO] Base URL: {base_url}")
    print(f"[INFO] Template: {args.template_code}, answer_count={len(answers)}")

    status, health, content_type = request_json("GET", f"{base_url}/api/v1/health/db")
    print(f"[STEP] GET /api/v1/health/db -> {status} {health}")
    assert_json_response(content_type, "GET /api/v1/health/db")
    assert_step(status == 200 and health.get("status") == "ok", f"health/db failed: {status} {health}")

    register_user(base_url=base_url, username=args.username, password=args.password)
    token, login_user_id = login_user(base_url=base_url, username=args.username, password=args.password)
    user_id = args.user_id if args.user_id is not None else login_user_id

    print(f"[INFO] username={args.username}, user_id={user_id}")
    auth_headers = {"Authorization": f"Bearer {token}"} if token else None

    create_payload = {
        "user_id": user_id,
        "screening_type": args.template_code,
        "used_modalities": ["face", "voice", "scale", "text"],
        "missing_modalities": [],
    }
    print(f"[JSON][REQ] POST /api/v1/evaluations/sessions {json.dumps(create_payload, ensure_ascii=False)}")
    status, created, content_type = request_json(
        "POST",
        f"{base_url}/api/v1/evaluations/sessions",
        payload=create_payload,
        headers=auth_headers,
    )
    print(f"[STEP] POST /api/v1/evaluations/sessions -> {status} {created}")
    assert_json_response(content_type, "POST /api/v1/evaluations/sessions")
    assert_step(status == 201, f"create session failed: {status} {created}")
    session_id = int(created["session_id"])

    submit_payload = {
        "template_code": args.template_code,
        "answers": [{"question_no": idx + 1, "answer_value": val} for idx, val in enumerate(answers)],
        "context": {
            "recent_stress_level": "medium",
            "sleep_status": "normal",
            "appetite_status": "normal",
            "self_evaluation": "stable",
            "social_avoidance_level": "low",
            "remark": "pipeline simulation",
        },
        "confidence_score": 0.91,
    }
    print(
        f"[JSON][REQ] POST /api/v1/evaluations/sessions/{session_id}/submit "
        f"{json.dumps(submit_payload, ensure_ascii=False)}"
    )
    status, submit_resp, content_type = request_json(
        "POST",
        f"{base_url}/api/v1/evaluations/sessions/{session_id}/submit",
        payload=submit_payload,
        headers=auth_headers,
    )
    print(f"[STEP] POST /api/v1/evaluations/sessions/{session_id}/submit -> {status} {submit_resp}")
    assert_json_response(content_type, f"POST /api/v1/evaluations/sessions/{session_id}/submit")
    assert_step(status == 200, f"submit evaluation failed: {status} {submit_resp}")
    report_id = int(submit_resp["report_id"])

    status, report_front, content_type = request_json(
        "GET",
        f"{base_url}/api/v1/reports/{report_id}/frontend",
        headers=auth_headers,
    )
    print(
        f"[STEP] GET /api/v1/reports/{report_id}/frontend -> "
        f"{status} {{'type': {report_front.get('type')}, 'total': {report_front.get('total')}, 'level': {report_front.get('level')}}}"
    )
    assert_json_response(content_type, f"GET /api/v1/reports/{report_id}/frontend")
    assert_step(status == 200, f"get frontend report failed: {status} {report_front}")

    mm_counts = simulate_multimodal_rows(session_id=session_id)
    print(f"[STEP] simulated multimodal insert -> {mm_counts}")

    core_counts = validate_rows(
        session_id=session_id,
        report_id=report_id,
        template_code=args.template_code,
        expected_answer_count=len(answers),
    )
    print(f"[STEP] validated questionnaire/report rows -> {core_counts}")

    assert_step(mm_counts["media_assets"] >= 2, f"media_assets not inserted: {mm_counts}")
    assert_step(mm_counts["modality_quality_metrics"] >= 2, f"modality_quality_metrics not inserted: {mm_counts}")
    assert_step(mm_counts["feature_snapshots"] >= 2, f"feature_snapshots not inserted: {mm_counts}")
    assert_step(mm_counts["model_inference_results"] >= 1, f"model_inference_results not inserted: {mm_counts}")

    print("[PASS] Assessment + report + multimodal DB simulation passed.")
    print(
        f"[SUMMARY] session_id={session_id}, report_id={report_id}, "
        f"template={args.template_code}, answers={len(answers)}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        raise SystemExit(1)
