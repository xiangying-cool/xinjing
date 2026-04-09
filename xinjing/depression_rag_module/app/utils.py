from __future__ import annotations

import json
import os
import re
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator

import orjson


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def load_json(path: str) -> Any:
    with open(path, 'rb') as f:
        return orjson.loads(f.read())


def dump_json(path: str, data: Any) -> None:
    with open(path, 'wb') as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2 | orjson.OPT_SERIALIZE_NUMPY))


def read_text(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_text(path: str, text: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def normalize_query(text: str) -> str:
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    return text


def compact_text(text: str) -> str:
    text = text.replace('\u3000', ' ')
    text = re.sub(r'\r\n?', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def safe_filename(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_.-]+', '_', name)


@contextmanager
def timed(bucket: Dict[str, float], name: str) -> Generator[None, None, None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        bucket[name] = round((time.perf_counter() - start) * 1000.0, 3)


def preview(text: str, limit: int = 120) -> str:
    text = compact_text(text)
    return text if len(text) <= limit else text[: limit - 3] + '...'


def json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
