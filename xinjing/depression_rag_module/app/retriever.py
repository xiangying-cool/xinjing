from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from app.config import Settings
from app.indexer import LocalHybridIndex
from app.internal_types import Chunk
from app.reranker import CrossEncoderReranker
from app.schemas import RetrievalFilters


@dataclass
class Candidate:
    chunk: Chunk
    fused_score: float = 0.0
    dense_rank: Optional[int] = None
    sparse_rank: Optional[int] = None
    dense_score: Optional[float] = None
    sparse_score: Optional[float] = None
    rerank_score: Optional[float] = None


class HybridRetriever:
    def __init__(
        self,
        index: LocalHybridIndex,
        settings: Settings,
        reranker: CrossEncoderReranker | None = None,
    ) -> None:
        self.index = index
        self.settings = settings
        self.reranker = reranker

    def _matches_filters(self, chunk: Chunk, filters: RetrievalFilters | None) -> bool:
        if filters is None:
            return True
        if filters.categories and chunk.category not in filters.categories:
            return False
        if filters.source_names and chunk.source_name not in filters.source_names:
            return False
        return True

    def _rrf(self, rank: int) -> float:
        return 1.0 / float(self.settings.rrf_k + rank)

    def retrieve(
        self,
        query: str,
        top_k: int,
        filters: RetrievalFilters | None = None,
        preferred_category: str | None = None,
    ) -> List[Candidate]:
        dense = self.index.search_dense(query, self.settings.dense_top_k)
        sparse = self.index.search_sparse(query, self.settings.sparse_top_k)

        candidates: Dict[int, Candidate] = {}

        def get_or_create(idx: int) -> Candidate:
            if idx not in candidates:
                candidates[idx] = Candidate(chunk=self.index.chunks[idx])
            return candidates[idx]

        for rank, (idx, score) in enumerate(dense, start=1):
            chunk = self.index.chunks[idx]
            if not self._matches_filters(chunk, filters):
                continue
            cand = get_or_create(idx)
            cand.dense_rank = rank
            cand.dense_score = score
            cand.fused_score += self._rrf(rank)

        for rank, (idx, score) in enumerate(sparse, start=1):
            chunk = self.index.chunks[idx]
            if not self._matches_filters(chunk, filters):
                continue
            cand = get_or_create(idx)
            cand.sparse_rank = rank
            cand.sparse_score = score
            cand.fused_score += self._rrf(rank)

        ranked = list(candidates.values())
        for cand in ranked:
            cand.fused_score += cand.chunk.priority * 0.005
            if preferred_category and cand.chunk.category == preferred_category:
                cand.fused_score += 0.05

        ranked.sort(key=lambda x: x.fused_score, reverse=True)

        if self.settings.enable_rerank and self.reranker is not None and ranked:
            pool = ranked[: self.settings.rerank_candidates]
            scores = self.reranker.score(query, [item.chunk.content for item in pool])
            for item, score in zip(pool, scores):
                item.rerank_score = score
            pool.sort(key=lambda x: ((x.rerank_score if x.rerank_score is not None else -1e9), x.fused_score), reverse=True)
            ranked = pool + ranked[self.settings.rerank_candidates :]

        return self._pack_diverse_contexts(ranked, top_k=top_k)

    def _pack_diverse_contexts(self, ranked: List[Candidate], top_k: int) -> List[Candidate]:
        result: List[Candidate] = []
        used_chunk_ids = set()
        used_doc_ids = set()
        total_chars = 0

        for cand in ranked:
            if cand.chunk.chunk_id in used_chunk_ids:
                continue
            if len(result) >= top_k:
                break
            if total_chars >= self.settings.max_context_chars:
                break

            # Prefer diversity across documents, but allow a second chunk from the same doc if needed.
            if cand.chunk.doc_id in used_doc_ids and len(result) < max(2, top_k // 2):
                continue

            result.append(cand)
            used_chunk_ids.add(cand.chunk.chunk_id)
            used_doc_ids.add(cand.chunk.doc_id)
            total_chars += len(cand.chunk.content)

        if len(result) < top_k:
            for cand in ranked:
                if cand.chunk.chunk_id in used_chunk_ids:
                    continue
                if len(result) >= top_k:
                    break
                if total_chars >= self.settings.max_context_chars:
                    break
                result.append(cand)
                used_chunk_ids.add(cand.chunk.chunk_id)
                total_chars += len(cand.chunk.content)

        return result
