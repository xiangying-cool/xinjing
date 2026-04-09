from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, List, Tuple

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

from app.embeddings import EmbeddingEncoder
from app.internal_types import Chunk
from app.tokenizer import tokenize_zh
from app.utils import dump_json, ensure_dir, load_json


class LocalHybridIndex:
    def __init__(self, storage_dir: str, encoder: EmbeddingEncoder) -> None:
        self.storage_dir = Path(storage_dir)
        self.encoder = encoder
        self.chunks: List[Chunk] = []
        self.faiss_index: faiss.Index | None = None
        self.bm25: BM25Okapi | None = None
        self.embedding_dim: int = 0

    @property
    def chunks_path(self) -> Path:
        return self.storage_dir / 'chunks.json'

    @property
    def meta_path(self) -> Path:
        return self.storage_dir / 'meta.json'

    @property
    def faiss_path(self) -> Path:
        return self.storage_dir / 'index.faiss'

    @property
    def bm25_path(self) -> Path:
        return self.storage_dir / 'bm25.pkl'

    def build(self, chunks: List[Chunk]) -> Dict[str, Any]:
        ensure_dir(str(self.storage_dir))
        self.chunks = chunks
        texts = [chunk.content for chunk in chunks]
        embeddings = self.encoder.encode(texts)
        if embeddings.size == 0:
            raise ValueError('No embeddings generated. Ensure the knowledge base is not empty.')

        self.embedding_dim = int(embeddings.shape[1])
        index = faiss.IndexFlatIP(self.embedding_dim)
        index.add(embeddings)
        self.faiss_index = index

        tokenized_corpus = [tokenize_zh(text) for text in texts]
        self.bm25 = BM25Okapi(tokenized_corpus)

        self._save()
        return {
            'chunk_count': len(chunks),
            'embedding_dimension': self.embedding_dim,
            'storage_dir': str(self.storage_dir),
        }

    def _save(self) -> None:
        if self.faiss_index is None or self.bm25 is None:
            raise RuntimeError('Index not built yet.')

        dump_json(str(self.chunks_path), [chunk.to_dict() for chunk in self.chunks])
        dump_json(
            str(self.meta_path),
            {
                'chunk_count': len(self.chunks),
                'embedding_dim': self.embedding_dim,
            },
        )
        faiss.write_index(self.faiss_index, str(self.faiss_path))
        with open(self.bm25_path, 'wb') as f:
            pickle.dump(self.bm25, f)

    def load(self) -> None:
        if not self.meta_path.exists() or not self.faiss_path.exists() or not self.bm25_path.exists() or not self.chunks_path.exists():
            raise FileNotFoundError('Stored index files are incomplete or missing.')

        meta = load_json(str(self.meta_path))
        self.embedding_dim = int(meta['embedding_dim'])
        raw_chunks = load_json(str(self.chunks_path))
        self.chunks = [Chunk(**item) for item in raw_chunks]
        self.faiss_index = faiss.read_index(str(self.faiss_path))
        with open(self.bm25_path, 'rb') as f:
            self.bm25 = pickle.load(f)

    @property
    def ready(self) -> bool:
        return self.faiss_index is not None and self.bm25 is not None and bool(self.chunks)

    def search_dense(self, query: str, top_k: int) -> List[Tuple[int, float]]:
        if self.faiss_index is None:
            raise RuntimeError('Dense index not loaded.')
        vector = self.encoder.encode([query])
        scores, indices = self.faiss_index.search(vector, top_k)
        result: List[Tuple[int, float]] = []
        for idx, score in zip(indices[0].tolist(), scores[0].tolist()):
            if idx < 0:
                continue
            result.append((idx, float(score)))
        return result

    def search_sparse(self, query: str, top_k: int) -> List[Tuple[int, float]]:
        if self.bm25 is None:
            raise RuntimeError('BM25 index not loaded.')
        scores = self.bm25.get_scores(tokenize_zh(query))
        if len(scores) == 0:
            return []
        top_indices = np.argsort(scores)[::-1][:top_k]
        result: List[Tuple[int, float]] = []
        for idx in top_indices.tolist():
            score = float(scores[idx])
            if score <= 0:
                continue
            result.append((idx, score))
        return result
