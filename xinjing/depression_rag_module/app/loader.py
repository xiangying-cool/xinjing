from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

import yaml
from pypdf import PdfReader

from app.internal_types import Document
from app.utils import compact_text


SUPPORTED_SUFFIXES = {'.md', '.txt', '.json', '.pdf'}


def _make_doc_id(source_path: str, title: str) -> str:
    raw = f'{source_path}::{title}'.encode('utf-8')
    return hashlib.md5(raw).hexdigest()[:16]


def _parse_frontmatter(text: str) -> Tuple[Dict, str]:
    if not text.startswith('---\n'):
        return {}, text

    try:
        _, rest = text.split('---\n', 1)
        frontmatter_raw, body = rest.split('\n---\n', 1)
        meta = yaml.safe_load(frontmatter_raw) or {}
        return meta, body
    except ValueError:
        return {}, text


def _read_markdown_or_text(path: Path) -> List[Document]:
    text = path.read_text(encoding='utf-8')
    meta, body = _parse_frontmatter(text)
    body = compact_text(body)
    title = meta.get('title') or path.stem
    category = meta.get('category') or path.parent.name
    source_name = meta.get('source_name') or path.parent.name
    source_url = meta.get('source_url')
    section = meta.get('section')
    priority = int(meta.get('priority', 1))
    metadata = {k: v for k, v in meta.items() if k not in {'title', 'category', 'source_name', 'source_url', 'section', 'priority'}}
    return [
        Document(
            doc_id=_make_doc_id(str(path), title),
            title=title,
            content=body,
            category=category,
            source_name=source_name,
            source_url=source_url,
            source_path=str(path),
            section=section,
            priority=priority,
            metadata=metadata,
        )
    ]


def _read_json(path: Path) -> List[Document]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(payload, dict):
        payload = [payload]

    docs: List[Document] = []
    for i, item in enumerate(payload):
        title = item.get('title') or f'{path.stem}_{i}'
        content = compact_text(item.get('content') or item.get('text') or '')
        if not content:
            continue
        category = item.get('category') or path.parent.name
        source_name = item.get('source_name') or path.parent.name
        source_url = item.get('source_url')
        section = item.get('section')
        priority = int(item.get('priority', 1))
        metadata = item.get('metadata', {})
        docs.append(
            Document(
                doc_id=_make_doc_id(f'{path}:{i}', title),
                title=title,
                content=content,
                category=category,
                source_name=source_name,
                source_url=source_url,
                source_path=str(path),
                section=section,
                priority=priority,
                metadata=metadata,
            )
        )
    return docs


def _read_pdf(path: Path) -> List[Document]:
    reader = PdfReader(str(path))
    texts = []
    for page in reader.pages:
        extracted = page.extract_text() or ''
        if extracted.strip():
            texts.append(extracted)
    content = compact_text('\n\n'.join(texts))
    if not content:
        return []
    title = path.stem
    return [
        Document(
            doc_id=_make_doc_id(str(path), title),
            title=title,
            content=content,
            category=path.parent.name,
            source_name=path.parent.name,
            source_path=str(path),
        )
    ]


def load_documents_from_dir(knowledge_dir: str) -> List[Document]:
    base = Path(knowledge_dir)
    if not base.exists():
        raise FileNotFoundError(f'Knowledge dir not found: {knowledge_dir}')

    documents: List[Document] = []
    for path in sorted(base.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        if path.suffix.lower() in {'.md', '.txt'}:
            documents.extend(_read_markdown_or_text(path))
        elif path.suffix.lower() == '.json':
            documents.extend(_read_json(path))
        elif path.suffix.lower() == '.pdf':
            documents.extend(_read_pdf(path))

    documents = [doc for doc in documents if doc.content.strip()]
    return documents
