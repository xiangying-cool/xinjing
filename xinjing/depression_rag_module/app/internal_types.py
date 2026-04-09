from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Document:
    doc_id: str
    title: str
    content: str
    category: str = 'general'
    source_name: str = 'local'
    source_url: Optional[str] = None
    source_path: Optional[str] = None
    section: Optional[str] = None
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    content: str
    category: str = 'general'
    source_name: str = 'local'
    source_url: Optional[str] = None
    source_path: Optional[str] = None
    section: Optional[str] = None
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
