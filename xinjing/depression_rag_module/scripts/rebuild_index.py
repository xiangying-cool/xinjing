from app.config import get_settings
from app.service import RAGService


def main() -> None:
    settings = get_settings()
    service = RAGService(settings)
    result = service.rebuild_index()
    print(result.model_dump_json(indent=2))


if __name__ == '__main__':
    main()
