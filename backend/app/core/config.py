"""
Configuration settings for TravelStyle AI application.
Manages environment variables and application configuration.
"""
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

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

    # Supabase Configuration
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")

    # API URLs
    QLOO_BASE_URL: str = "https://api.qloo.com/v1"
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5/weather"
    EXCHANGE_BASE_URL: str = " https://v6.exchangerate-api.com/v6/"

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic configuration for environment file loading."""

        env_file = ".env"
        case_sensitive = True

settings = Settings()
