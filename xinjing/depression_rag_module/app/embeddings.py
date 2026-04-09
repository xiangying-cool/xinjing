from __future__ import annotations

from typing import Iterable, List

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingEncoder:
    def __init__(self, model_name_or_path: str, device: str = 'cpu', batch_size: int = 32) -> None:
        self.model_name_or_path = model_name_or_path
        self.device = device
        self.batch_size = batch_size
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name_or_path, device=self.device)
        return self._model

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        text_list: List[str] = list(texts)
        if not text_list:
            return np.zeros((0, 0), dtype='float32')
        embeddings = self.model.encode(
            text_list,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return embeddings.astype('float32')
