from __future__ import annotations

import hashlib
import re
from typing import List, Optional

from app.internal_types import Chunk, Document


SENTENCE_SPLIT_REGEX = re.compile(r'(?<=[。！？!?；;])')


def _hash_chunk(doc_id: str, index: int, text: str) -> str:
    raw = f'{doc_id}::{index}::{text[:80]}'.encode('utf-8')
    return hashlib.md5(raw).hexdigest()[:16]


def _split_long_paragraph(paragraph: str, chunk_size: int, overlap: int) -> List[str]:
    sentences = [s.strip() for s in SENTENCE_SPLIT_REGEX.split(paragraph) if s.strip()]
    if not sentences:
        return []

    chunks: List[str] = []
    current = ''
    for sent in sentences:
        if len(current) + len(sent) <= chunk_size:
            current += sent
        else:
            if current:
                chunks.append(current)
            if len(sent) <= chunk_size:
                current = sent
            else:
                # Hard split for very long sentences.
                step = max(1, chunk_size - overlap)
                for start in range(0, len(sent), step):
                    piece = sent[start : start + chunk_size]
                    if piece:
                        chunks.append(piece)
                current = ''
    if current:
        chunks.append(current)
    return chunks


def split_document(doc: Document, chunk_size: int = 420, overlap: int = 80) -> List[Chunk]:
    raw_paragraphs = [p.strip() for p in doc.content.split('\n') if p.strip()]
    paragraphs: List[str] = []
    for paragraph in raw_paragraphs:
        if len(paragraph) <= chunk_size:
            paragraphs.append(paragraph)
        else:
            paragraphs.extend(_split_long_paragraph(paragraph, chunk_size, overlap))

    chunks: List[Chunk] = []
    current = ''
    last_section: Optional[str] = doc.section

    for paragraph in paragraphs:
        if paragraph.startswith('#'):
            last_section = paragraph.lstrip('#').strip()
            continue

        candidate = paragraph if not current else current + '\n' + paragraph
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            idx = len(chunks)
            chunks.append(
                Chunk(
                    chunk_id=_hash_chunk(doc.doc_id, idx, current),
                    doc_id=doc.doc_id,
                    title=doc.title,
                    content=current,
                    category=doc.category,
                    source_name=doc.source_name,
                    source_url=doc.source_url,
                    source_path=doc.source_path,
                    section=last_section,
                    priority=doc.priority,
                    metadata=doc.metadata,
                )
            )
            tail = current[-overlap:] if overlap > 0 else ''
            current = (tail + '\n' + paragraph).strip()
        else:
            current = paragraph

    if current:
        idx = len(chunks)
        chunks.append(
            Chunk(
                chunk_id=_hash_chunk(doc.doc_id, idx, current),
                doc_id=doc.doc_id,
                title=doc.title,
                content=current,
                category=doc.category,
                source_name=doc.source_name,
                source_url=doc.source_url,
                source_path=doc.source_path,
                section=last_section,
                priority=doc.priority,
                metadata=doc.metadata,
            )
        )

    return chunks


def split_documents(documents: List[Document], chunk_size: int = 420, overlap: int = 80) -> List[Chunk]:
    all_chunks: List[Chunk] = []
    for doc in documents:
        all_chunks.extend(split_document(doc, chunk_size=chunk_size, overlap=overlap))
    return all_chunks
