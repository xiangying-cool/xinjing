from __future__ import annotations

import re
from typing import List

import jieba


_TOKEN_REGEX = re.compile(r'[A-Za-z0-9_]+')


def tokenize_zh(text: str) -> List[str]:
    text = text.lower().strip()
    if not text:
        return []
    parts = list(jieba.cut_for_search(text))
    tokens: List[str] = []
    for part in parts:
        token = part.strip().lower()
        if not token:
            continue
        if len(token) == 1 and not _TOKEN_REGEX.fullmatch(token):
            continue
        tokens.append(token)
    return tokens
