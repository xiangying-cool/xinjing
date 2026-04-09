from app.config import get_settings
from app.schemas import QueryRequest
from app.service import RAGService


TEST_QUERIES = [
    '我最近总是睡不好，情绪也很低落，我该怎么做？',
    '家人可以怎么陪伴抑郁情绪明显的人？',
    '我觉得活着没意思，有点撑不住了。',
]


def main() -> None:
    settings = get_settings()
    service = RAGService(settings)
    service.startup()

    for query in TEST_QUERIES:
        req = QueryRequest(query=query, debug=True)
        resp = service.retrieve(req, generate_answer=settings.enable_llm_generation)
        print('=' * 80)
        print('Q:', query)
        print('Risk:', resp.risk.model_dump())
        print('Latency:', resp.latency_ms)
        if resp.answer:
            print('Answer:', resp.answer)
        print('Contexts:')
        for ctx in resp.contexts:
            print(f'- [{ctx.category}] {ctx.title} ({ctx.source_name}) score={ctx.score}')


if __name__ == '__main__':
    main()
