import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = "sqlite+pysqlite:///:memory:"
    llm_mode: str = "mock"
    milvus_uri: str = ""
    milvus_collection: str = "emka_document_chunks"
    embedding_dimension: int = 1536


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite+pysqlite:///:memory:"),
        llm_mode=os.getenv("LLM_MODE", "mock"),
        milvus_uri=os.getenv("MILVUS_URI", ""),
        milvus_collection=os.getenv("MILVUS_COLLECTION", "emka_document_chunks"),
        embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "1536")),
    )
