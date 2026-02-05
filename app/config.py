"""Configuration management using pydantic-settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str
    
    # LLM Provider
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-3.5-turbo"
    OPENAI_API_KEY: str = ""
    
    # Embeddings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536
    
    # Chunking
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Vector Search
    VECTOR_INDEX_TYPE: str = "hnsw"
    SIMILARITY_METRIC: str = "cosine"
    
    # Application
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
