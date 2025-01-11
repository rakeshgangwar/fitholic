from typing import Optional
from pydantic_settings import BaseSettings

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
    
    @property
    def get_database_url(self) -> str:
        """Get the database URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

settings = Settings()
