from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "CI/CD Failure Analyzer"
    DATABASE_URL: str = "sqlite+aiosqlite:///./cicd_analyzer.db"
    OPENAI_API_KEY: Optional[str] = None
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_MODEL: str = "gpt-3.5-turbo"
    MAX_CHUNK_SIZE: int = 2000
    TOP_K_SIMILAR: int = 3
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
