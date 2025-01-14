from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Fitholic"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fitholic"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key"  # TODO: Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Frontend URLs
    FRONTEND_URL: str = "app://fitholic.com"  # Mobile app URL
    WEBAPP_URL: str = "https://app.fitholic.com"  # Web application URL
    
    # Environment
    ENVIRONMENT: str = "development"

    # Optional Google API Key for AI features
    GOOGLE_API_KEY: Optional[str] = None
    
    # LLM Configuration
    default_llm_provider: str = "gemini"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""

    DEBUG: bool = True
    
    # LLM Provider Settings
    llm_timeout: int = 30  # seconds
    llm_retry_attempts: int = 3
    llm_cache_enabled: bool = True
    
    @property
    def get_database_url(self) -> str:
        """Get the database URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"

settings = Settings()
