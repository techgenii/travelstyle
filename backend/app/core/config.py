"""
Configuration settings for TravelStyle AI application.
Manages environment variables and application configuration.
"""

import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Get the directory where this config.py file is located
config_dir = os.path.dirname(os.path.abspath(__file__))
# Go up to the backend directory (assuming config.py is in backend/app/core/)
backend_dir = os.path.dirname(os.path.dirname(config_dir))
env_path = os.path.join(backend_dir, ".env")

print(f".env file exists: {os.path.exists(env_path)}")

# Load .env from the backend directory
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TravelStyle AI"
    VERSION: str = "1.0.0"

    # External API Keys
    OPENAI_API_KEY: str = ""
    OPENAI_ORG_ID: str | None = None
    QLOO_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""
    EXCHANGE_API_KEY: str = ""

    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # API URLs
    QLOO_BASE_URL: str = "https://api.qloo.com/v1"
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5/weather"
    EXCHANGE_BASE_URL: str = "https://v6.exchangerate-api.com/v6/"

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic configuration for environment file loading."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()
