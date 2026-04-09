from __future__ import annotations

import copy
from typing import Dict, List

from app.chunker import split_documents
from app.config import Settings
from app.embeddings import EmbeddingEncoder
from app.indexer import LocalHybridIndex
from app.internal_types import Chunk
from app.llm import OpenAICompatibleLLM
from app.loader import load_documents_from_dir
from app.prompting import build_prompt_bundle
from app.retriever import Candidate, HybridRetriever
from app.reranker import CrossEncoderReranker
from app.safety import detect_risk
from app.schemas import (
    HealthResponse,
    QueryRequest,
    QueryResponse,
    RebuildIndexResponse,
    RetrievedChunk,
)
from app.utils import normalize_query, timed


FOLLOWUP_HINTS = ('这个', '那怎么办', '那我呢', '这种情况', '这样的话', '然后呢', '怎么办')


class RAGService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.encoder = EmbeddingEncoder(
            model_name_or_path=settings.embedding_model,
            device=settings.embedding_device,
            batch_size=settings.embed_batch_size,
        )
        self.reranker = None
        if settings.enable_rerank:
            self.reranker = CrossEncoderReranker(
                model_name_or_path=settings.rerank_model,
                device=settings.rerank_device,
            )
        self.index = LocalHybridIndex(storage_dir=settings.storage_dir, encoder=self.encoder)
        self.retriever = HybridRetriever(index=self.index, settings=settings, reranker=self.reranker)
        self.llm = OpenAICompatibleLLM(settings) if (settings.enable_llm_generation or settings.enable_query_rewrite or settings.enable_multi_query) else None

    def startup(self) -> None:
        try:
            self.index.load()
        except FileNotFoundError:
            if not self.settings.auto_rebuild_if_missing:
                raise
            self.rebuild_index()

    def rebuild_index(self) -> RebuildIndexResponse:
        docs = load_documents_from_dir(self.settings.knowledge_dir)
        chunks = split_documents(docs, chunk_size=self.settings.chunk_size, overlap=self.settings.chunk_overlap)
        stats = self.index.build(chunks)
        return RebuildIndexResponse(
            chunk_count=stats['chunk_count'],
            doc_count=len(docs),
            embedding_dimension=stats['embedding_dimension'],
            storage_dir=stats['storage_dir'],
        )

    def health(self) -> HealthResponse:
        chunk_count = len(self.index.chunks)
        return HealthResponse(
            index_ready=self.index.ready,
            chunk_count=chunk_count,
            llm_enabled=self.settings.enable_llm_generation,
            embedding_model=self.settings.embedding_model,
            rerank_model=self.settings.rerank_model,
        )

    def _condense_query(self, request: QueryRequest, normalized_query: str) -> str:
        if len(normalized_query) > 10:
            return normalized_query
        history_user_turns = [m.content.strip() for m in request.chat_history if m.role == 'user' and m.content.strip()]
        if not history_user_turns:
            return normalized_query
        if any(hint in normalized_query for hint in FOLLOWUP_HINTS) or len(normalized_query) <= 6:
            return f'{history_user_turns[-1]} {normalized_query}'.strip()
        return normalized_query

    def _rewrite_queries(self, request: QueryRequest, normalized_query: str, latency_ms: Dict[str, float]) -> List[str]:
        queries = [normalized_query]
        if self.llm is None:
            return queries
        if not (self.settings.enable_query_rewrite or self.settings.enable_multi_query):
            return queries

        history = [m.model_dump() for m in request.chat_history]
        with timed(latency_ms, 'query_rewrite'):
            generated = self.llm.rewrite_queries(normalized_query, history)
        for item in generated:
            item = normalize_query(item)
            if item and item not in queries:
                queries.append(item)
        return queries[:3]

    def _retrieve_from_queries(self, queries: List[str], request: QueryRequest, preferred_category: str | None) -> List[Candidate]:
        target_k = request.top_k or self.settings.final_top_k
        merged: Dict[str, Candidate] = {}
        filters = request.filters

        for qidx, query in enumerate(queries):
            partial = self.retriever.retrieve(
                query=query,
                top_k=max(target_k * 2, self.settings.final_top_k),
                filters=filters,
                preferred_category=preferred_category,
            )
            for rank, cand in enumerate(partial, start=1):
                key = cand.chunk.chunk_id
                if key not in merged:
                    new_cand = copy.deepcopy(cand)
                    new_cand.fused_score += 0.002 * (len(queries) - qidx)
                    merged[key] = new_cand
                else:
                    existing = merged[key]
                    existing.fused_score = max(existing.fused_score, cand.fused_score)
                    if cand.rerank_score is not None:
                        existing.rerank_score = max(existing.rerank_score or cand.rerank_score, cand.rerank_score)
                    if cand.dense_rank is not None:
                        existing.dense_rank = min(existing.dense_rank or cand.dense_rank, cand.dense_rank)
                    if cand.sparse_rank is not None:
                        existing.sparse_rank = min(existing.sparse_rank or cand.sparse_rank, cand.sparse_rank)
                    if cand.dense_score is not None:
                        existing.dense_score = max(existing.dense_score or cand.dense_score, cand.dense_score)
                    if cand.sparse_score is not None:
                        existing.sparse_score = max(existing.sparse_score or cand.sparse_score, cand.sparse_score)

        ranked = list(merged.values())
        ranked.sort(
            key=lambda x: (
                x.rerank_score if x.rerank_score is not None else -1e9,
                x.fused_score,
            ),
            reverse=True,
        )
        return self.retriever._pack_diverse_contexts(ranked, top_k=target_k)

    def retrieve(self, request: QueryRequest, generate_answer: bool = False) -> QueryResponse:
        latency_ms: Dict[str, float] = {}
        with timed(latency_ms, 'normalize_query'):
            normalized_query = normalize_query(request.query)
            condensed_query = self._condense_query(request, normalized_query)

        history_user_texts = [m.content for m in request.chat_history if m.role == 'user']
        with timed(latency_ms, 'risk_assessment'):
            risk = detect_risk(condensed_query, history_user_texts, request.user_state)

        rewritten_queries = self._rewrite_queries(request, condensed_query, latency_ms)
        preferred_category = 'crisis' if risk.risk_level == 'high' else None

        with timed(latency_ms, 'retrieval'):
            candidates = self._retrieve_from_queries(rewritten_queries, request, preferred_category)

        chunks = [cand.chunk for cand in candidates]
        contexts = [
            RetrievedChunk(
                chunk_id=cand.chunk.chunk_id,
                doc_id=cand.chunk.doc_id,
                title=cand.chunk.title,
                category=cand.chunk.category,
                source_name=cand.chunk.source_name,
                source_url=cand.chunk.source_url,
                section=cand.chunk.section,
                content=cand.chunk.content,
                score=round(cand.fused_score, 6),
                dense_rank=cand.dense_rank,
                sparse_rank=cand.sparse_rank,
                rerank_score=round(cand.rerank_score, 6) if cand.rerank_score is not None else None,
            )
            for cand in candidates
        ]

        # 始终构建 prompt_bundle，因为 LLM 生成需要它
        # return_prompt_bundle 只控制是否在响应中返回
        with timed(latency_ms, 'prompt_build'):
            prompt_bundle = build_prompt_bundle(
                query=request.query,
                history=[m.model_dump() for m in request.chat_history],
                chunks=chunks,
                risk=risk,
            )

        answer = None
        if generate_answer:
            if risk.risk_level == 'high' and risk.fixed_reply:
                answer = risk.fixed_reply
            elif self.llm is None:
                answer = '当前服务未启用本地生成模型，请调用 /retrieve 接口并将 prompt_bundle 交给你们现有的 LLM。'
            else:
                with timed(latency_ms, 'generation'):
                    answer = self.llm.chat(prompt_bundle.system_prompt, prompt_bundle.user_prompt)
        
        # 如果不需要返回 prompt_bundle，则设为 None
        if not request.return_prompt_bundle:
            prompt_bundle = None

        latency_ms['total'] = round(sum(v for v in latency_ms.values()), 3)

        debug: Dict[str, object] = {}
        if request.debug:
            debug = {
                'condensed_query': condensed_query,
                'preferred_category': preferred_category,
                'matched_rules': risk.matched_rules,
                'top_context_ids': [ctx.chunk_id for ctx in contexts],
            }

        return QueryResponse(
            query=request.query,
            normalized_query=condensed_query,
            rewritten_queries=rewritten_queries,
            risk=risk,
            contexts=contexts,
            prompt_bundle=prompt_bundle,
            answer=answer,
            latency_ms=latency_ms,
            debug=debug,
        )
