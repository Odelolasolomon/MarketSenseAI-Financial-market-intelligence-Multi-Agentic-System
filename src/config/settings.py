"""
Application Settings and Configuration
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    claude_api_key: str = Field(..., env="CLUDE_API_KEY")
    fred_api_key: str = Field(default="", env="FRED_API_KEY")
    newsapi_key: str = Field(default="", env="NEWSAPI_KEY")
    coingecko_api_key: str = Field(default="", env="COINGECKO_API_KEY")
    binance_api_key: str = Field(default="", env="BINANCE_API_KEY")
    binance_api_secret: str = Field(default="", env="BINANCE_API_SECRET")
    
    # Database
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/multiasset",
        env="DATABASE_URL"
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # ChromaDB
    chroma_persist_directory: str = Field(
        default="./chroma_db",
        env="CHROMA_PERSIST_DIRECTORY"
    )
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=True, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Agent Settings
    max_agent_iterations: int = Field(default=5, env="MAX_AGENT_ITERATIONS")
    agent_temperature: float = Field(default=0.7, env="AGENT_TEMPERATURE")
    llm_model: str = Field(default="gemma2-9b-it", env="LLM_MODEL")
    
    # Model Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Data Collection Settings
    data_update_interval: int = Field(default=3600, env="DATA_UPDATE_INTERVAL")
    cache_ttl: int = Field(default=1800, env="CACHE_TTL")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./src/logs/app.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
