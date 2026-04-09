from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.schemas import HealthResponse, QueryRequest, QueryResponse, RebuildIndexResponse
from app.service import RAGService


settings = get_settings()
rag_service = RAGService(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    rag_service.startup()
    yield


app = FastAPI(
    title=settings.app_name,
    version='0.1.0',
    description='Local RAG module for mental-health support digital human projects.',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origin_list,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health', response_model=HealthResponse)
def health() -> HealthResponse:
    return rag_service.health()


@app.post(f'{settings.api_prefix}/index/rebuild', response_model=RebuildIndexResponse)
def rebuild_index() -> RebuildIndexResponse:
    try:
        return rag_service.rebuild_index()
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post(f'{settings.api_prefix}/rag/retrieve', response_model=QueryResponse)
def retrieve(request: QueryRequest) -> QueryResponse:
    try:
        return rag_service.retrieve(request, generate_answer=False)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post(f'{settings.api_prefix}/rag/answer', response_model=QueryResponse)
def answer(request: QueryRequest) -> QueryResponse:
    try:
        return rag_service.retrieve(request, generate_answer=True)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc
