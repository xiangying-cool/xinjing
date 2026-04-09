from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.db import base  # noqa: F401
from app.db.session import SessionLocal, engine
from app.models import *  # noqa: F401,F403
from app.services.bootstrap import seed_questionnaire_templates

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    base.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        try:
            seed_questionnaire_templates(db)
            db.commit()
        except Exception as exc:  # pragma: no cover - defensive startup guard
            db.rollback()
            logger.warning("Questionnaire bootstrap skipped due to startup error: %s", exc)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8010",
        "http://127.0.0.1:8010",
    ],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True,
)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running"}


app.include_router(api_router, prefix="/api/v1")

# Keep plain /health for quick checks
@app.get("/health", tags=["health"])
def global_health() -> dict[str, str]:
    return {"status": "ok"}
