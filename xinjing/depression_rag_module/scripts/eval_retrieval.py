from __future__ import annotations

import json
from pathlib import Path

from app.config import get_settings
from app.schemas import QueryRequest
from app.service import RAGService


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    eval_path = base / 'data' / 'eval' / 'queries.json'
    queries = json.loads(eval_path.read_text(encoding='utf-8'))

    settings = get_settings()
    service = RAGService(settings)
    service.startup()

    hit = 0
    total = len(queries)
    total_latency = 0.0

    for item in queries:
        req = QueryRequest(query=item['query'])
        resp = service.retrieve(req)
        total_latency += resp.latency_ms.get('total', 0.0)
        retrieved_titles = {ctx.title for ctx in resp.contexts}
        if item['expected_title'] in retrieved_titles:
            hit += 1
        print(f"Q: {item['query']}")
        print(f"Expected: {item['expected_title']}")
        print('Retrieved:', ', '.join(retrieved_titles))
        print('-' * 60)

    print(json.dumps({
        'hit_rate_at_k': round(hit / total, 4) if total else 0.0,
        'avg_latency_ms': round(total_latency / total, 3) if total else 0.0,
        'total_cases': total,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
