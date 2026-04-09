from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = Field(default='DepressionRAGService', alias='APP_NAME')
    app_host: str = Field(default='0.0.0.0', alias='APP_HOST')
    app_port: int = Field(default=8001, alias='APP_PORT')
    debug: bool = Field(default=True, alias='DEBUG')
    api_prefix: str = Field(default='/v1', alias='API_PREFIX')

    knowledge_dir: str = Field(default='./data/knowledge', alias='KNOWLEDGE_DIR')
    storage_dir: str = Field(default='./storage', alias='STORAGE_DIR')
    auto_rebuild_if_missing: bool = Field(default=True, alias='AUTO_REBUILD_IF_MISSING')

    chunk_size: int = Field(default=420, alias='CHUNK_SIZE')
    chunk_overlap: int = Field(default=80, alias='CHUNK_OVERLAP')
    dense_top_k: int = Field(default=20, alias='DENSE_TOP_K')
    sparse_top_k: int = Field(default=20, alias='SPARSE_TOP_K')
    rerank_candidates: int = Field(default=12, alias='RERANK_CANDIDATES')
    final_top_k: int = Field(default=6, alias='FINAL_TOP_K')
    max_context_chars: int = Field(default=2600, alias='MAX_CONTEXT_CHARS')
    enable_rerank: bool = Field(default=True, alias='ENABLE_RERANK')
    rrf_k: int = Field(default=60, alias='RRF_K')

    embedding_model: str = Field(default='BAAI/bge-small-zh-v1.5', alias='EMBEDDING_MODEL')
    rerank_model: str = Field(default='maidalun1020/bce-reranker-base_v1', alias='RERANK_MODEL')
    embedding_device: str = Field(default='cpu', alias='EMBEDDING_DEVICE')
    rerank_device: str = Field(default='cpu', alias='RERANK_DEVICE')
    embed_batch_size: int = Field(default=32, alias='EMBED_BATCH_SIZE')

    enable_llm_generation: bool = Field(default=False, alias='ENABLE_LLM_GENERATION')
    openai_base_url: str = Field(default='http://localhost:11434/v1', alias='OPENAI_BASE_URL')
    openai_api_key: str = Field(default='ollama', alias='OPENAI_API_KEY')
    openai_model: str = Field(default='qwen2.5:3b', alias='OPENAI_MODEL')
    llm_timeout: int = Field(default=60, alias='LLM_TIMEOUT')
    llm_temperature: float = Field(default=0.2, alias='LLM_TEMPERATURE')
    enable_query_rewrite: bool = Field(default=False, alias='ENABLE_QUERY_REWRITE')
    enable_multi_query: bool = Field(default=False, alias='ENABLE_MULTI_QUERY')

    cors_allow_origins: str = Field(default='*', alias='CORS_ALLOW_ORIGINS')

    @property
    def cors_allow_origin_list(self) -> List[str]:
        value = self.cors_allow_origins.strip()
        if value == '*':
            return ['*']
        return [item.strip() for item in value.split(',') if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
