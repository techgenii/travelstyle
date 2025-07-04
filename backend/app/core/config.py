from pydantic import BaseSettings, Field
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TravelStyle AI"
    VERSION: str = "1.0.0"
    
    # External API Keys
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_ORG_ID: Optional[str] = Field(None, env="OPENAI_ORG_ID")
    QLOO_API_KEY: str = Field(..., env="QLOO_API_KEY")
    OPENWEATHER_API_KEY: str = Field(..., env="OPENWEATHER_API_KEY")
    EXCHANGE_API_KEY: str = Field(..., env="EXCHANGE_API_KEY")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Redis Cache
    REDIS_URL: str = Field("redis://localhost:6379", env="REDIS_URL")
    
    # JWT Settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # API URLs
    QLOO_BASE_URL: str = "https://api.qloo.com/v1"
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    EXCHANGE_BASE_URL: str = "https://api.exchangerate-api.com/v4/latest"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 