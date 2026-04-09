from __future__ import annotations

from typing import List, Sequence, Tuple

from sentence_transformers import CrossEncoder


class CrossEncoderReranker:
    def __init__(self, model_name_or_path: str, device: str = 'cpu', max_length: int = 512) -> None:
        self.model_name_or_path = model_name_or_path
        self.device = device
        self.max_length = max_length
        self._model: CrossEncoder | None = None

    @property
    def model(self) -> CrossEncoder:
        if self._model is None:
            self._model = CrossEncoder(
                self.model_name_or_path,
                device=self.device,
                max_length=self.max_length,
                trust_remote_code=True,
            )
        return self._model

    def score(self, query: str, passages: Sequence[str]) -> List[float]:
        if not passages:
            return []
        pairs: List[Tuple[str, str]] = [(query, passage) for passage in passages]
        scores = self.model.predict(pairs, show_progress_bar=False)
        return [float(s) for s in scores]
