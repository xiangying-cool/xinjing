import logging

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.models.questionnaire import QuestionnaireQuestion, QuestionnaireTemplate

logger = logging.getLogger(__name__)


TEMPLATES = {
    "phq9": {
        "name": "PHQ-9",
        "questions": 9,
    },
    "sds": {
        "name": "SDS",
        "questions": 20,
    },
    "ais": {
        "name": "AIS",
        "questions": 8,
    },
    "pss": {
        "name": "PSS",
        "questions": 10,
    },
}


def seed_questionnaire_templates(db: Session) -> None:
    # If external database schema does not match ORM model,
    # skip bootstrap instead of crashing whole app startup.
    inspector = inspect(db.bind)
    for model in (QuestionnaireTemplate, QuestionnaireQuestion):
        model_columns = set(model.__table__.columns.keys())
        try:
            db_columns = {col["name"] for col in inspector.get_columns(model.__tablename__)}
        except Exception as exc:  # pragma: no cover - defensive startup guard
            logger.warning("Skip questionnaire bootstrap: cannot inspect table '%s': %s", model.__tablename__, exc)
            return

        missing = sorted(model_columns - db_columns)
        if missing:
            logger.warning(
                "Skip questionnaire bootstrap: table '%s' missing columns %s; please align DB schema.",
                model.__tablename__,
                missing,
            )
            return

    for code, cfg in TEMPLATES.items():
        tpl = db.query(QuestionnaireTemplate).filter(QuestionnaireTemplate.code == code).first()
        if not tpl:
            tpl = QuestionnaireTemplate(
                code=code,
                name=cfg["name"],
                description=f"{cfg['name']} auto seeded template",
                is_active=1,
            )
            db.add(tpl)
            db.flush()

        existing_count = (
            db.query(QuestionnaireQuestion)
            .filter(QuestionnaireQuestion.template_id == tpl.id)
            .count()
        )
        if existing_count >= cfg["questions"]:
            continue

        existing_nos = {
            q_no
            for (q_no,) in db.query(QuestionnaireQuestion.question_no)
            .filter(QuestionnaireQuestion.template_id == tpl.id)
            .all()
        }
        for no in range(1, cfg["questions"] + 1):
            if no in existing_nos:
                continue
            db.add(
                QuestionnaireQuestion(
                    template_id=tpl.id,
                    question_no=no,
                    question_text=f"{cfg['name']} Question {no}",
                )
            )
